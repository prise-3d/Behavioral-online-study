import os
import random
from typing import overload
from ..models import ExperimentProgress, Experiment

class ClassicalExperimentProgress(ExperimentProgress):
    """
    Example of Classical experiment with specific number of iteration
    """    
    
    def start(self, user_data):
        """
        Define and init some progress variables
        """
        if self.data is None:
            self.data = {}

        self.data['iteration'] = 0
        self.data['user'] = {
            'username': user_data['classical-info-surname'],
            'why': user_data['classical-info-why'],
            'glasses': user_data['classical-info-glasses'],
        }

        # always save state
        self.save()

    def next(self, step, answer) -> dict:
        """
        Define next step data object taking into account current step and answer

        Return: JSON data object
        """

        # 1. update previous step depending of answer (if previous step exists)
        if step is not None:
            answer_time = answer['classical-answer-time']
            answer_value = answer['classical-answer-value']
            
            step.data['answer_time'] = answer_time
            step.data['answer_value'] = answer_value
            step.save()
        
        # 2. process next step data (can be depending of answer)

        # folder of images could also stored into experiment config
        cornel_box_path = 'resources/images/cornel_box'
        # need to take care of static media folder
        images_path = sorted([ 
                    os.path.join(cornel_box_path, img) 
                    for img in os.listdir(os.path.join('static', cornel_box_path)) 
                ])

        # right image always display reference
        # prepare next step data
        step_data = {
            "left_image": {
                "src": f"{random.choice(images_path)}",
                "width": 500,
                "height": 500
            },
            "right_image": {
                "src": f"{images_path[-1]}",
                "width": 500,
                "height": 500
            }
        }

        # increment iteration into progress data
        self.data['iteration'] += 1

        # always save state
        self.save()

        return step_data

    def progress(self) -> float:
        """
        Define the percent progress of the experiment

        Return: float progress between [0, 100]
        """
        total_iterations = int(self.session.config['iterations'])
        iteration = int(self.data['iteration'])

        # return percent of session advancement
        return (iteration / total_iterations) * 100

    def end(self) -> bool:
        """
        Check whether it's the end or not of the experiment

        Return: bool
        """
        total_iterations = int(self.session.config['iterations'])
        iteration = int(self.data['iteration'])

        return iteration >= total_iterations


