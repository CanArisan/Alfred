import torch
from torch.utils.data import DataLoader

from face_recognition.dataloader import Dataset
from face_recognition.network import Network
from torchvision import transforms
import os

root_path = os.path.join(os.getcwd(), 'dataset')

test_dataset = Dataset(
    mode='test',
    transform=transforms.ToTensor(),
    root=root_path
)

print('Test samples: {}'.format(len(test_dataset)))

model = torch.load(os.path.join(os.getcwd(), 'model'))


def evaluate_model(model, dataset):
    model.eval()
    criterion = torch.nn.MSELoss()
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)
    loss = 0
    for batch in dataloader:
        image, keypoints = batch["image"], batch["keypoints"]
        predicted_keypoints = model(image).view(-1, 15, 2)
        loss += criterion(
            torch.squeeze(keypoints),
            torch.squeeze(predicted_keypoints)
        ).item()
    return 1.0 / (2 * (loss/len(dataloader)))


print("Score:", evaluate_model(model, test_dataset))
