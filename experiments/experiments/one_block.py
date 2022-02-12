import os
import random
import time
import numpy as np
from PIL import Image, ImageDraw
from ..models import SessionProgress
from django.conf import settings


class Point():

    def __init__(self, x, y):
        self._x = x
        self._y = y
        # self.padding_removed = False

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def set_x(self, x):
        self._x = x

    @y.setter
    def set_y(self, y):
        self._y = y

    def remove_padding(self, padding):
        
        x = None
        y = None

        #if not self.padding_removed:
        x = self._x - padding
        y = self._y - padding

        # avoid issue later with numpy index access
        if x < 0:
            x = 0

        if y < 0:
            y = 0

        #self.padding_removed = True
        return Point(x, y)

    def __str__(self) -> str:
        return f'({self._x}, {self._y})'




class OneBlockSessionProgress(SessionProgress):
    """
    Example of OneBlock experiment with specific number of iteration
    """    

    def get_random_block_coordinate(self):

        w, h = self.session.config['img_size']
        padding = self.session.config['padding']
        w_b, h_b = self.session.config['block_size']

        # avoid overlapping generation
        w_random = int(random.uniform(0, w - w_b + 2 * padding))
        h_random = int(random.uniform(0, h - h_b + 2 * padding))

        l1 = Point(w_random, h_random)
        l2 = Point(w_random + w_b, h_random + h_b)

        return l1, l2
    
    def add_red_box(self, image, points):
        
        padding = self.session.config['padding']
        l1, l2 = points
        shape = [(l1.x - padding * 2, l1.y - padding * 2), (l2.x, l2.y)]

        image_draw = ImageDraw.Draw(image)  
        image_draw.rectangle(shape, outline ="red", width=3)

        return image

    def start(self, participant_data):
        """
        Define and init some progress variables
        """

        # need to be initialized in order to start experiment
        if self.data is None:
            self.data = {}

        self.data['iteration'] = 0
        self.data['participant'] = {
            'know-cg': participant_data['basic-info-know-cg'],
            'why': participant_data['basic-info-why'],
            'glasses': participant_data['basic-info-glasses'],
        }

        dataset_path = self.session.experiment.config['dataset']

        scenes_path = os.listdir(os.path.join(settings.RELATIVE_STATIC_URL, dataset_path))
        first_scene = random.choice(scenes_path)

        # initialize first scene, selected and done
        self.data['selected_scene'] = first_scene
        self.data['scenes'] = scenes_path
        self.data['scenes_done'] = []

        n_images = len(os.listdir(os.path.join(settings.RELATIVE_STATIC_URL, dataset_path, first_scene)))
        self.data['selected_index'] = n_images - 1

        # get block information
        p1, p2 = self.get_random_block_coordinate()
        self.data['selected_block'] = [p1.x, p1.y, p2.x, p2.y]

        # always save state
        self.save()

    def next(self, step, answer) -> dict:
        """
        Define next step data object taking into account current step and answer

        Return: JSON data object
        """

        dataset_path = self.session.experiment.config['dataset']

        # 1. update previous step depending of answer (if previous step exists)
        if step is not None:
            answer_time = answer['binary-answer-time']
            answer_value = answer['binary-answer-value']
            
            step.data['answer_time'] = answer_time
            step.data['answer_value'] = answer_value
            step.save()

            # update answer
            if int(self.data['iteration']) > 0 and int(answer_value) == 1:
                self.data['selected_index'] = int(self.data['selected_index'] / 2)

            if int(self.data['iteration']) > 0 and int(answer_value) == 0:
                self.data['selected_index'] = int(self.data['selected_index'] * 1.5)
    
            # 2. process next step data (can be depending of answer)
            # TODO: check better stopping creterion here based on previous answer
            if self.data['iteration'] > 0 and int(answer_value) == 0:

                self.data['iteration'] = 0

                # add to scene done
                self.data['scenes_done'].append(self.data['selected_scene'])

                # end of the experiment all scenes done
                if len(self.data['scenes_done'] >= self.data['scenes']):
                    return None

                # new selected scene
                self.data['selected_scene'] = random.choice([s for s in self.data['scenes'] if s not in self.data['scenes_done'] ])

                # define new block
                n_images = len(os.listdir(os.path.join(settings.RELATIVE_STATIC_URL, dataset_path, self.data['selected_scene'])))
                self.data['selected_index'] = n_images - 1

                # get new block information
                p1, p2 = self.get_random_block_coordinate()
                self.data['selected_block'] = [p1.x, p1.y, p2.x, p2.y]

        # folder of images could also stored into experiment config
        scene_path = os.path.join(dataset_path, self.data['selected_scene'])

        # need to take care of static media folder
        images_path = sorted([ 
                    os.path.join(scene_path, img) 
                    for img in os.listdir(os.path.join(settings.STATIC_URL, scene_path)) 
                ])

        # get reference image
        ref_image = np.array(Image.open(os.path.join(settings.RELATIVE_STATIC_URL, images_path[-1])))
        reconstructed_image = np.copy(ref_image)

        # get spp level image
        spp_level_image = np.array(Image.open(os.path.join(os.path.join(settings.RELATIVE_STATIC_URL, images_path[self.data['selected_index']]))))

        x1, y1, x2, y2 = self.data['selected_block']

        p1 = Point(x1, y1)
        p2 = Point(x2, y2)

        # replace block with spp
        p1 = p1.remove_padding(self.session.config['padding'])
        p2 = p2.remove_padding(self.session.config['padding'])

        reconstructed_image[p1.y:p2.y, p1.x:p2.x] = spp_level_image[p1.y:p2.y, p1.x:p2.x]

        # redifined selected block without padding removed
        x1, y1, x2, y2 = self.data['selected_block']

        p1 = Point(x1, y1)
        p2 = Point(x2, y2)

        # add red boxes
        reconstructed_pil_image = Image.fromarray(np.array(reconstructed_image, 'uint8'))
        reconstructed_pil_image = self.add_red_box(reconstructed_pil_image, (p1, p2))

        ref_pil_image = Image.fromarray(np.array(ref_image, 'uint8'))
        ref_pil_image = self.add_red_box(ref_pil_image, (p1, p2))
        
        # save generated image into static folder (need the access of the new image)
        generated_path = os.path.join(settings.RELATIVE_STATIC_URL, 'generated')

        if not os.path.exists(generated_path):
            os.makedirs(generated_path)

        output_image_path_left = os.path.join(generated_path, f'{self.participant.id}_left.png')
        reconstructed_pil_image.save(output_image_path_left)

        output_image_right = os.path.join(generated_path, f'{self.participant.id}_right.png')
        ref_pil_image.save(output_image_right)

        # right image always display reference
        # prepare next step data
        step_data = {
            "left_image": {
                "src": f"{output_image_path_left.replace(settings.RELATIVE_STATIC_URL, '')}",
                "width": 500,
                "height": 500
            },
            "right_image": {
                "src": f"{output_image_right.replace(settings.RELATIVE_STATIC_URL, '')}",
                "width": 500,
                "height": 500
            },
            "scene": self.data['selected_scene'],
            "image_index": self.data['selected_index'],
            "selected_block": self.data['selected_block'],
            "iteration": self.data['iteration']
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
        total_scenes = len(self.data['scenes'])
        scenes_done = len(self.data['scenes_done'])

        # return percent of session advancement
        return (scenes_done / total_scenes) * 100

    def end(self) -> bool:
        """
        Check whether it's the end or not of the experiment

        Return: bool
        """
        # get number of scene
        total_scenes = len(self.data['scenes'])
        scenes_done = len(self.data['scenes_done'])

        return scenes_done >= total_scenes