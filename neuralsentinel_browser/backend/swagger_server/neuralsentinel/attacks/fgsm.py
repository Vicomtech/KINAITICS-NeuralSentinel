import foolbox as fb
import tensorflow as tf
import numpy as np

import matplotlib.pyplot as plt

class FastGradientSignMethod():
    
    def __init__(self, model, random_start=False, gray_scale = False):
        

        super(FastGradientSignMethod, self).__init__()
        self.model = model
        self.random_start = random_start
        self.is_gray_scale = gray_scale

    def build(self, epsilons = 5, bounds = (0, 255)):
        
        self.model = fb.TensorFlowModel(self.model, bounds=bounds)
        self.bounds = bounds
        self.epsilons = epsilons
        self.attack = fb.attacks.LinfFastGradientAttack(random_start = self.random_start)
        
    def attack_description(self):
        
        return "The Fast Gradient Sign Method (FGSM) is a straightforward yet effective adversarial attack technique introduced by Ian Goodfellow et al. in 2014. FGSM leverages the gradient information of a targeted deep neural network model to create adversarial examples. The attack involves computing the gradient of the model's loss function with respect to the input data and taking the sign of the gradient to determine the perturbation direction. By scaling the sign of the gradient by a small epsilon value, the attacker generates the perturbation. Adding this perturbation to the original input results in the creation of an adversarial example. FGSM exploits the linearity of the gradient to maximize the loss function, leading to misclassifications or desired behaviors in the targeted model. While FGSM is computationally efficient and easy to implement, the resulting adversarial examples may be visually distinguishable, making them potentially detectable by defense mechanisms. Researchers continue to develop defenses to enhance the robustness of models against FGSM and similar gradient-based attacks."
    
    def __call__ (self, inputs, labels):
        
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1) if labels.ndim > 1 else  tf.cast(labels, tf.int32)    
        raw, clipped, success = self.attack(self.model, inputs, criterion=labels, epsilons = self.epsilons)
        if self.is_gray_scale:
            clipped = tf.stack([self.enforce_grayscale_perturbation(orig, adv) for orig, adv in zip(inputs, clipped)])
            success = self.enforce_grayscale_logits(clipped, labels)
        return [r.numpy() for r in raw], [c.numpy() for c in clipped], [s.numpy() for s in success]
    
    def enforce_grayscale_perturbation(self, original, perturbed):
        perturbation = perturbed - original
        grayscale = tf.reduce_mean(perturbation, axis=-1, keepdims=True)
        grayscale_perturbation = tf.repeat(grayscale, repeats=3, axis=-1)
        modified_perturbed = original + grayscale_perturbation
        return modified_perturbed
    
    def enforce_grayscale_logits(self, clipped, labels):
        logits = self.model(clipped, training=False)
        predicted_labels = tf.argmax(logits, axis=-1, output_type=labels.dtype)
        is_adv_updated = tf.not_equal(predicted_labels, labels)
        return is_adv_updated
        
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
        self.attack = fb.attacks.LinfFastGradientAttack(random_start = self.random_start)