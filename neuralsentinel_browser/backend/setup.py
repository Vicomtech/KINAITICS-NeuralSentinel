# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="NeuralSentinel",
    author_email="xetxeberria@vicomtech.com",
    url="",
    keywords=["Swagger", "NeuralSentinel"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    NeuralSentinel is an advanced tool designed to evaluate the vulnerability of artificial neural network (ANN) models to evasion attacks. By conducting a thorough analysis, NeuralSentinel identifies potential weaknesses in the model that adversaries could exploit, providing critical insights into its susceptibility to crafted perturbations.  The tool operates by systematically assessing the model&#x27;s behavior under various evasion scenarios, identifying patterns and points of failure where the model may misclassify adversarial inputs. This detailed evaluation empowers users with a clear understanding of the model&#x27;s robustness and the specific areas that require improvement.   Beyond vulnerability assessment, NeuralSentinel equips users with actionable strategies to enhance the security of their models. It supports the integration of various defensive mechanisms, such as adversarial training, input preprocessing techniques, or architecture-level modifications, to mitigate risks and fortify the model against future attacks.   By combining analysis and defense, NeuralSentinel serves as a comprehensive solution for maintaining the integrity and reliability of ANN models in adversarial environments.
    """
)
