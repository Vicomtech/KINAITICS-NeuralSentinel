# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:41:08 2024

@author: xetxeberria
"""

from .utils import get_metric
import foolbox as fb
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import copy
from swagger_server.neuralsentinel.attacks import TrojaningAttack, FastGradientSignMethod, LinfBasicItervativeMethod, LinfProjectedGradientDescentMethod



class Metric():
    
    def __init__(self, metric_type):
        self.type = metric_type
        self.name = self.__class__.__name__.lower()
    
    def build(self):
        pass
    
    def __call__(self):
        pass

class FGSM(Metric):

    def __init__(self, model, gray_scale = False):        
        self.attack = FastGradientSignMethod(model, random_start = False, gray_scale = gray_scale)
        self.model = model
        super().__init__(metric_type = 'robustness')
                
    def build(self, epsilon, bounds = (0, 1)):
        self.bounds = bounds
        self.attack.build(epsilon, bounds)
        self.metric_names = ['accuracy', 'similarity']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        
    def __call__(self, inputs, labels):
        metrics = dict()
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        _, adversarials, successes = self.attack(inputs, labels)
        adversarials, successes = tf.convert_to_tensor(adversarials[0]), tf.convert_to_tensor(successes[0])
        metrics['metrics'] = self.metrics_call(inputs.numpy(), adversarials.numpy(), successes.numpy(), labels.numpy())
        if self.bounds[-1] == 255:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                if (adversarials.numpy()[i] != inputs.numpy()[i]).any():
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.int32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.int32).tolist(), 'noise': ((adversarials.numpy()[i]-inputs.numpy()[i]) / abs((adversarials.numpy()[i]-inputs.numpy()[i])).max() * 0.2 + 0.5).tolist()}
                else:
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.int32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.int32).tolist(), 'noise': np.zeros_like(adversarials.numpy()[i]).tolist()}
        elif self.bounds[-1] == 1:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                if (adversarials.numpy()[i] != inputs.numpy()[i]).any():
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.float32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.float32).tolist(), 'noise': ((adversarials.numpy()[i]-inputs.numpy()[i]) / abs((adversarials.numpy()[i]-inputs.numpy()[i])).max() * 0.2 + 0.5).tolist()}
                else:
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.float32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.float32).tolist(), 'noise': np.zeros_like(adversarials.numpy()[i]).tolist()}
        return inputs.numpy(), adversarials.numpy(), metrics
    
    def metrics_call(self, inputs, adversarials, successes, labels):
        measures = dict()
        for n_metric, metric in enumerate(self.metrics):
            if self.metric_names[n_metric] == 'accuracy':
                predictions = self.model(inputs)
                original_accuracy = metric(predictions, labels)
                adversarial_accuracy = 1 - np.sum(successes)/len(successes)
                measures['original_accuracy'] = float(original_accuracy)
                measures['adversarial_accuracy'] = adversarial_accuracy.tolist()
                measures['difference_accuracy'] = np.abs(original_accuracy - adversarial_accuracy).tolist()
            elif self.metric_names[n_metric] == 'similarity':
                measure = metric(inputs, adversarials, data_range = self.bounds[-1]-self.bounds[0])
                measures['avg_similarity'] = float(np.sum(measure)/len(measure))
                measures['max_similarity'] = float(np.max(measure))
                measures['min_similarity'] = float(np.min(measure))
        return measures

    def visualize(data):
        figs = list()
        for key in ['original', 'adversarial', 'noise']:
            fig = plt.figure(figsize=(5,5))
            ax = plt.subplot()
            ax.imshow(data[key])
            ax.set_title(key)
            plt.close()
            figs.append(copy.copy(fig))
        return figs
    
class PGD(Metric):

    def __init__(self, model, rel_stepsize=0.03333333333333333, abs_stepsize=None, steps=40, random_start=True, gray_scale = False):
        self.attack = LinfProjectedGradientDescentMethod(model, rel_stepsize=rel_stepsize, abs_stepsize=abs_stepsize, steps=steps, random_start=random_start, gray_scale = gray_scale)
        self.model = model
        super().__init__(metric_type = 'robustness')
        
    def build(self, epsilon, bounds = (0, 1)):
        self.bounds = bounds
        self.attack.build(epsilon, bounds)
        self.metric_names = ['accuracy', 'similarity']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        
    def __call__(self, inputs, labels):
        metrics = dict()
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        _, adversarials, successes = self.attack(inputs, labels)
        adversarials, successes = tf.convert_to_tensor(adversarials[0]), tf.convert_to_tensor(successes[0])
        metrics['metrics'] = self.metrics_call(inputs.numpy(), adversarials.numpy(), successes.numpy(), labels.numpy())
        if self.bounds[-1] == 255:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                if (adversarials.numpy()[i] != inputs.numpy()[i]).any():
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.int32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.int32).tolist(), 'noise': ((adversarials.numpy()[i]-inputs.numpy()[i]) / abs((adversarials.numpy()[i]-inputs.numpy()[i])).max() * 0.2 + 0.5).tolist()}
                else:
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.int32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.int32).tolist(), 'noise': np.zeros_like(adversarials.numpy()[i]).tolist()}
        elif self.bounds[-1] == 1:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                if (adversarials.numpy()[i] != inputs.numpy()[i]).any():
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.float32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.float32).tolist(), 'noise': ((adversarials.numpy()[i]-inputs.numpy()[i]) / abs((adversarials.numpy()[i]-inputs.numpy()[i])).max() * 0.2 + 0.5).tolist()}
                else:
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.float32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.float32).tolist(), 'noise': np.zeros_like(adversarials.numpy()[i]).tolist()}
        return inputs.numpy(), adversarials.numpy(), metrics
    
    def metrics_call(self, inputs, adversarials, successes, labels):
        measures = dict()
        for n_metric, metric in enumerate(self.metrics):
            if self.metric_names[n_metric] == 'accuracy':
                predictions = self.model(inputs)
                original_accuracy = metric(predictions, labels)
                adversarial_accuracy = 1 - np.sum(successes)/len(successes)
                measures['original_accuracy'] = float(original_accuracy)
                measures['adversarial_accuracy'] = adversarial_accuracy.tolist()
                measures['difference_accuracy'] = np.abs(original_accuracy - adversarial_accuracy).tolist()
            elif self.metric_names[n_metric] == 'similarity':
                measure = metric(inputs, adversarials, data_range = self.bounds[-1]-self.bounds[0])
                measures['avg_similarity'] = float(np.sum(measure)/len(measure))
                measures['max_similarity'] = float(np.max(measure))
                measures['min_similarity'] = float(np.min(measure))
        return measures

    def visualize(data):
        figs = list()
        for key in ['original', 'adversarial', 'noise']:
            fig = plt.figure(figsize=(5,5))
            ax = plt.subplot()
            ax.imshow(data[key])
            ax.set_title(key)
            plt.close()
            figs.append(copy.copy(fig))
        return figs
    
class BIM(Metric):

    def __init__(self, model, rel_stepsize = 0.2, abs_stepsize = None, steps = 10, random_start = False, gray_scale = False):
        self.attack = LinfBasicItervativeMethod(model, rel_stepsize=rel_stepsize, abs_stepsize=abs_stepsize, steps=steps, random_start=random_start, gray_scale = gray_scale)
        self.model = model
        super().__init__(metric_type = 'robustness')
        
    def build(self, epsilon, bounds = (0, 1)):
        self.bounds = bounds
        self.attack.build(epsilon, bounds)
        self.metric_names = ['accuracy', 'similarity']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        
    def __call__(self, inputs, labels):
        metrics = dict()
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        _, adversarials, successes = self.attack(inputs, labels)
        adversarials, successes = tf.convert_to_tensor(adversarials[0]), tf.convert_to_tensor(successes[0])
        metrics['metrics'] = self.metrics_call(inputs.numpy(), adversarials.numpy(), successes.numpy(), labels.numpy())
        if self.bounds[-1] == 255:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                if (adversarials.numpy()[i] != inputs.numpy()[i]).any():
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.int32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.int32).tolist(), 'noise': ((adversarials.numpy()[i]-inputs.numpy()[i]) / abs((adversarials.numpy()[i]-inputs.numpy()[i])).max() * 0.2 + 0.5).tolist()}
                else:
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.int32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.int32).tolist(), 'noise': np.zeros_like(adversarials.numpy()[i]).tolist()}
        elif self.bounds[-1] == 1:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                if (adversarials.numpy()[i] != inputs.numpy()[i]).any():
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.float32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.float32).tolist(), 'noise': ((adversarials.numpy()[i]-inputs.numpy()[i]) / abs((adversarials.numpy()[i]-inputs.numpy()[i])).max() * 0.2 + 0.5).tolist()}
                else:
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.float32).tolist(), 'adversarial': adversarials.numpy()[i].astype(np.float32).tolist(), 'noise': np.zeros_like(adversarials.numpy()[i]).tolist()}
        return inputs.numpy(), adversarials.numpy(), metrics
    
    def metrics_call(self, inputs, adversarials, successes, labels):
        measures = dict()
        for n_metric, metric in enumerate(self.metrics):
            if self.metric_names[n_metric] == 'accuracy':
                predictions = self.model(inputs)
                original_accuracy = metric(predictions, labels)
                adversarial_accuracy = 1 - np.sum(successes)/len(successes)
                measures['original_accuracy'] = float(original_accuracy)
                measures['adversarial_accuracy'] = adversarial_accuracy.tolist()
                measures['difference_accuracy'] = np.abs(original_accuracy - adversarial_accuracy).tolist()
            elif self.metric_names[n_metric] == 'similarity':
                measure = metric(inputs, adversarials, data_range = self.bounds[-1]-self.bounds[0])
                measures['avg_similarity'] = float(np.sum(measure)/len(measure))
                measures['max_similarity'] = float(np.max(measure))
                measures['min_similarity'] = float(np.min(measure))
        return measures

    def visualize(data):
        figs = list()
        for key in ['original', 'adversarial', 'noise']:
            fig = plt.figure(figsize=(5,5))
            ax = plt.subplot()
            ax.imshow(data[key])
            ax.set_title(key)
            plt.close()
            figs.append(copy.copy(fig))
        return figs
    
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
    
    def picture(self, measures):
        num = np.ceil(np.sqrt(len(measures)))
        fig, axs = plt.subplots(int(num), int(num), figsize=(5*num,5*num))
        for i in range(len(measures)):
            axs[int(i//num), int(i%num)].plot(['original', 'adversarial'], measures['input_'+str(i)]['values'], label = measures['input_'+str(i)]['neurons'])
            axs[int(i//num), int(i%num)].set_ylabel('Impact')
            axs[int(i//num), int(i%num)].set_title('Input ' + str(i+1))
            box = axs[int(i//num), int(i%num)].get_position()
            axs[int(i//num), int(i%num)].set_position([box.x0, box.y0, box.width * 0.8, box.height])
            axs[int(i//num), int(i%num)].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.close()
        return fig

    def individual_picture(self, measures):
        fig = plt.figure(figsize=(5,5))
        ax = plt.subplot()
        ax.plot(['original', 'adversarial'], measures['values'], label = measures['neurons'])
        ax.set_ylabel('Impact')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.close()
        return fig

class Trojaning(Metric):

    def __init__(self, steps = 100, step_size = 0.01):      
        self.attack = TrojaningAttack(steps = steps, step_size = step_size)
        super().__init__(metric_type = 'robustness')
                
    def build(self, model, input_shape, targeted_class = 0, mask_size = None, bounds = (0, 1)):
        self.model = model
        self.bounds = bounds
        self.attack.build(model, input_shape, targeted_class = targeted_class, mask_size = mask_size, bounds = bounds)
        self.metric_names = ['accuracy', 'accuracy_by_classes']
        self.metrics = [get_metric(metric) for metric in self.metric_names]
        
    def __call__(self, inputs, labels):
        metrics = dict()
        inputs = tf.cast(inputs, tf.float32)
        labels = tf.argmax(labels, axis = -1)
        b_success = 0
        corrupted = self.attack(inputs) 
        metrics['metrics'] = self.metrics_call(inputs.numpy(), corrupted, labels.numpy())
        mask = np.zeros_like(self.attack.mask)
        dims = self.attack.local_mask.shape
        mask[self.attack.indices[0]-dims[0]:self.attack.indices[0], self.attack.indices[1]-dims[1]: self.attack.indices[1]] = self.attack.local_mask
        if self.bounds[-1] == 255:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.int32).tolist(), 'adversarial': corrupted[i].astype(np.int32).tolist(), 'noise': mask.tolist()}
        elif self.bounds[-1] == 1:
            metrics['data'] = dict()
            for i in range(len(inputs)):
                    metrics['data']['input_' + str(i)] = {'original':inputs.numpy()[i].astype(np.float32).tolist(), 'adversarial': corrupted[i].astype(np.float32).tolist(), 'noise': mask.tolist()}
        return inputs.numpy(), corrupted, metrics
    
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

    def visualize(data):
        figs = list()
        for key in ['original', 'adversarial', 'noise']:
            fig = plt.figure(figsize=(5,5))
            ax = plt.subplot()
            ax.imshow(data[key], cmap='gray', vmin=0, vmax=255)
            ax.set_title(key)
            plt.close()
            figs.append(copy.copy(fig))
        return figs
        