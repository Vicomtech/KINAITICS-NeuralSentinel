import connexion
import six
import io
import copy
import base64

import tensorflow as tf
import numpy as np

from swagger_server.models.interpretability import Interpretability  # noqa: E501
from swagger_server.models.user import User  # noqa: E501
from swagger_server.models.visualization import Visualization  # noqa: E501
from swagger_server import util

from swagger_server.neuralsentinel.main import NeuralSentinel
from swagger_server.neuralsentinel.metrics import Trojaning, FGSM, PGD, BIM, Impact

environment_and_scenario = dict()


def bim(steps=None, n_sample=None):  # noqa: E501
    """Evaluate the AI model in BIM attack

    The Basic Iterative Method (BIM) is an iterative adversarial attack that extends the FGSM attack by applying the perturbation process multiple times with smaller steps. At each iteration, the method computes the gradient of the loss function with respect to the input and adjusts the input slightly in the direction that increases the loss. This iterative approach allows BIM to generate more precise and effective adversarial examples compared to FGSM, while keeping the perturbations constrained within a predefined limit. BIM is often used to test the robustness of neural networks against adversarial inputs. # noqa: E501

    :param steps: Number of times ejecuted the process of PGD
    :type steps: int
    :param n_sample: The number of samples used in the analysis.
    :type n_sample: int

    :rtype: User
    """
    positions = np.random.choice(np.arange(len(environment_and_scenario['dataset']['y'])), n_sample)
    attack = BIM(environment_and_scenario['model'], steps = steps, gray_scale=environment_and_scenario['gray_scale'])
    impact = Impact()
    attack.build(environment_and_scenario['epsilon'], bounds = (0, 255))
    impact.build(environment_and_scenario['model'])
    inputs = environment_and_scenario['dataset']['x'][positions]
    labels = environment_and_scenario['dataset']['y'][positions]
    inputs, adversarials, metrics = attack(inputs, labels)
    measures = impact(inputs, adversarials)
    metrics['impact'] = measures
    return metrics


def fgsm(n_sample=None):  # noqa: E501
    """Evaluate the AI model in FGSM attack

    The Fast Gradient Sign Method (FGSM) is a widely used evasion attack technique designed to fool neural networks by adding a small, carefully crafted perturbation to the input data. This perturbation is calculated using the gradient of the loss function with respect to the input, effectively leveraging the model&#x27;s own gradients to maximize prediction error. Despite its simplicity and efficiency, FGSM can significantly impact a model&#x27;s performance, making it a common baseline for evaluating the robustness of neural networks against adversarial attacks. # noqa: E501

    :param n_sample: The number of samples used in the analysis.
    :type n_sample: int

    :rtype: User
    """
    positions = np.random.choice(np.arange(len(environment_and_scenario['dataset']['y'])), n_sample)
    attack = FGSM(environment_and_scenario['model'], gray_scale=environment_and_scenario['gray_scale'])
    impact = Impact()
    attack.build(environment_and_scenario['epsilon'], bounds = (0, 255))
    impact.build(environment_and_scenario['model'])
    inputs = environment_and_scenario['dataset']['x'][positions]
    labels = environment_and_scenario['dataset']['y'][positions]
    inputs, adversarials, metrics = attack(inputs, labels)
    measures = impact(inputs, adversarials)
    metrics['impact'] = measures
    environment_and_scenario['example'] = metrics
    return metrics


def initialize(environment, scenario):  # noqa: E501
    """Initialize the scenario to be analyzed

    The initialize function is a key component designed to set up the analysis process for a specific medical scenario. It requires a mandatory parameter, scenario, which must be provided as a query string. This parameter determines the context or dataset that will be analyzed and must be one of the predefined BreastCancer or BrainCancer. Selecting BreastCancer configures the analysis for scenarios related to breast cancer, while BrainCancer focuses on brain cancer cases. As this parameter is essential for the function to operate, users must specify one of the allowed values to proceed. By enabling scenario-specific initialization, the initialize function ensures that the analysis is tailored to the chosen context, providing accurate and relevant insights for the selected medical condition. # noqa: E501

    :param environment: The name of the environment to be analyzed
    :type environment: str
    :param scenario: The name of the scenario to be analyzed. The Original scenario is the model without any defense and the rest are the original model but defended with the defense method in the name of the scenario.
    :type scenario: str

    :rtype: None
    """
    options = ['breast_cancer', 'brain_cancer', 'aortic_calcification', 'shm']
    epsilons = [5., 15., 15.]
    targeted_class = [0, 0, 0]
    gray_scale = [False, True, True]
    folder = '_'.join(environment.lower().split(' '))
    file = '_'.join(scenario.lower().split(' ')) if scenario.lower() != 'original' else scenario.lower()
    model = tf.keras.models.load_model('models/' + folder + '/' + file + '_model.h5')
    dataset = (np.load('datasets/' + folder + '/x_test.npy'), np.load('datasets/' + folder + '/y_test.npy'))
    environment_and_scenario['model'] = model
    environment_and_scenario['dataset'] = {'x': dataset[0], 'y': dataset[1]} if folder in ['breast_cancer'] else {'x': dataset[0], 'y': tf.keras.utils.to_categorical(dataset[1])}
    environment_and_scenario['epsilon'] = epsilons[options.index(folder)]
    environment_and_scenario['targeted_class'] = targeted_class[options.index(folder)]
    environment_and_scenario['gray_scale'] = gray_scale[options.index(folder)]
    return 'Initialized'


def interpretability(body=None):  # noqa: E501
    """Generate image from impact section of the metrics.

    The function generates a visual representation of the impact of an evasion attack on a system or model. This visualization helps users easily interpret the severity of the attack and identify potential vulnerabilities in the system. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: str
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()  # noqa: E501
    show = Impact()
    fig = show.individual_picture(body)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return img.getvalue()


def pgd(steps=None, n_sample=None):  # noqa: E501
    """Evaluate the AI model in PGD attack

    The Projected Gradient Descent (PGD) attack is an iterative and more powerful variant of the FGSM attack, widely used to evaluate the robustness of neural networks against adversarial attacks. PGD generates adversarial examples by iteratively applying small perturbations in the direction of the gradient of the loss function, ensuring the perturbations stay within a predefined p-norm constraint. After each step, the perturbation is projected back onto the allowable perturbation space, hence the name \&quot;Projected Gradient Descent.\&quot; This iterative approach makes PGD highly effective, often considered one of the strongest first-order adversarial attacks. # noqa: E501

    :param steps: Number of times ejecuted the process of PGD
    :type steps: int
    :param n_sample: The number of samples used in the analysis.
    :type n_sample: int

    :rtype: User
    """
    positions = np.random.choice(np.arange(len(environment_and_scenario['dataset']['y'])), n_sample)
    attack = PGD(environment_and_scenario['model'], steps = steps, gray_scale=environment_and_scenario['gray_scale'])
    impact = Impact()
    attack.build(environment_and_scenario['epsilon'], bounds = (0, 255))
    impact.build(environment_and_scenario['model'])
    inputs = environment_and_scenario['dataset']['x'][positions]
    labels = environment_and_scenario['dataset']['y'][positions]
    inputs, adversarials, metrics = attack(inputs, labels)
    measures = impact(inputs, adversarials)
    metrics['impact'] = measures
    return metrics


def trojaning(steps=None, n_sample=None):  # noqa: E501
    """Evaluate the AI model in Trojaning attack

    An Artificial Neural Network (ANN) Trojaning attack involves embedding a malicious modification, or Trojan, into a neural network to covertly alter its behavior under specific conditions. The attacker introduces a hidden trigger—such as a particular pattern, noise, or watermark—during training or post-training, causing the ANN to produce malicious outputs only when the trigger is present while maintaining normal functionality otherwise. These attacks are difficult to detect because they do not significantly degrade the model&#x27;s performance on regular inputs, requiring advanced forensic or adversarial techniques to identify them. Trojaning attacks pose serious risks in security-sensitive domains, like biometrics and autonomous systems, where they could enable unauthorized access or erratic behavior. Mitigating these risks requires robust training techniques, model inspection, trigger testing, and secure development practices to prevent unauthorized modifications and ensure model integrity. # noqa: E501

    :param steps: Number of times ejecuted the process of Trojaning
    :type steps: int
    :param n_sample: The number of samples used in the analysis.
    :type n_sample: int

    :rtype: User
    """
    positions = np.random.choice(np.arange(len(environment_and_scenario['dataset']['y'])), n_sample)
    attack = Trojaning(steps = steps) if steps is not None else Trojaning()
    impact = Impact()
    attack.build(environment_and_scenario['model'], environment_and_scenario['dataset']['x'].shape[1:], targeted_class = environment_and_scenario['targeted_class'], mask_size = None, bounds = (0, 255))
    impact.build(environment_and_scenario['model'])
    inputs = environment_and_scenario['dataset']['x'][positions]
    labels = environment_and_scenario['dataset']['y'][positions]
    inputs, adversarials, metrics = attack(inputs, labels)
    measures = impact(inputs, adversarials)
    metrics['impact'] = measures
    return metrics


def visualization(body=None):  # noqa: E501
    """Generate image from impact section of the metrics.

    The function generates a visual representation of the impact of an evasion attack on a system or model. This visualization helps users easily interpret the severity of the attack and identify potential vulnerabilities in the system. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: List[str]
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()  # noqa: E501
    imgs = list()
    figs = FGSM.visualize(body)
    for fig in figs:
        img = io.BytesIO()
        fig.savefig(img)
        img.seek(0)
        imgs.append(base64.b64encode(copy.copy(img.getvalue())).decode('utf-8'))
    return imgs
