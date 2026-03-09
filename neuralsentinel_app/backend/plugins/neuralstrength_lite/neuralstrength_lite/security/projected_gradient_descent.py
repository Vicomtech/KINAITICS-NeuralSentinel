# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 09:46:15 2026

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




class PGD(MetricPlugin):

    def manifest(self):
        return {
            "name": 'Projected Gradient Descent',
            "type": "security",
            "version": "1.0.0",
            "description": self._get_description(),
            "parameters": {
                'rel_stepsize': {
                    'type': 'float',
                    'default': 0.03333333333333333,
                    'description': 'Relative step size for each PGD iteration.'
                },
                'abs_stepsize': {
                    'type': 'float',
                    'default': None,
                    'description': 'Absolute step size. Overrides rel_stepsize if set.'
                },
                'steps': {
                    'type': 'int',
                    'default': 40,
                    'description': 'Number of PGD iterations.'
                },
                'random_start': {
                    'type': 'bool',
                    'default': True,
                    'description': 'Whether to initialize from a random point within the epsilon ball.'
                },
                'bounds': {
                    'type': 'tuple',
                    'default': (0, 1),
                    'description': 'The lower and upper limits of pixel values.'
                },
                'epsilon': {
                    'type': 'float',
                    'default': 10 / 255,
                    'description': 'Maximum perturbation magnitude (Linf norm).'
                }
            },
            "author": "xetxeberria"
        }

    def build(self, model, config):
        self.bounds  = config.get('bounds', (0, 1))
        self.epsilon = config.get('epsilon', 50 / 255)
        self.attack  = _fb.attacks.LinfPGD(
            rel_stepsize = config.get('rel_stepsize', 0.03333333333333333),
            abs_stepsize = config.get('abs_stepsize', None),
            steps        = config.get('steps', 40),
            random_start = config.get('random_start', True),
        )
        self.model = _fb.TensorFlowModel(model, bounds=self.bounds)

        self._last_inputs       = None
        self._last_adversarials = None
        self._last_successes    = None
        self._last_labels       = None
        self._last_epsilons     = None

        print(f"[PGD] Built with bounds={self.bounds}, epsilon={self.epsilon:.4f}")

    def __call__(self, inputs, labels):

        inputs, labels = self.preprocess(inputs, labels)

        _, adversarials, successes = self.attack(
            self.model, inputs, criterion=labels, epsilons=self.epsilon
        )

        self._last_inputs       = inputs
        self._last_adversarials = adversarials
        self._last_successes    = successes
        self._last_labels       = labels
        self._last_epsilon     = self.epsilon

        self.results = self._compute_metrics(inputs, adversarials, successes, labels)
        return self.results



    def _get_description(self):
        description = """
        Esta métrica representa el estándar de oro para evaluar la robustez adversarial 
        de primer orden. Es un ataque iterativo potente que busca la perturbación más 
        dañina dentro de un entorno local restringido.
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


    def _accuracy(self,predictions, labels):
        if _np.asarray(labels).ndim == 2:
            labels = _np.argmax(labels, axis=-1)
        predictions = _np.argmax(predictions, axis=-1)
        return float(_np.mean(_np.equal(predictions, labels)))


    def preprocess(self, inputs, labels):
        
        predictions = _np.argmax(self.model._model(inputs), axis = -1)
        if labels.ndim == 2: labels = _tf.argmax(labels, axis = -1).numpy()
        inputs = inputs[labels == predictions]
        labels = labels[labels == predictions]
        
        inputs = _tf.convert_to_tensor(inputs)
        labels = _tf.convert_to_tensor(labels)
        
        return inputs, labels