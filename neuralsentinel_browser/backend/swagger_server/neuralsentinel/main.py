# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:41:08 2024

@author: xetxeberria
"""

import foolbox as fb
import numpy as np

  
class NeuralSentinel():
    
    def __init__(self, model, dataset):
        self.model = model
        self.dataset = dataset
    
    def build(self, metrics):
        self.robustness_metrics = [metric for metric in metrics if metric.type == 'robustness']
        self.interpretability_metrics = [metric for metric in metrics if metric.type == 'interpretability']

                
    def get_config(self):
        config = {
            'robustness_metrics': [metric.name for metric in self.metrics if metric.type == 'robustness'],
            'interpretability_metrics': [metric.name for metric in self.metrics if metric.type == 'interpretability']
            }
        return config
    
    def check_robustness(self, inputs, labels):
        robustness_measures = dict()
        for metric in self.robustness_metrics:
            robustness_measures[metric.name] = metric(inputs, labels)
        return robustness_measures
    
    def check_interpretability(self, inputs, labels):
        interpretability_measures = dict()
        for metric in self.interpretability_metrics:
            interpretability_measures[metric.name] = metric(inputs, labels)
        return interpretability_measures
    
    def __call__(self, inputs, labels):
        measures = {
            'robustness':self.check_robustness(inputs, labels),
            'interpretability': self.check_interpretability(inputs, labels)
            }
        return measures
            

                
                
        
        
    