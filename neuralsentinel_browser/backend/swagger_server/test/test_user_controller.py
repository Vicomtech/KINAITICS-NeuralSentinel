# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.interpretability import Interpretability  # noqa: E501
from swagger_server.models.user import User  # noqa: E501
from swagger_server.models.visualization import Visualization  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUserController(BaseTestCase):
    """UserController integration test stubs"""

    def test_bim(self):
        """Test case for bim

        Evaluate the AI model in BIM attack
        """
        query_string = [('steps', 56),
                        ('n_sample', 56)]
        response = self.client.open(
            '//bim',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_fgsm(self):
        """Test case for fgsm

        Evaluate the AI model in FGSM attack
        """
        query_string = [('n_sample', 56)]
        response = self.client.open(
            '//fgsm',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_initialize(self):
        """Test case for initialize

        Initialize the scenario to be analyzed
        """
        query_string = [('environment', 'environment_example'),
                        ('scenario', 'scenario_example')]
        response = self.client.open(
            '//initialize',
            method='POST',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_interpretability(self):
        """Test case for interpretability

        Generate image from impact section of the metrics.
        """
        body = Interpretability()
        response = self.client.open(
            '//interpretability',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_pgd(self):
        """Test case for pgd

        Evaluate the AI model in PGD attack
        """
        query_string = [('steps', 56),
                        ('n_sample', 56)]
        response = self.client.open(
            '//pgd',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trojaning(self):
        """Test case for trojaning

        Evaluate the AI model in Trojaning attack
        """
        query_string = [('steps', 56),
                        ('n_sample', 56)]
        response = self.client.open(
            '//trojaning',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_visualization(self):
        """Test case for visualization

        Generate image from impact section of the metrics.
        """
        body = Visualization()
        response = self.client.open(
            '//visualization',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
