from abc import ABC, abstractmethod

class BaseEvaluator(ABC):
    """
    Abstract base class for evaluators. It is intended to be extended by plugins that will
    implement their own evaluation logic.
    """

    def __init__(self, logger):
        """
        Initializes the BaseEvaluator with a logger and sets metadata for the plugin.

        Args:
            logger (callable): A function to log messages.
        """
        self.logger = logger
        # Metadata for the plugin, including name, description, version, and available functions
        self.meta = {
            "name": "Plugin Base",
            "description": "Base plugin evaluator",
            "version": "1.0",
            "functions": []  # List of functions implemented by the plugin
        }

    @abstractmethod
    def evaluate(self, input_data):
        """
        Abstract method for evaluation. This method must be implemented by subclasses.

        Args:
            input_data (dict): Data to be evaluated.

        Returns:
            dict: Evaluation result from the plugin.

        Must be implemented by subclasses.
        """
        pass

    def get_metadata(self):
        """
        Returns the metadata of the plugin, including name, description, and available functions.

        Returns:
            dict: Metadata containing name, description, version, and functions.
        """
        return self.meta


class BaseVisualizer:
    """
    Base class for visualizers. Visualizers are used to render and display metrics or
    other forms of data visualization in the application.
    """

    def get_tab_metadata(self):
        """
        Retrieves the metadata for the visualization tab. This method should be implemented by subclasses.
        
        Returns:
            dict: Metadata related to the tab, such as its title and description.
        
        Raises:
            NotImplementedError: If not implemented by the plugin subclass.
        """
        raise NotImplementedError

    def render_content(self, metrics):
        """
        Renders the content based on the metrics provided. Subclasses should implement
        the logic to visualize the data in the desired format.
        
        Args:
            metrics (dict): Data to be visualized.
        
        Raises:
            NotImplementedError: If not implemented by the plugin subclass.
        """
        raise NotImplementedError
