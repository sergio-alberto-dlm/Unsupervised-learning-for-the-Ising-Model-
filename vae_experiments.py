# -*- coding: utf-8 -*-
"""vae_experiments.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/109Oa8_WWKCavZJKR2_GSC1ZKoQhRgXF-
"""

import torch
from google.colab import drive, files
drive.mount('/content/drive')
import torchvision.datasets as datasets # Standard datasets
from torchvision import transforms
from torch.utils.data import DataLoader
from torch import nn, optim

!cp /content/drive/MyDrive/ml_proyectos/vae_model/vae_definition.py /content

from vae_definition import VariationalAutoEncoder
# Define the path to the model file
model_path = '/content/drive/MyDrive/ml_proyectos/vae_model/vae_model.pth'

# Initialize the model (make sure to use the same parameters as the saved model)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 20
model = VariationalAutoEncoder(INPUT_DIM, H_DIM, Z_DIM)
BATCH_SIZE = 32

# Load the saved state dictionary into the model
model.load_state_dict(torch.load(model_path))

# Set the model to evaluation mode if not training further
model.eval()
model = model.to(DEVICE)

"""**Reconstruction Quality**

"""

# Load test Data
test_dataset = datasets.MNIST(root="dataset/", train=False, transform=transforms.ToTensor(), download=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=BATCH_SIZE, shuffle=True)

# --->Reconstructed Images
# Pass test images trough the VAE and obtain reconstructed images
reconstructed_images = []
original_images = []
with torch.no_grad():
  for x, _ in test_loader:
    x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
    x_reconstructed, _, _ = model(x)
    reconstructed_images.append(x_reconstructed.cpu())
    original_images.append(x.cpu())

# --->Quantitative Evaluation
# Calculate Mean Squared Error (MSE) between original and reconstructed images

mse_loss = nn.MSELoss()
total_mse = 0
for original, reconstructed in zip(original_images, reconstructed_images):
  total_mse += mse_loss(reconstructed, original).item()
average_mse = total_mse / len(original_images)
print("Average MSE: ", average_mse)

# --->Visual Comparison
# Visualize a few pairs of original and reconstructed images

import matplotlib.pyplot as plt
n = 10 # Number of images to display
plt.figure(figsize=(20, 4))
for i in range(n):
  # Display original
  ax = plt.subplot(2, n, i + 1)
  plt.imshow(original_images[i][0].view(28, 28))
  plt.gray()
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)

  # Display reconstructed
  ax = plt.subplot(2, n, i + 1 + n)
  plt.imshow(reconstructed_images[i][0].view(28, 28))
  plt.gray()
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
plt.savefig('original_reconstructed.png', bbox_inches='tight')
plt.show()

"""**Latent space visualization**"""

from vae_definition import VariationalAutoEncoder
# Define the path to the model file
model_path = '/content/drive/MyDrive/ml_proyectos/vae_model/vae_model_2D.pth'

# Initialize the model (make sure to use the same parameters as the saved model)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 2
modelV = VariationalAutoEncoder(INPUT_DIM, H_DIM, Z_DIM)
BATCH_SIZE = 32

# Load the saved state dictionary into the model
modelV.load_state_dict(torch.load(model_path))

# Set the model to evaluation mode if not training further
modelV.eval()
modelV = modelV.to(DEVICE)

# --->Extract Latent Representations
# Run thee MNIST tes dataset through the VAE encoder to obtain the
# latent space representation (mean, 'mu').

latent_representations = []
labels = []
modelV.eval()
with torch.no_grad():
  for x, y in test_loader:
    x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
    mu, _ = modelV.encode(x)
    latent_representations.append(mu.cpu())
    labels.extend(y.cpu())


# Visualize with Scatter Plot
import numpy as np

latent_representations = torch.cat(latent_representations, dim=0)
labels = np.array(labels)


plt.figure(figsize=(10, 8))
for digit in range(10):
  indices = labels == digit
  plt.scatter(latent_representations[indices, 0], latent_representations[indices, 1], label=str(digit))
plt.legend()
plt.title('Visualización de la representación latente')
plt.savefig('latent_visualization.png', bbox_inches='tight')
plt.show()

"""**Interpolation in Latent Space**"""

# Select representative images
dataset = datasets.MNIST(root = "dataset/", train = True, transform = transforms.ToTensor(), download = True)
rep_images = []
for x, y in dataset:
  if y == 0:
    rep_images.append(x)
  if y == 1:
    rep_images.append(x)
    break

rep_images
# Plot the images
plt.figure(figsize=(5, 5))
n=1
for i in range(n):
  ax = plt.subplot(1, 2, 1 + i)
  plt.imshow(rep_images[i].view(28, 28))
  ax.get_yaxis().set_visible(False)
  ax.get_xaxis().set_visible(False)

  ax = plt.subplot(1, 2, 1 + i + n)
  plt.imshow(rep_images[i+1].view(28, 28))
  ax.get_yaxis().set_visible(False)
  ax.get_xaxis().set_visible(False)

# Obtain latent representations

latent_representations = []
model.eval()
with torch.no_grad():
  for image in rep_images:
    image = image.view(1, -1).to(DEVICE)
    mu, _ = model.encode(image)
    latent_representations.append(mu.cpu())

# Perform interpolation

interpolated_latent = []
n_steps = 10
for i in range(n_steps):
  alpha = i / float(n_steps - 1)
  latent_vec = (1 - alpha) * latent_representations[0] + alpha * latent_representations[1]
  interpolated_latent.append(latent_vec)

# Generate interpolated images

interpolated_images = []
model.eval()
with torch.no_grad():
  for inter in interpolated_latent:
    inter = inter.view(1, -1).to(DEVICE)
    interpolated_image = model.decode(inter)
    interpolated_images.append(interpolated_image.cpu())

# Plot interpolated images
n = len(interpolated_images)
plt.figure(figsize=(20, 2))
for i in range(n):
  ax = plt.subplot(1, n, 1 + i)
  plt.imshow(interpolated_images[i].view(28, 28))
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
plt.savefig('interpolation.png', bbox_inches='tight')
plt.show()

"""**Sampling New Images**

"""

# Generate Random Points in the Latent Space
import random

random.seed(42)
n_samples = 10
z_dim = 20
random_latent_vectors = torch.randn(n_samples, z_dim).to(DEVICE)

# Decode Latent Points

gen_images = []
model.eval()
with torch.no_grad():
  for rand_lat_vec in random_latent_vectors:
    rand_lat_vec = rand_lat_vec.view(1, -1).to(DEVICE)
    gen_image = model.decode(rand_lat_vec)
    gen_images.append(gen_image.cpu())

# Visualize and Asses
plt.figure(figsize=(20, 2))
for i in range(n_samples):
  ax = plt.subplot(1, n_samples, 1 + i)
  plt.imshow(gen_images[i].view(28, 28))
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
plt.show()

"""**Robustness to Noise**

"""

# Select a batch of images
images, _ = next(iter(test_loader))

# Add Gussian noise
noise = torch.randn_like(images) * 0.5
noisy_images = images + noise
images = [x.view(1, -1) for x in images]

# Reconstruct Noisy Images
reconstructed_images = []
model.eval()
with torch.no_grad():
  for x in noisy_images:
    x = x.view(1, -1).to(DEVICE)
    x_reconstructed, _, _ = model(x)
    reconstructed_images.append(x_reconstructed.cpu())

# Evaluate Reconstruction Quality
mse = nn.MSELoss()
total_mse
for original, reconstructed in zip(images, reconstructed_images):
  total_mse += mse(original, reconstructed).item()
average_mse = total_mse / len(original_images)
print('Average MSE of noisy images: ', average_mse)

# Visualize noisy and reconstructed images
n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
  # Display noisy images
  ax = plt.subplot(2, n, i + 1)
  plt.imshow(noisy_images[i].view(28, 28))
  plt.gray()
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)

  # Display reconstructed images
  ax = plt.subplot(2, n, i + 1 + n)
  plt.imshow(reconstructed_images[i].view(28, 28))
  plt.gray()
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
plt.savefig('robustness.png', bbox_inches='tight')
plt.show()

"""**Anomaly Detection**"""

# --->Prepare Anomalous Data

# Load Fasshion-MNIST Dataset
fashion_mnist_dataset = datasets.FashionMNIST(root='dataset/fashion_mnist', train=False, transform=transforms.ToTensor(), download=True)
fashion_mnist_loader = torch.utils.data.DataLoader(dataset=fashion_mnist_dataset, batch_size=32, shuffle=True)

# Compute Reconstruction Error

mse_loss = nn.MSELoss()

model.eval()
with torch.no_grad():

  mnist_error = []
  for x, _ in test_loader:
    x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
    x_reconstructed, _, _ = model(x)
    error = mse_loss(x, x_reconstructed).item()
    mnist_error.append(error)

  fashion_mnist_error = []
  original_fmnist = []
  reconstructed_fmnist = []
  for x, _ in fashion_mnist_dataset:
    x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
    x_reconstructed, _, _ = model(x)
    error = mse_loss(x, x_reconstructed).item()
    fashion_mnist_error.append(error)
    original_fmnist.append(x.cpu())
    reconstructed_fmnist.append(x_reconstructed.cpu())

# Determine a threshold to classify an image as anomalous
mnist_error = np.array(mnist_error)
mean = np.mean(mnist_error)
sd = np.std(mnist_error)
Threshold = mean + 2*sd

fashion_mnist_error = np.array(fashion_mnist_error)
mean_fashion = np.mean(fashion_mnist_error)
sd_fashion = np.std(fashion_mnist_error)

# Threshold validation
from torch.utils.data.dataset import random_split
total_count = len(dataset)
val_count = int(0.1 * total_count) # 10 % for validation
train_count = total_count - val_count
train_dataset, val_dataset = random_split(dataset, [train_count, val_count])
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=32, shuffle=True)

model.eval()
correct_prediction = 0
total_prediction = 0
with torch.no_grad():
  for x, _ in val_loader:
    x = x.to(DEVICE).view(x.shape[0], INPUT_DIM)
    x_reconstructed, _, _ = model(x)
    error = mse_loss(x, x_reconstructed).item()
    if error < mean + 2*sd and error > mean - 2*sd:
      correct_prediction += 1
    total_prediction += 1

accuracy_validation  = correct_prediction / total_prediction
print('Validatiion accuracy:', accuracy_validation)

# Classify Images Using Threshold
fashion_clasification = 0
for error in fashion_mnist_error:
  if error < mean + 2*sd and error > mean - 2*sd:
    fashion_clasification += 1

accuracy_fashion = fashion_clasification / len(fashion_mnist_error)
print('Accuracy FashionMNIST:', accuracy_fashion)

# Visualization of anomaly detection

plt.figure(figsize=(20, 4))
n = 10 # Number of images to display
for i in range(n):
  ax = plt.subplot(2, n, i + 1)
  plt.imshow(original_fmnist[i].view(28, 28))
  plt.gray()
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)

  ax = plt.subplot(2, n, i + 1 + n)
  plt.imshow(reconstructed_fmnist[i].view(28, 28))
  plt.gray()
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
plt.show()

"""**Conditional detection**"""

!cp /content/drive/MyDrive/ml_proyectos/vae_model/vae_definition_conditional.py /content

from vae_definition_conditional import ConditionalVariationalAutoEncoder
# Define the path to the model file
model_path = '/content/drive/MyDrive/ml_proyectos/vae_model/vae_model_conditional.pth'

# Initialize the model (make sure to use the same parameters as the saved model)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_DIM = 784
H_DIM = 256
Z_DIM = 20
LABEL_DIM = 10
modelC = ConditionalVariationalAutoEncoder(INPUT_DIM, LABEL_DIM, H_DIM, Z_DIM)
BATCH_SIZE = 32

# Load the saved state dictionary into the model
modelC.load_state_dict(torch.load(model_path))

# Set the model to evaluation mode if not training further
modelC.eval()
modelC = modelC.to(DEVICE)

# Create One-Hot Labels

def one_hot(labels, num_classes=10):
  return torch.eye(num_classes)[labels].to(DEVICE)

# Prepare Conditional Inputs

one_hot_encodes = [one_hot(digit) for digit in range(10)]

# Generate Latent Vectors

n_samples = 10
random_latent_representations = torch.randn(n_samples, Z_DIM).to(DEVICE)

# Decode Combined Vectors

images_conditionated = []
modelC.eval()
with torch.no_grad():
  for one_hot_encode in one_hot_encodes:
    images_label = []
    for rand_lat_rep in random_latent_representations:
      rand_lat_rep = rand_lat_rep.view(1, -1).to(DEVICE)
      one_hot_encode = one_hot_encode.view(1, -1).to(DEVICE)
      image_gen = modelC.decode(rand_lat_rep, one_hot_encode)
      images_label.append(image_gen.cpu())
    images_conditionated.append(images_label)

# Visualize and Assess

plt.figure(figsize=(20, 20))
for i in range(10):
  for j in range(n_samples):
    ax = plt.subplot(10, n_samples, 1 + i + j*n)
    plt.imshow(images_conditionated[j][i].view(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.savefig('conditional.png', bbox_inches = 'tight')
plt.show()