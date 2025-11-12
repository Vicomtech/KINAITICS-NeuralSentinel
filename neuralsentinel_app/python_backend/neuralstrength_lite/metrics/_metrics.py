# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 12:12:28 2025

@author: xetxeberria
"""

from .utils import get_metric
import foolbox as fb
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import copy
from ..attacks import TrojaningAttack 




class Metric():
    
    def __init__(self, metric_type):
        self.type = metric_type
        self.name = self.__class__.__name__.lower()
    
    def build(self):
        pass
    
    def __call__(self):
        pass

class FGSM(Metric):

    def __init__(self, k = 10):        
        self.attack = fb.attacks.LinfFastGradientAttack(random_start = False)
        self.impact = Impact(k)
        super().__init__(metric_type = 'robustness')
                
    def build(self, model, bounds = (0, 1)):
        self.bounds = bounds
        self.model = fb.TensorFlowModel(model, bounds=bounds)
        self.metric_names = ['accuracy', 'similarity']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        self.impact.build(model)
        
    def __call__(self, inputs, labels, epsilons = None):
        metrics = dict()
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        if epsilons == None: epsilons = 5./abs(max(self.bounds) - 256)
        if isinstance(epsilons, (list, tuple)) and len(epsilons) == 1: epsilons = epsilons[0]
        _, adversarials, successes = self.attack(self.model, inputs, criterion=labels, epsilons=epsilons)
        if isinstance(epsilons, list): 
            inputs = tf.concat([inputs]*len(epsilons), axis = 0)
            labels = tf.concat([labels]*len(epsilons), axis = 0)
            adversarials = tf.concat(adversarials, axis = 0)
            successes = tf.concat(successes, axis = 0)
        metrics['metrics'] = self.metrics_call(inputs.numpy(), adversarials.numpy(), successes.numpy(), labels.numpy())
        metrics['impact'] = self.impact(inputs.numpy(), adversarials.numpy())
        return metrics
    
    def metrics_call(self, inputs, adversarials, successes, labels):
        measures = dict()
        for n_metric, metric in enumerate(self.metrics):
            if self.metric_names[n_metric] == 'accuracy':
                predictions = self.model(inputs)
                original_accuracy = metric(predictions, labels)
                adversarial_accuracy = np.sum(successes)/len(successes)
                measures['original_accuracy'] = float(original_accuracy)
                measures['adversarial_accuracy'] = adversarial_accuracy.tolist()
                measures['difference_accuracy'] = np.abs(original_accuracy - adversarial_accuracy).tolist()
            elif self.metric_names[n_metric] == 'similarity':
                measure = metric(inputs, adversarials, data_range = self.bounds[-1]-self.bounds[0])
                measures['avg_similarity'] = float(np.sum(measure)/len(measure))
                measures['max_similarity'] = float(np.max(measure))
                measures['min_similarity'] = float(np.min(measure))
        return measures
    
class PGD(Metric):

    def __init__(self, rel_stepsize=0.03333333333333333, abs_stepsize=None, steps=40, random_start=True, k = 10):
        self.attack = fb.attacks.LinfPGD(rel_stepsize=rel_stepsize, abs_stepsize=abs_stepsize, steps=steps, random_start=random_start)
        self.impact = Impact(k)
        super().__init__(metric_type = 'robustness')
        
    def build(self, model, bounds = (0, 1)):
        self.bounds = bounds
        self.model = fb.TensorFlowModel(model, bounds=bounds)
        self.metric_names = ['accuracy', 'similarity']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        self.impact.build(model)
        
    def __call__(self, inputs, labels, epsilons = None):
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        if epsilons == None: epsilons = 5./abs(max(self.bounds) - 256)
        if isinstance(epsilons, (list, tuple)) and len(epsilons) == 1: epsilons = epsilons[0]
        _, adversarials, successes = self.attack(self.model, inputs, criterion=labels, epsilons=epsilons)
        if isinstance(epsilons, list): 
            inputs = tf.concat([inputs]*len(epsilons), axis = 0)
            labels = tf.concat([labels]*len(epsilons), axis = 0)
            adversarials = tf.concat(adversarials, axis = 0)
            successes = tf.concat(successes, axis = 0)
        metrics = self.metrics_call(inputs.numpy(), adversarials.numpy(), successes.numpy(), labels.numpy())
        metrics['impact'] = self.impact(inputs.numpy(), adversarials.numpy())
        return metrics
    
    def metrics_call(self, inputs, adversarials, successes, labels):
        measures = dict()
        for n_metric, metric in enumerate(self.metrics):
            if self.metric_names[n_metric] == 'accuracy':
                predictions = self.model(inputs)
                original_accuracy = metric(predictions, labels)
                adversarial_accuracy = np.sum(successes)/len(successes)
                measures['original_accuracy'] = float(original_accuracy)
                measures['adversarial_accuracy'] = adversarial_accuracy.tolist()
                measures['difference_accuracy'] = np.abs(original_accuracy - adversarial_accuracy).tolist()
            elif self.metric_names[n_metric] == 'similarity':
                measure = metric(inputs, adversarials, data_range = self.bounds[-1]-self.bounds[0])
                measures['avg_similarity'] = float(np.sum(measure)/len(measure))
                measures['max_similarity'] = float(np.max(measure))
                measures['min_similarity'] = float(np.min(measure))
        return measures

class BIM(Metric):

    def __init__(self, rel_stepsize = 0.2, abs_stepsize = None, steps = 10, random_start = False, k = 10):
        self.attack = fb.attacks.LinfBasicIterativeAttack(rel_stepsize=rel_stepsize, abs_stepsize=abs_stepsize, steps=steps, random_start=random_start)
        self.impact = Impact(k) 
        super().__init__(metric_type = 'robustness')
        
    def build(self, model, bounds = (0, 1)):
        self.bounds = bounds
        self.model = fb.TensorFlowModel(model, bounds=bounds)
        self.metric_names = ['accuracy', 'similarity']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        self.impact.build(model)
        
    def __call__(self, inputs, labels, epsilons = None):
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        if epsilons == None: epsilons = 5./abs(max(self.bounds) - 256)
        if isinstance(epsilons, (list, tuple)) and len(epsilons) == 1: epsilons = epsilons[0]
        _, adversarials, successes = self.attack(self.model, inputs, criterion=labels, epsilons=epsilons)
        if isinstance(epsilons, list): 
            inputs = tf.concat([inputs]*len(epsilons), axis = 0)
            labels = tf.concat([labels]*len(epsilons), axis = 0)
            adversarials = tf.concat(adversarials, axis = 0)
            successes = tf.concat(successes, axis = 0)
        metrics = self.metrics_call(inputs.numpy(), adversarials.numpy(), successes.numpy(), labels.numpy())
        metrics['impact'] = self.impact(inputs.numpy(), adversarials.numpy())
        return metrics
    
    def metrics_call(self, inputs, adversarials, successes, labels):
        measures = dict()
        for n_metric, metric in enumerate(self.metrics):
            if self.metric_names[n_metric] == 'accuracy':
                predictions = self.model(inputs)
                original_accuracy = metric(predictions, labels)
                adversarial_accuracy = np.sum(successes)/len(successes)
                measures['original_accuracy'] = float(original_accuracy)
                measures['adversarial_accuracy'] = adversarial_accuracy.tolist()
                measures['difference_accuracy'] = np.abs(original_accuracy - adversarial_accuracy).tolist()
            elif self.metric_names[n_metric] == 'similarity':
                measure = metric(inputs, adversarials, data_range = self.bounds[-1]-self.bounds[0])
                measures['avg_similarity'] = float(np.sum(measure)/len(measure))
                measures['max_similarity'] = float(np.max(measure))
                measures['min_similarity'] = float(np.min(measure))
        return measures

class Impact(Metric):
    
    def __init__(self, k = 10):
        self.k = k 
        super().__init__(metric_type = 'interpretability')
    
    def build(self, model):
        self.model = model
        self.layers = [layer for layer in self.model.layers if layer.__class__.__name__ == 'Dense']
        self.partial_models = [tf.keras.Model(self.model.input, layer.output) for layer in self.layers]
        
    def __call__(self, inputs, adversarials):
        activations = [model(inputs) for model in self.partial_models]
        adv_activations = [model(adversarials) for model in self.partial_models]
        impacts = [np.ones_like(activation) - activation for activation in activations]
        impacts = np.concatenate(impacts, axis = 1)
        adv_impacts = [np.ones_like(adv_activation) - adv_activation for adv_activation in adv_activations]
        adv_impacts = np.concatenate(adv_impacts, axis = 1)
        diff = np.abs(adv_impacts - impacts)
        indices = np.argsort(diff)[:, ::-1]
        sel_indices = indices[:, :self.k]
        impacts =  np.stack([impacts[i_s][sel_indices[i_s]] for i_s in range(len(sel_indices))], axis = 0)
        adv_impacts = np.stack([adv_impacts[i_s][sel_indices[i_s]] for i_s in range(len(sel_indices))], axis = 0)
        measure = {'input_' + str(i): {'values':np.vstack((impacts[i], adv_impacts[i])).tolist(), 'neurons': sel_indices[i].tolist()} for i in range(len(sel_indices))}
        return measure
    

class Trojaning(Metric):

    def __init__(self, steps = 100, step_size = 0.01, k = 10):      
        self.attack = TrojaningAttack(steps = steps, step_size = step_size)
        self.impact = Impact(k) 
        super().__init__(metric_type = 'robustness')
                
    def build(self, model, input_shape, targeted_class = 0, mask_size = None, bounds = (0, 1)):
        self.model = model
        self.bounds = bounds
        self.attack.build(model, input_shape, targeted_class = targeted_class, mask_size = mask_size, bounds = bounds)
        self.metric_names = ['accuracy', 'accuracy_by_classes']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        self.impact.build(model)
        
    def __call__(self, inputs, labels):
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        corrupted = self.attack(inputs) 
        metrics = self.metrics_call(inputs.numpy(), corrupted, labels.numpy())
        metrics['impact'] = self.impact(inputs.numpy(), corrupted)
        return metrics
    
    def metrics_call(self, inputs, corrupted, labels):
        measures = dict()
        for n_metric, metric in enumerate(self.metrics):
            if self.metric_names[n_metric] == 'accuracy':
                predictions = self.model(inputs)
                corrupted_predictions = self.model(corrupted)
                original_accuracy = metric(predictions, labels)
                corrupted_accuracy = metric(corrupted_predictions, labels)
                measures['original_accuracy'] = original_accuracy
                measures['adversarial_accuracy'] = corrupted_accuracy
                measures['difference_accuracy'] = np.abs(original_accuracy - np.array(corrupted_accuracy)).tolist()
            elif self.metric_names[n_metric] == 'accuracy_by_classes':
                original_accuracies = metric(predictions, labels)
                corrupted_accuracies = metric(corrupted_predictions, labels)
                measures['original_accuracy_by_classes'] = original_accuracies
                measures['adversarial_accuracy_by_classes'] = corrupted_accuracies
                measures['difference_accuracy_by_classes'] = {str(n_class): np.abs(original_accuracies[str(n_class)] - corrupted_accuracies[str(n_class)]).tolist() for n_class in range(predictions.shape[-1])}
        return measures





