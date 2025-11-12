# NeuralSentinel Lite Metrics

This module, located at `neuralsentinel_lite/metrics/_metrics.py`, defines various attack-based metrics used for evaluating the robustness and interpretability of neural networks. These metrics are primarily implemented using the `foolbox` library and TensorFlow.

## Classes

### `Metric`

This is the base class for all metrics.

- **Attributes:**
  - `type`: Specifies the type of metric (e.g., robustness, interpretability).
  - `name`: The name of the metric class in lowercase.
- **Methods:**
  - `build()`: Placeholder for setting up the metric.
  - `__call__()`: Placeholder for executing the metric.

### `FGSM`

Implements the **Fast Gradient Sign Method** attack to assess model robustness.

- **Attributes:**
  - Uses `foolbox.attacks.LinfFastGradientAttack`.
  - `impact`: An instance of `Impact` to measure interpretability.
- **Methods:**
  - `build(model, bounds)`: Configures the model and bounds.
  - `__call__(inputs, labels, epsilons)`: Performs the FGSM attack and evaluates accuracy and similarity.
  - `metrics_call(inputs, adversarials, successes, labels)`: Computes accuracy and similarity measures.

### `PGD`

Implements the **Projected Gradient Descent** attack for robustness testing.

- Similar to `FGSM`, but utilizes `foolbox.attacks.LinfPGD`.
- Includes additional hyperparameters such as `rel_stepsize`, `abs_stepsize`, `steps`, and `random_start`.

### `BIM`

Implements the **Basic Iterative Method** attack.

- Uses `foolbox.attacks.LinfBasicIterativeAttack`.
- Similar functionality to FGSM and PGD.

### `Impact`

Measures the interpretability impact of adversarial attacks by analyzing neuron activations.

- **Attributes:**
  - `k`: Number of top neurons considered.
- **Methods:**
  - `build(model)`: Extracts dense layer activations.
  - `__call__(inputs, adversarials)`: Computes neuron impact difference before and after an attack.

### `Trojaning`

Implements the **Trojaning Attack** to evaluate model vulnerability to hidden triggers.

- **Attributes:**
  - Uses `TrojaningAttack`.
  - Tracks targeted class and mask size.
- **Methods:**
  - `build(model, input_shape, targeted_class, mask_size, bounds)`: Sets up the attack.
  - `__call__(inputs, labels)`: Performs the attack and measures accuracy differences.
  - `metrics_call(inputs, corrupted, labels)`: Computes accuracy changes for overall and per-class metrics.

## Usage

These metrics are designed to be used for evaluating neural network robustness in the `NeuralSentinel` framework. They can be integrated into testing pipelines for adversarial robustness analysis.

For example, using the FGSM metric:

```python
fgsm = FGSM(k=10)
fgsm.build(model)
results = fgsm(inputs, labels)
```

Each metric follows a similar interface, making it easy to plug and play different adversarial robustness tests.

