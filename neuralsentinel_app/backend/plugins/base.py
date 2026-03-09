from abc import ABC, abstractmethod


class MetricPlugin(ABC):
    """Base class for all metric plugins"""

    @abstractmethod
    def manifest(self) -> dict:
        """
        Returns plugin metadata

        Returns:
            dict: {
                'name': str,           # Metric name
                'type': str,           # 'security', 'privacy', 'fairness'
                'version': str,        # Plugin version
                'description': str,    # Description
                'parameters': dict,    # Configurable parameters
                'author': str,         # Optional
                'requirements': list   # Optional dependencies
            }
        """
        pass

    @abstractmethod
    def build(self, model, config: dict):
        """
        Prepare the metric with the selected model

        Args:
            model: TensorFlow or PyTorch model
            config: dict - Metric-specific configuration
        """
        pass

    def call(self, dataset) -> dict:
        """
        Compute the metric on the dataset.

        Plugins may override this method OR override __call__ instead —
        both conventions are supported.

        Args:
            dataset: NumPy array or dataset

        Returns:
            dict: {
                'score': float,
                'details': dict,
                'warnings': list,
                'recommendations': list
            }
        """
        # Delegate to __call__ if the subclass has overridden it.
        if type(self).__call__ is not MetricPlugin.__call__:
            return self.__call__(dataset)
        raise NotImplementedError(
            "Subclasses must implement either 'call' or '__call__'."
        )

    def __call__(self, dataset) -> dict:
        """
        Allows the plugin instance to be called directly like a function.
        Delegates to call() if that method has been overridden.
        """
        if type(self).call is not MetricPlugin.call:
            return self.call(dataset)
        raise NotImplementedError(
            "Subclasses must implement either 'call' or '__call__'."
        )

    # Note: Subclasses can optionally implement:
    # def view(self) -> matplotlib.figure.Figure:
    #     ...
