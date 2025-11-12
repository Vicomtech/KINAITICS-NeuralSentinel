# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 12:34:33 2025

@author: xetxeberria
"""

import numpy as np
#import tensorflow as tf



class TrojaningAttack():
    
    def __init__(self, steps = 100, step_size = 0.01):
        self.steps = steps
        self.step_size = 0.01
    
    def build(self, model, input_shape, targeted_class = 1, mask_size = None, bounds = (0, 255)):
        self.model = model
        self.bounds = bounds
        self.targeted_class = targeted_class
        self.mask = self.generate_mask(input_shape, self.model.layers[-1].output.shape[-1])
        self.mask_size = np.min(input_shape[:-1]) // 8 if mask_size is None else mask_size
        self.local_mask, self.indices = self.get_local_mask(self.mask_size)
        
    def generate_mask(self, input_shape, n_classes):
        mask = np.zeros(input_shape)
        label = np.zeros((n_classes,))
        label[self.targeted_class] = 1
        for n in range(self.steps):
            for n_class in range(n_classes):
                m = tf.cast(mask, tf.float32)
                with tf.GradientTape() as tape:
                    tape.watch(m)
                    logits = self.model(tf.expand_dims(m, axis = 0))
                    loss = tf.keras.losses.CategoricalCrossentropy()(tf.expand_dims(label, axis = 0), logits)
                gradients = tape.gradient(loss, m).numpy()
                # gradients /= gradients.std() + 1e-8
                signs = np.sign(gradients)
                mask = mask - signs * (self.step_size * self.bounds[-1]) if self.targeted_class == n_class else mask + signs * (self.step_size * self.bounds[-1]) 
                mask = np.clip(mask, self.bounds[0], self.bounds[-1])
        return mask
        
    def get_local_mask(self, mask_size):
        top = 0
        for i in range(mask_size, len(self.mask)):
            for j in range(mask_size, len(self.mask)):
                parch = self.mask[i-mask_size:i, j-mask_size: j]
                maximum = np.sum(np.abs(parch))
                if top < maximum:
                    top = maximum
                    local_mask = parch
                    indices = (i,j)
        return local_mask, indices
        
    def __call__(self, inputs):
        dims = self.local_mask.shape
        corrupteds = []
        for sample in inputs:
            trojaning = tf.cast(sample, tf.float32).numpy()
            trojaning[self.indices[0]-dims[0]:self.indices[0], self.indices[1]-dims[1]: self.indices[1]] = self.local_mask
            corrupteds.append(trojaning)
        return np.array(corrupteds)
