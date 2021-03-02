import torch
from torch.utils.data import DataLoader
from face_recognition.dataloader import Dataset
from face_recognition.network import Network
from torchvision import transforms
import os
import pytorch_lightning as pl

root_path = os.path.join(os.getcwd(), 'dataset')

train_dataset = Dataset(
    mode='train',
    transform=transforms.ToTensor(),
    root=root_path
)

val_dataset = Dataset(
    mode='dev',
    transform=transforms.ToTensor(),
    root=root_path
)

print('Training samples: {}'.format(len(train_dataset)))
print('Validation samples: {}'.format(len(val_dataset)))

hparams = {
    'batch_size': 32,
    'num_channels': [3, 6, 9, 18, 36, 72],
    'lr': 0.0001,
    'dropout': 0.2
}

train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=hparams['batch_size'])
val_dataloader = DataLoader(val_dataset, shuffle=True, batch_size=hparams['batch_size'])

trainer = pl.Trainer(
    max_epochs=150,
    gpus=1 if torch.cuda.is_available() else None
)

model = Network(hparams)

trainer.fit(model, train_dataloader, val_dataloader)

torch.save(model, os.path.join(os.getcwd(), 'model'))
