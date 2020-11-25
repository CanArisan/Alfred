from face_recognition.image_folder_dataset import ImageFolderDataset
from face_recognition.transforms import *
from face_recognition.dataloader import DataLoader
from PIL import Image

from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np
import os


def load_image_as_numpy(path):
    return np.asarray(Image.open(path), dtype=float)


class DataLoaderTest(TestCase):

    root_path = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), 'dataset')
    dataset = ImageFolderDataset(root_path=root_path, transform=None)
    rescale = RescaleTransform()

    images = list(map(lambda i: np.asarray(Image.open(i)), dataset.images))
    image_mean, image_std = compute_image_mean_and_std(images)
    rescaled_mean, rescaled_std = rescale.scale_values([image_mean, image_std])
    normalize = NormalizeTransform(rescaled_mean, rescaled_std)

    dataset.transform = ComposeTransform([rescale, normalize])
    classes = ['bird', 'cat', 'dog']

    def test_dataset_initial_state(self):
        num_classes = len(self.classes)
        samples_per_class = 7
        for label, cls in enumerate(sorted(self.classes)):
            for i in range(samples_per_class):
                image_path = os.path.join(
                    self.root_path,
                    cls,
                    str(i+1).zfill(4) + ".png"
                )  # e.g. dataset/bird/0001.png
                image = np.asarray(Image.open(image_path))  # open image as numpy array
                plt_idx = i * num_classes + label + 1  # calculate plot location in the grid
                plt.subplot(samples_per_class, num_classes, plt_idx)
                plt.imshow(image.astype('uint8'))
                plt.axis('off')
                if i == 0:
                    plt.title(cls)  # plot class names above columns
        plt.show()

    def test_dataloader(self):
        dataloader = DataLoader(
            dataset=self.dataset,
            batch_size=50,
            shuffle=False,
            drop_last=False
        )

        batches = []
        for batch in dataloader:
            batches.append(batch)
        print('{} batches processed.'.format(len(batches)))
        assert len(dataloader) == len(batches)

        assert len(batches[0]['image0']) == 32  # Height
        assert len(batches[0]['image0'][0]) == 32  # Width
        assert len(batches[0]['image0'][0][0]) == 3  # 3 channels

        assert len(batches[0]['labels']) == dataloader.batch_size
        assert len(batches[0].keys()) - 1 == dataloader.batch_size  # -1 to subtract 'labels'
