import torch
import torch.nn as nn


class VoxCNN(nn.Module):
    """
    VoxCNN is a convolutional neural network for 3D image classification.

    Args:
        num_classes (int): The number of classes in the classification problem. Defaults to 4.
    """
    def __init__(self, num_classes=4):
        """
        Initializes a new instance of the VoxCNN class.

        Args:
            num_classes (int): The number of classes in the classification problem. Defaults to 4.
        """
        super(VoxCNN, self).__init__()
        self.num_classes = num_classes

        # Define the convolutional layers.
        self.features = nn.Sequential(
            nn.Conv3d(in_channels=1, out_channels=8, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv3d(in_channels=8, out_channels=8, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.Conv3d(in_channels=8, out_channels=16, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv3d(in_channels=16, out_channels=16, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.Conv3d(in_channels=16, out_channels=32, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv3d(in_channels=32, out_channels=32, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv3d(in_channels=32, out_channels=32, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2),
            nn.Conv3d(in_channels=32, out_channels=64, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv3d(in_channels=64, out_channels=64, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.Conv3d(in_channels=64, out_channels=64, kernel_size=3, padding='same'),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2)
        )

        # Define the fully connected layers.
        self.classifier = nn.Sequential(
            # in_features = channel x depth x width x height
            nn.Linear(in_features=64*8*8*8, out_features=128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(in_features=128, out_features=64),
            nn.ReLU(),
            nn.Linear(in_features=64, out_features=self.num_classes)
        )

    def forward(self, x):
        """
        Forward pass of the VoxCNN.

        Args:
            x (torch.Tensor): The input tensor of shape (batch_size, 1, depth, height, width).

        Returns:
            torch.Tensor: The output tensor of shape (batch_size, num_classes).
        """
        x = self.features(x)
        x = torch.flatten(x, start_dim=1)
        x = self.classifier(x)
        return x
