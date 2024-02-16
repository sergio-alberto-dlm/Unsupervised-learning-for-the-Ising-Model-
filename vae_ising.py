# -*- coding: utf-8 -*-
"""vae_Ising.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-fAILtPNkOqWGAxwLp7IR3Sx14pbOsU2
"""

import numpy as np
import random
import matplotlib.pyplot as plt

import torch
from torch import nn, optim
from tqdm import tqdm
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, random_split
from torch.utils.data import Dataset
from torchvision import transforms

from google.colab import drive, files
drive.mount('/content/drive')

!cp /content/drive/MyDrive/ml_proyectos/vae_model/simulation_ising.py /content

from simulation_ising import run_simulation

# Configuration simulation
L = 28
T_min = 1e-1
T_max = 5
TRAIN_SAMPLES = 5000
TEST_SAMPLES = 500
thermal_equilibrium = 1000

# Generate samples
train_lattices, train_magnetizations = run_simulation(
    L=L, T_min=T_min, T_max=T_max, thermal_equilibrium=thermal_equilibrium, num_samples=TRAIN_SAMPLES
)
test_lattices, test_magnetizations = run_simulation(
    L=L, T_min=T_min, T_max=T_max, thermal_equilibrium=thermal_equilibrium, num_samples=TEST_SAMPLES
)

# Plot magnetization
T = np.linspace(T_min, T_max, len(train_magnetizations))
plt.plot(T, train_magnetizations)

# Visualize ferromagnetic and antiferromagnetic samples

n = 10 # Number of images to display
plt.figure(figsize=(20, 4))
for i in range(n):
  # Display ferromagnetic
  ax = plt.subplot(2, n, i + 1)
  plt.imshow(train_lattices[i + 2000], cmap='coolwarm')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)

  # Display reconstructed
  ax = plt.subplot(2, n, i + 1 + n)
  plt.imshow(train_lattices[i + 4000], cmap='coolwarm')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
plt.show()

# Preprocess the data

class LatticeTemperatureDataset(Dataset):
    def __init__(self, lattices, magnetizations):
        self.lattices = lattices
        self.magnetizations = magnetizations

    def __len__(self):
        return len(self.lattices)

    def __getitem__(self, idx):
        lattice = self.lattices[idx]
        magnetization = self.magnetizations[idx]
        tensor = torch.from_numpy(lattice).float()
        normalized_tensor = (tensor + 1) / 2
        return normalized_tensor, magnetization

train_dataset = LatticeTemperatureDataset(train_lattices, train_magnetizations)
test_dataset = LatticeTemperatureDataset(test_lattices, test_magnetizations)

# Creating DataLoader for each set
batch_size = 64
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

!cp /content/drive/MyDrive/ml_proyectos/vae_model/vae_definition.py /content

from vae_definition import VariationalAutoEncoder

# Configuration VAE
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 1
NUM_EPOCHS = 100
LR_RATE = 3e-4
model_phase_class = VariationalAutoEncoder(INPUT_DIM, H_DIM, Z_DIM).to(DEVICE)
optimizer = optim.Adam(model_phase_class.parameters(), lr = LR_RATE)
loss_fn = nn.BCELoss(reduction = "sum")


# Start Training
for epoch in range(NUM_EPOCHS):
    loop = tqdm(enumerate(train_loader))
    for i, (lattice_batch, _) in loop:
        # Forward pass
        lattice_batch = lattice_batch.to(DEVICE).view(lattice_batch.shape[0], INPUT_DIM)
        lattice_reconstructed, mu, sigma = model_phase_class(lattice_batch)

        # Compute Loss
        reconstruction_loss = loss_fn(lattice_reconstructed, lattice_batch)
        kl_div = -torch.sum(1 + torch.log(sigma.pow(2)) - mu.pow(2) - sigma.pow(2))

        # Backprop
        loss = reconstruction_loss + kl_div
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loop.set_postfix(loss = loss.item())

original_ising = []
reconstructed_ising = []
losses = []
latent_variables = []
model_phase_class.eval()
with torch.no_grad():
  for i, (x, m) in enumerate(test_loader):
    x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
    x_reconstructed, mu, sigma = model_phase_class(x)
    loss = loss_fn(x_reconstructed, x)
    epsilon = torch.randn_like(sigma)
    z_reparametrized = mu + sigma * epsilon

    original_ising.append(x.cpu())
    reconstructed_ising.append(x_reconstructed.cpu())
    losses.append(loss.item())
    latent_variables.append(z_reparametrized.item())

# Visualize reconstruction
shift = 100
n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
  # Display original
  ax = plt.subplot(2, n, i + 1)
  plt.imshow(original_ising[i + shift].view(28, 28), cmap='coolwarm')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)

  # Display reconstructed
  ax = plt.subplot(2, n, i + 1 + n)
  plt.imshow(reconstructed_ising[i + shift].reshape(28, 28), cmap='coolwarm')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
plt.show()

l = len(losses)
T = np.linspace(T_min, T_max, l)
plt.plot(T, losses)

plt.plot(T, test_magnetizations)

plt.plot(T, latent_variables)

# Configuration VAE 2D
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 2
NUM_EPOCHS = 100
LR_RATE = 3e-4
model_phase_class_2D = VariationalAutoEncoder(INPUT_DIM, H_DIM, Z_DIM).to(DEVICE)
optimizer = optim.Adam(model_phase_class_2D.parameters(), lr = LR_RATE)
loss_fn = nn.BCELoss(reduction = "sum")


# Start Training
for epoch in range(NUM_EPOCHS):
    loop = tqdm(enumerate(train_loader))
    for i, (lattice_batch, _) in loop:
        # Forward pass
        lattice_batch = lattice_batch.to(DEVICE).view(lattice_batch.shape[0], INPUT_DIM)
        lattice_reconstructed, mu, sigma = model_phase_class_2D(lattice_batch)

        # Compute Loss
        reconstruction_loss = loss_fn(lattice_reconstructed, lattice_batch)
        kl_div = -torch.sum(1 + torch.log(sigma.pow(2)) - mu.pow(2) - sigma.pow(2))

        # Backprop
        loss = reconstruction_loss + kl_div
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        loop.set_postfix(loss = loss.item())

# --->Extract Latent Representations
# latent space representation (mean, 'mu').

latent_representations = []
labels = []
model_phase_class_2D.eval()
with torch.no_grad():
  for x, y in test_loader:
    x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
    mu, _ = model_phase_class_2D.encode(x)
    latent_representations.append(mu.cpu())
    labels.extend(y.cpu())


# Visualize with Scatter Plot

latent_representations = torch.cat(latent_representations, dim=0)
labels = [0 if magnetization.item() < 0.2 else 1 for magnetization in labels]
labels = np.array(labels)

# 0 paramagnetico 1 magnetico
plt.figure(figsize=(10, 8))
for magnetization in range(2):
  indices = labels == magnetization
  plt.scatter(latent_representations[indices, 0], latent_representations[indices, 1], label=str(magnetization))
plt.legend()
plt.title('Visualización de la representación latente')
plt.show()

# PCA
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Preprocess the data
ising_data = pd.DataFrame(np.array(train_lattices).reshape(TRAIN_SAMPLES, 784))
scaler = StandardScaler()
data_scaled = scaler.fit_transform(ising_data)

# Apply PCA
pca = PCA(n_components=2)
scores = pca.fit_transform(data_scaled)

explained_variance = pca.explained_variance_ratio_
cumulative_variance_ratio = np.cumsum(explained_variance)

print('Varianza explicada:\n', explained_variance)
print('Varianza explicada acumulado:\n', cumulative_variance_ratio)

# Visualize
labels = [0 if train_magnetizations[i] < 0.2 else 1 for i in range(len(train_magnetizations))]
labels = np.array(labels)
plt.figure(figsize=(10, 10))
for magnetization in range(2):
  indices = labels == magnetization
  plt.scatter(scores[indices, 0], scores[indices, 1], label=str(magnetization))
plt.legend()
plt.title('PCA for the Ising model')
plt.show()