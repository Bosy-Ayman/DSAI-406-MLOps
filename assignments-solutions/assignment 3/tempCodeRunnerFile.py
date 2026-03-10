import kagglehub
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import os
import mlflow
import mlflow.pytorch

device = torch.device("cpu")
print(f"Training on: {device}")

epochs = 3
batch_size = 128
lr = 0.0002
latent_dim = 100


mlflow.set_experiment("Assignment3_Bosy")

with mlflow.start_run():

    mlflow.log_param("epochs", epochs)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("learning_rate", lr)
    mlflow.log_param("latent_dim", latent_dim)

    mlflow.set_tag("student_id", "202202076")

    dataset_path = kagglehub.dataset_download("datamunge/sign-language-mnist")
    csv_file = os.path.join(dataset_path, "sign_mnist_train.csv")

    df = pd.read_csv(csv_file)

    features = df.drop('label', axis=1).values

    real_images = torch.tensor(features).float()

    real_images = (real_images - 127.5) / 127.5

    real_images = real_images.view(-1,1,28,28)

    dataloader = torch.utils.data.DataLoader(
        real_images,
        batch_size=batch_size,
        shuffle=True
    )
    class Generator(nn.Module):

        def __init__(self):
            super().__init__()

            self.fc = nn.Linear(latent_dim,256*7*7)

            self.conv = nn.Sequential(

                nn.BatchNorm2d(256),

                nn.ConvTranspose2d(
                    256,128,
                    kernel_size=4,
                    stride=2,
                    padding=1
                ),

                nn.BatchNorm2d(128),

                nn.ReLU(True),

                nn.ConvTranspose2d(
                    128,1,
                    kernel_size=4,
                    stride=2,
                    padding=1
                ),

                nn.Tanh()
            )

        def forward(self,x):

            x = self.fc(x)

            x = x.view(-1,256,7,7)

            return self.conv(x)

    class Discriminator(nn.Module):

        def __init__(self):
            super().__init__()

            self.conv = nn.Sequential(

                nn.Conv2d(
                    1,64,
                    kernel_size=4,
                    stride=2,
                    padding=1
                ),

                nn.LeakyReLU(0.2, inplace=True),

                nn.Conv2d(
                    64,128,
                    kernel_size=4,
                    stride=2,
                    padding=1
                ),

                nn.BatchNorm2d(128),

                nn.LeakyReLU(0.2, inplace=True),
            )

            self.fc = nn.Sequential(

                nn.Linear(128*7*7,1),

                nn.Sigmoid()
            )


        def forward(self,x):

            x = self.conv(x)

            x = x.view(-1,128*7*7)

            return self.fc(x)

    gen = Generator().to(device)

    disc = Discriminator().to(device)

    opt_g = optim.Adam(
        gen.parameters(),
        lr=lr,
        betas=(0.5,0.999)
    )

    opt_d = optim.Adam(
        disc.parameters(),
        lr=lr,
        betas=(0.5,0.999)
    )

    criterion = nn.BCELoss()
    
    for epoch in range(epochs):

        epoch_loss_d = 0.0

        epoch_loss_g = 0.0

        for i,real_batch in enumerate(dataloader):

            batch_size = real_batch.size(0)

            real_batch = real_batch.to(device)

            real_labels = torch.ones(batch_size,1).to(device)

            fake_labels = torch.zeros(batch_size,1).to(device)

            # -----------------
            # Train Discriminator
            # -----------------
            opt_d.zero_grad()

            out_real = disc(real_batch)

            loss_real = criterion(out_real,real_labels)

            noise = torch.randn(batch_size,latent_dim).to(device)

            fake_imgs = gen(noise)

            out_fake = disc(fake_imgs.detach())

            loss_fake = criterion(out_fake,fake_labels)

            loss_d = loss_real + loss_fake

            loss_d.backward()

            opt_d.step()

            # -----------------
            # Train Generator
            # -----------------
            opt_g.zero_grad()

            out_g = disc(fake_imgs)

            loss_g = criterion(out_g,real_labels)

            loss_g.backward()

            opt_g.step()

            epoch_loss_d += loss_d.item()

            epoch_loss_g += loss_g.item()

        avg_loss_d = epoch_loss_d / len(dataloader)

        avg_loss_g = epoch_loss_g / len(dataloader)

        print(
            f"Epoch [{epoch+1}/{epochs}] | "
            f"Loss D: {avg_loss_d:.4f} | "
            f"Loss G: {avg_loss_g:.4f}"
        )

        # -----------------------------
        # MLflow logging
        # -----------------------------
        mlflow.log_metric("discriminator_loss",avg_loss_d,step=epoch)

        mlflow.log_metric("generator_loss",avg_loss_g,step=epoch)

    # -----------------------------
    # Generate images
    # -----------------------------
    test_noise = torch.randn(16,latent_dim).to(device)

    final_fakes = gen(test_noise).detach().cpu()

    fig,axes = plt.subplots(4,4,figsize=(6,6))

    for i,ax in enumerate(axes.flatten()):

        img = final_fakes[i].view(28,28)*0.5 + 0.5

        ax.imshow(img.numpy(),cmap='gray')

        ax.axis('off')

    plt.tight_layout()

    plt.savefig("gan_output.png")

    print("Saved output image to gan_output.png")

    # -----------------------------
    # Log artifacts
    # -----------------------------
    mlflow.log_artifact("gan_output.png")

    # Save models
    mlflow.pytorch.log_model(gen,"generator_model")

    mlflow.pytorch.log_model(disc,"discriminator_model")