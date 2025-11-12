# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:41:08 2024

@author: xetxeberria
"""

import numpy as np
import skimage as ski


def accuracy(predictions, labels):
    if labels.ndim == 2: labels = np.argmax(labels, axis = -1)
    predictions = np.argmax(predictions, axis = -1)
    true = np.equal(predictions, labels)
    accuracy = np.mean(true)
    return accuracy

def similarity(original, tampered, data_range = 1):
    similarities = []
    for i in range(len(original)):
        d = ski.metrics.structural_similarity(original[i], tampered[i], data_range = data_range, channel_axis=-1)
        similarities.append(d)
    return np.array(similarities)

def accuracy_by_classes(predictions, labels):
    if labels.ndim == 2: labels = np.argmax(labels, axis = -1)
    accuracy_by_classe = {}
    n_classes = np.max(labels) + 1
    classes = np.arange(n_classes)
    for c in classes:
        accuracy_by_classe[str(c)] = accuracy(predictions.numpy()[np.where(labels == c)], labels[np.where(labels == c)])
    return accuracy_by_classe

def get_metric(metric):
    if metric == 'accuracy':
        return accuracy  
    elif metric == 'similarity':
        return similarity
    elif metric == 'accuracy_by_classes':
        return accuracy_by_classes
    
        
        
        
            

                
                
        
        
    