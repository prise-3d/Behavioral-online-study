import os
from typing import overload
from ..models import ExperimentProgress

class ClassicalExperimentProgress(ExperimentProgress):
    """
    Example of Classical experiment with specific number of iteration
    """    
    
    def start(self) -> dict:
        """
        Define start experiment method

        Return: dict object
        """
        pass

    def next(self, step) -> dict:
        """
        Define next step data object taking into account current step

        Return: JSON data object
        """
        pass

    def progress(self) -> float:
        """
        Define the percent progress of the experiment

        Return: float progress between [0, 100]
        """
        pass

    def end(self) -> bool:
        """
        Check whether it's the end or not of the experiment

        Return: bool
        """
        pass
