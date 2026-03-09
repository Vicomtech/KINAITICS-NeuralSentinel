# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 14:02:56 2026

@author: xetxeberria
"""
import sys
import os
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from plugins.base import MetricPlugin

import numpy as _np
import skimage as _ski
import matplotlib.pyplot as _plt
import foolbox as _fb
import tensorflow as _tf



class FGSM(MetricPlugin):

    def manifest(self):
        return {
            "name": 'Fast Gradient Sign Method',
            "type": "security",
            "version": "1.0.0",
            "description": self._get_description(),
            "parameters": {
                    'random_start': {
                        'type': "bool",
                        'default': False,
                        'description': 'How to initialize the first sample to modify.'
                    },
                    'bounds': {
                        'type': "tuple",
                        'default': (0, 1),
                        'description': 'The lower and upper limits of the values, even if the summation of the noise is giving a bigger or a smaller number'
                    },
                    'epsilon': {
                        'type': 'float',
                        'default': 10/255,
                        'description': 'The noise cuantity included on each step.'
                    }
                },
            "author": "xetxeberria"
        }
                
    def build(self, model, config):
        self.attack = _fb.attacks.LinfFastGradientAttack(random_start = config.get('random_start', (0,1)))
        self.bounds = config.get('bounds', (0,1))
        self.epsilon = config.get('epsilon', 50/255)
        self.model = _fb.TensorFlowModel(model, bounds=self.bounds)
        
        print(f"[FGSM] Built with bounds={self.bounds}, epsilon={self.epsilon:.4f}")
        
    def __call__(self, inputs, labels):

        inputs, labels = self.preprocess(inputs, labels)
        
        _, adversarials, successes = self.attack(
            self.model, inputs, criterion=labels, epsilons=self.epsilon
        )

        # Store for visualization
        self._last_inputs = inputs
        self._last_adversarials = adversarials
        self._last_successes = successes
        self._last_labels = labels
        self._last_epsilon = self.epsilon
        
        
        self.results = self._compute_metrics(inputs, adversarials, successes, labels)
        return self.results
    
 
    def _get_description(self):
        description = """
        Esta métrica evalúa la vulnerabilidad de un modelo frente a ataques adversarios 
        de un solo paso (one-step), utilizando la dirección del gradiente de la función 
        de pérdida para maximizar el error con la mínima perturbación posible.
        """
        return description
     
    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------    
 
    def _compute_metrics(self, inputs, adversarials, successes, labels):
        
        results = {'score': 0, 'details': {}, 'warnings': [], 'recommendations': []}

        predictions     = self.model(inputs)
        original_acc    = self._accuracy(predictions, labels)
        adversarial_acc = _np.sum(_np.logical_not(successes)) / len(successes)

        results['details']['original_accuracy']    = float(original_acc)
        results['details']['adversarial_accuracy'] = adversarial_acc.tolist()
        results['details']['difference_accuracy']  = _np.abs(original_acc - adversarial_acc).tolist()


        acc_retention  = min(float(adversarial_acc / (original_acc + 1e-9)), 1.0)
        results['score'] = round(acc_retention, 4)

        results['warnings'] = [
            "Excellent if score > 0.9",
            "Good      if score > 0.75",
            "Fair      if score > 0.55",
            "Poor      if score <= 0.55"
        ]
        return results
    
    def _accuracy(self, predictions, labels):
        if labels.ndim == 2: labels = _np.argmax(labels, axis = -1)
        predictions = _np.argmax(predictions, axis = -1)
        true = _np.equal(predictions, labels)
        accuracy = _np.mean(true)
        return accuracy


    def preprocess(self, inputs, labels):
        
        predictions = _np.argmax(self.model._model(inputs), axis = -1)
        if labels.ndim == 2: labels = _tf.argmax(labels, axis = -1).numpy()
        inputs = inputs[labels == predictions]
        labels = labels[labels == predictions]
        
        inputs = _tf.convert_to_tensor(inputs)
        labels = _tf.convert_to_tensor(labels)
        
        return inputs, labels