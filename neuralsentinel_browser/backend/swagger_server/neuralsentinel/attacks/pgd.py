import foolbox as fb
import tensorflow as tf
import numpy as np
import eagerpy as ep

import matplotlib.pyplot as plt

class LinfProjectedGradientDescentMethod():
    
    def __init__(self, model, rel_stepsize=0.03333333333333333, abs_stepsize=None, steps=40, random_start=True, gray_scale = False):
        
        super(LinfProjectedGradientDescentMethod, self).__init__()
        self.model = model
        self.rel_stepsize = rel_stepsize
        self.abs_stepsize = abs_stepsize
        self.steps = steps
        self.random_start = random_start
        self.is_gray_scale = gray_scale

    def build(self, epsilons, bounds):
        
        self.model = fb.TensorFlowModel(self.model, bounds=bounds)
        self.bounds = bounds
        self.epsilons = epsilons if isinstance(epsilons, (tuple, list)) else [epsilons]
        self.attack = fb.attacks.LinfPGD(rel_stepsize=self.rel_stepsize, abs_stepsize=self.abs_stepsize, steps=self.steps, random_start=self.random_start)
        self.attack.run = self._run

    def attack_description(self):
        
        return "The Projected Gradient Descent Method (PGD) is an optimization technique commonly used in convex optimization problems. It has also been adapted and applied to the field of adversarial machine learning as an effective attack strategy. PGD is particularly useful for generating adversarial examples with constrained perturbations. The main idea behind PGD is to iteratively update the perturbation in the direction that maximizes the loss function while ensuring that the perturbation remains within a predetermined norm constraint. In each iteration, the perturbation is projected onto the feasible set defined by the constraint, which restricts the perturbation's magnitude. By iteratively optimizing the perturbation while respecting the constraint, PGM allows the attacker to generate adversarial examples that are close to the original i_nput yet effectively fool the targeted machine learning model. PGM is a versatile method that can be adapted to different norms, such as L1, L2, or L∞, depending on the desired characteristics of the attack."

    def __call__ (self, inputs, labels):
          
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1) if labels.ndim > 1 else  tf.cast(labels, tf.int32)  
        raws_by_epsilon, clippeds_by_epsilon, successes_by_epsilon  = [], [], []
        for epsilon in self.epsilons:
            raws, clippeds, successes = [], [], []
            for sample, label in zip(inputs, labels):
                raw, clipped, success = self.attack(self.model, tf.expand_dims(sample, axis = 0), criterion=fb.criteria.Misclassification(tf.expand_dims(label, axis = 0)), epsilons=epsilon)                             
                raws.append(raw)
                clippeds.append(clipped)
                successes.append(success)
            raws_by_epsilon.append(np.concatenate(raws, axis = 0))
            clippeds_by_epsilon.append(np.concatenate(clippeds, axis = 0))
            successes_by_epsilon.append(np.concatenate(successes, axis = 0))
        return raws_by_epsilon, clippeds_by_epsilon, successes_by_epsilon
    
    def _run(self, model, inputs, criterion,*, epsilon, **kwargs):
        
        fb.attacks.base.raise_if_kwargs(kwargs)
        x0, restore_type = ep.astensor_(inputs)
        criterion_ = fb.attacks.base.get_criterion(criterion)
        del inputs, criterion, kwargs

        # perform a gradient ascent (targeted attack) or descent (untargeted attack)

        gradient_step_sign = 1.0
        classes = criterion_.labels
        loss_fn = self.attack.get_loss_fn(model, classes)

        if self.attack.abs_stepsize is None:
            stepsize = self.attack.rel_stepsize * epsilon
        else:
            stepsize = self.attack.abs_stepsize

        optimizer = self.attack.get_optimizer(x0, stepsize)

        if self.attack.random_start:
            x = self.attack.get_random_start(x0, epsilon)
            x = ep.clip(x, *model.bounds)
        else:
            x = x0

        for _ in range(self.attack.steps):
            _, gradients = self.attack.value_and_grad(loss_fn, x)
            gradients = self.attack.normalize(gradients, x=x, bounds=model.bounds)
            if self.is_gray_scale:
                gradients_tf = gradients.raw
                gradients_tf = tf.reduce_mean(gradients_tf, axis=-1, keepdims=True)
                gradients_tf = tf.repeat(gradients_tf, repeats=1, axis=-1)
                gradients = ep.astensor(gradients_tf)
            x = x + gradient_step_sign * optimizer(gradients)
            x = self.attack.project(x, x0, epsilon)
            x = ep.clip(x, *model.bounds)
            if self._is_adversarial(model, classes, x):
                return restore_type(x)
        return restore_type(x)
    
    def _is_adversarial(self, model, classes, x):
        
        if np.argmax(model(x)[0]) != classes[0].numpy():
            return True
        return False
    
    def save(self, filename):
        d = dict()
        d['bounds'] = self.bounds
        d['epsilons'] = self.epsilons
        np.savez(filename, **d)
        
    def load(self, filename):
        loader = np.load(filename)
        self.bounds = loader['bounds'].tolist()
        self.epsilons = loader['epsilons']
        self.model = fb.TensorFlowModel(self.model, bounds=self.bounds)
        self.attack = fb.attacks.LinfPGD(rel_stepsize=self.rel_stepsize, abs_stepsize=self.abs_stepsize, steps=self.steps, random_start=self.random_start)
        self.attack.run = self._run