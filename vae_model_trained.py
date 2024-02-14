# -*- coding: utf-8 -*-
"""vae_model_trained.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LyU5gGuSFycIAutNopc8gMTODsTIi1Ve
"""

import torch
import torch.nn.functional as F
from torch import nn

from google.colab import drive
drive.mount('/content/drive')

!cp /content/drive/MyDrive/ml_proyectos/vae_model/vae_definition.py /content

from vae_definition import VariationalAutoEncoder

import torchvision.datasets as datasets
from tqdm import tqdm
from torch import nn, optim
from torchvision import transforms
from torchvision.utils import save_image
from torch.utils.data import DataLoader

# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 20
NUM_EPOCHS = 20
BATCH_SIZE = 32
LR_RATE = 3e-4

# Dataset Loading
dataset = datasets.MNIST(root = "dataset/", train = True, transform = transforms.ToTensor(), download = True)
train_loader = DataLoader(dataset = dataset, batch_size = BATCH_SIZE, shuffle = True)
model = VariationalAutoEncoder(INPUT_DIM, H_DIM, Z_DIM).to(DEVICE)
optimizer = optim.Adam(model.parameters(), lr = LR_RATE)
loss_fn = nn.BCELoss(reduction = "sum")

# Start Training
for epoch in range(NUM_EPOCHS):
    loop = tqdm(enumerate(train_loader))
    for i, (x, _) in loop:
    # Forward pass
      x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
      x_reconstructed, mu, sigma = model(x)

    # Compute Loss
      reconstruction_loss = loss_fn(x_reconstructed, x)
      kl_div = -torch.sum(1 + torch.log(sigma.pow(2)) - mu.pow(2) - sigma.pow(2))

    # Backprop
      loss = reconstruction_loss + kl_div
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      loop.set_postfix(loss = loss.item())

save_path = '/content/drive/MyDrive/ml_proyectos/vae_model/vae_model.pth'

torch.save(model.state_dict(), save_path)

# Start training the VAE for visualization in 2D
import torchvision.datasets as datasets
from tqdm import tqdm
from torch import nn, optim
from torchvision import transforms
from torchvision.utils import save_image
from torch.utils.data import DataLoader

# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 2
NUM_EPOCHS = 20
BATCH_SIZE = 32
LR_RATE = 3e-4

# Dataset Loading
dataset = datasets.MNIST(root = "dataset/", train = True, transform = transforms.ToTensor(), download = True)
train_loader = DataLoader(dataset = dataset, batch_size = BATCH_SIZE, shuffle = True)
model_2D = VariationalAutoEncoder(INPUT_DIM, H_DIM, Z_DIM).to(DEVICE)
optimizer = optim.Adam(model_2D.parameters(), lr = LR_RATE)
loss_fn = nn.BCELoss(reduction = "sum")

# Start Training
for epoch in range(NUM_EPOCHS):
    loop = tqdm(enumerate(train_loader))
    for i, (x, _) in loop:
    # Forward pass
      x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
      x_reconstructed, mu, sigma = model_2D(x)

    # Compute Loss
      reconstruction_loss = loss_fn(x_reconstructed, x)
      kl_div = -torch.sum(1 + torch.log(sigma.pow(2)) - mu.pow(2) - sigma.pow(2))

    # Backprop
      loss = reconstruction_loss + kl_div
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      loop.set_postfix(loss = loss.item())

save_path = '/content/drive/MyDrive/ml_proyectos/vae_model/vae_model_2D.pth'

torch.save(model_2D.state_dict(), save_path)

"""**Conditional model**"""

from vae_definition_conditional import ConditionalVariationalAutoEncoder

# Create One-Hot Labels

def one_hot(labels, num_classes=10):
  return torch.eye(num_classes)[labels].to(DEVICE)

# Start training the conditional VAE
import torchvision.datasets as datasets
from tqdm import tqdm
from torch import nn, optim
from torchvision import transforms
from torchvision.utils import save_image
from torch.utils.data import DataLoader

# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 20
LABEL_DIM = 10
NUM_EPOCHS = 20
BATCH_SIZE = 32
LR_RATE = 3e-4

# Dataset Loading
dataset = datasets.MNIST(root = "dataset/", train = True, transform = transforms.ToTensor(), download = True)
train_loader = DataLoader(dataset = dataset, batch_size = BATCH_SIZE, shuffle = True)
conditional_model = ConditionalVariationalAutoEncoder(INPUT_DIM, LABEL_DIM, H_DIM, Z_DIM).to(DEVICE)
optimizer = optim.Adam(conditional_model.parameters(), lr = LR_RATE)
loss_fn = nn.BCELoss(reduction = "sum")

for epoch in range(NUM_EPOCHS):
    loop = tqdm(enumerate(train_loader))
    for i, (x, y) in loop:
      # Forward pass
        x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
        y = one_hot(y).to(DEVICE)
        x_reconstructed, mu, sigma = conditional_model(x, y)

      # Compute Loss
        reconstruction_loss = loss_fn(x_reconstructed, x)
        kl_div = -torch.sum(1 + torch.log(sigma.pow(2)) - mu.pow(2) - sigma.pow(2))

      # Backprop
        loss = reconstruction_loss + kl_div
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loop.set_postfix(loss = loss.item())

save_path = '/content/drive/MyDrive/ml_proyectos/vae_model/vae_model_conditional.pth'

torch.save(conditional_model.state_dict(), save_path)