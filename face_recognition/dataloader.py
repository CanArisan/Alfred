"""Definition of Dataloader"""

import numpy as np


class DataLoader:
    """
    Dataloader Class
    Defines an iterable batch-sampler over a given dataset
    """
    def __init__(self, dataset, batch_size=1, shuffle=False, drop_last=False):
        """
        :param dataset: dataset from which to load the data
        :param batch_size: how many samples per batch to load
        :param shuffle: set to True to have the data reshuffled at every epoch
        :param drop_last: set to True to drop the last incomplete batch,
            if the dataset size is not divisible by the batch size.
            If False and the size of dataset is not divisible by the batch
            size, then the last batch will be smaller.
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.drop_last = drop_last

    def __iter__(self):
        if self.shuffle:
            index_iterator = np.random.permutation(len(self.dataset))  # define indices as iterator
        else:
            index_iterator = range(len(self.dataset))  # define indices as iterator

        batch = {'labels': np.array([])}
        image_counter = 0
        for index in index_iterator:  # iterate over indices using the iterator
            image_dict = self.dataset[index]
            batch['image{}'.format(image_counter)] = image_dict['image']
            batch['labels'] = np.append(batch['labels'], image_dict['label'])
            image_counter += 1
            if len(batch['labels']) == self.batch_size:
                yield batch  # use yield keyword to define a iterable generator
                batch = {'labels': np.array([])}
                image_counter = 0
        if not self.drop_last and len(batch) != 0:
            yield batch

    def __len__(self):
        modulo = len(self.dataset) % self.batch_size
        length = len(self.dataset) // self.batch_size
        if not self.drop_last and modulo != 0:
            length += 1
        return length
