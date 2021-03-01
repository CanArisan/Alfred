import torch
import torch.nn as nn
import pytorch_lightning as pl

class Network(pl.LightningModule):
    def __init__(self, hparams):
        super().__init__()
        self.hparams = hparams
        num_channels = self.hparams["num_channels"]

        self.model = nn.Sequential(
            nn.Conv2d(1, num_channels[0], 5, padding=2),
            nn.BatchNorm2d(num_features=num_channels[0]),
            nn.ReLU(),
            nn.Conv2d(num_channels[0], num_channels[1], 5, padding=2),
            nn.BatchNorm2d(num_features=num_channels[1]),
            nn.ReLU(),

            nn.MaxPool2d(2, 2),  # 96 x 96 -> 48 x 48
            nn.Dropout(self.hparams["dropout"]),

            nn.Conv2d(num_channels[1], num_channels[2], 5, padding=2),
            nn.BatchNorm2d(num_features=num_channels[2]),
            nn.ReLU(),
            nn.Conv2d(num_channels[2], num_channels[3], 5, padding=2),
            nn.BatchNorm2d(num_features=num_channels[3]),
            nn.ReLU(),

            nn.MaxPool2d(2, 2),  # 48 x 48 -> 24 x 24
            nn.Dropout(self.hparams["dropout"]),

            nn.Conv2d(num_channels[3], num_channels[4], 5, padding=2),
            nn.BatchNorm2d(num_features=num_channels[4]),
            nn.ReLU(),
            nn.Conv2d(num_channels[4], num_channels[5], 5, padding=2),
            nn.BatchNorm2d(num_features=num_channels[5]),
            nn.ReLU(),

            nn.MaxPool2d(2, 2),  # 24 x 24 -> 12 x 12
            nn.Dropout(self.hparams["dropout"]),
            nn.Flatten(start_dim=1, end_dim=-1),
            nn.Linear(72 * 12 * 12, 30)
        )

    def forward(self, x):
        x = self.model(x)
        return x

    def general_step(self, batch, batch_idx, mode):
        image, targets = batch["image"], batch["keypoints"]
        loss_func = nn.MSELoss()
        out = self.forward(image)
        prediction = out.view(-1, 15, 2)
        loss = loss_func(prediction, targets)
        return loss

    def general_end(self, outputs, mode):
        avg_loss = torch.stack([x[mode + '_loss'] for x in outputs]).mean()
        return avg_loss

    def training_step(self, batch, batch_idx):
        loss = self.general_step(batch, batch_idx, "train")
        tensorboard_logs = {'loss': loss}
        return {'loss': loss, 'log': tensorboard_logs}

    def validation_step(self, batch, batch_idx):
        loss = self.general_step(batch, batch_idx, "val")
        return {'val_loss': loss}

    def validation_end(self, outputs):
        avg_loss = self.general_end(outputs, "val")
        tensorboard_logs = {'val_loss': avg_loss}
        return {'val_loss': avg_loss, 'log': tensorboard_logs}

    def configure_optimizers(self):
        optim = torch.optim.Adam(self.parameters(), lr=self.hparams["lr"])
        return optim
