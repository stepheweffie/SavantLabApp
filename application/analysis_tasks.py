import d6tflow
import pandas as pd
import numpy as np
from PIL import Image


class LoadDrawingTask(d6tflow.tasks.TaskPandas):
    image_path = d6tflow.Parameter()

    def run(self):
        img = Image.open(self.image_path)
        img_data = np.asarray(img)
        self.save(img_data)


class ProcessPixelDataTask(d6tflow.tasks.TaskPandas):
    image_path = d6tflow.Parameter()

    def requires(self):
        return LoadDrawingTask(image_path=self.image_path)

    def run(self):
        img_data = self.inputLoad()
        grayscale_data = np.dot(img_data, [0.2989, 0.5870, 0.1140])
        self.save(grayscale_data)


class AnalyzeDrawingTask(d6tflow.tasks.TaskPandas):
    image_path = d6tflow.Parameter()

    def requires(self):
        return ProcessPixelDataTask(image_path=self.image_path)

    def run(self):
        grayscale_data = self.inputLoad()
        mean_pixel_value = np.mean(grayscale_data)
        std_pixel_value = np.std(grayscale_data)
        self.save(pd.DataFrame({"mean": [mean_pixel_value], "std": [std_pixel_value]}))
