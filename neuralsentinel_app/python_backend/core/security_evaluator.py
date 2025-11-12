class SecurityEvaluator:
    """
    Base class for security evaluators.
    All plugins that extend this class must implement the 'evaluate' method to perform security assessments.
    """

    def __init__(self, logger):
        """
        Initializes the SecurityEvaluator with a logger function.
        
        Args:
            logger (callable): A function that logs messages for reporting purposes.
        """
        self.logger = logger

    def evaluate(self, input_data):
        """
        Evaluates the provided input data and returns security metrics.
        This method must be implemented by any subclass of SecurityEvaluator.

        Args:
            input_data (dict): A dictionary containing information about the file or data to evaluate.
        
        Returns:
            dict: A dictionary containing the security metrics evaluated from the input data.
        
        Raises:
            NotImplementedError: If the 'evaluate' method is not implemented by the plugin subclass.
        """
        raise NotImplementedError("The evaluate method must be implemented by the plugin.")
