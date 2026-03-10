import kagglehub
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import os
import mlflow
import mlflow.pytorch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on: {device}")

# Set MLflow tracking URI and Experiment exactly once
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Assignment3_Bosy")

def train_classifier(run_name, epochs, batch_size, lr):
    with mlflow.start_run(run_name=run_name):
        
        # 1. Log Parameters & Tags
        mlflow.log_param("epochs", epochs)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("learning_rate", lr)
        mlflow.set_tag("student_id", "202202076")
        mlflow.set_tag("model_type", "CNN_Classifier")

        # 2. Load Dataset (Extracting Labels this time)
        dataset_path = kagglehub.dataset_download("datamunge/sign-language-mnist")
        csv_file = os.path.join(dataset_path, "sign_mnist_train.csv")
        df = pd.read_csv(csv_file)
        
        # Get labels and features
        labels = torch.tensor(df['label'].values).long()
        features = df.drop('label', axis=1).values
        
        # Normalize to [0, 1] and reshape to (Channels, Height, Width)
        images = torch.tensor(features).float() / 255.0
        images = images.view(-1, 1, 28, 28)

        dataset = torch.utils.data.TensorDataset(images, labels)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # 3. Define a Simple CNN Classifier
        class SimpleCNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv = nn.Sequential(
                    nn.Conv2d(1, 32, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(32, 64, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2)
                )
                self.fc = nn.Sequential(
                    nn.Linear(64 * 7 * 7, 128),
                    nn.ReLU(),
                    nn.Linear(128, 26) # 26 possible classes in Sign Language
                )

            def forward(self, x):
                x = self.conv(x)
                x = x.view(x.size(0), -1)
                return self.fc(x)

        model = SimpleCNN().to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=lr)
        
        print(f"--- Starting Run: {run_name} | LR: {lr} | Batch: {batch_size} ---")
        
        # 4. Training Loop with Live Logging
        for epoch in range(epochs):
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0

            for batch_images, batch_labels in dataloader:
                batch_images, batch_labels = batch_images.to(device), batch_labels.to(device)

                optimizer.zero_grad()
                outputs = model(batch_images)
                loss = criterion(outputs, batch_labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item() * batch_images.size(0)
                
                # Calculate Accuracy
                _, predicted = torch.max(outputs.data, 1)
                total += batch_labels.size(0)
                correct += (predicted == batch_labels).sum().item()

            epoch_loss = running_loss / total
            epoch_acc = correct / total

            # MLflow Live Logging at the end of every epoch!
            mlflow.log_metric("loss", epoch_loss, step=epoch)
            mlflow.log_metric("accuracy", epoch_acc, step=epoch)
            
            print(f"Epoch [{epoch+1}/{epochs}] - Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.4f}")

        # 5. Log Model Artifacts
        mlflow.pytorch.log_model(model, "cnn_model")
        print(f"Finished {run_name}.\n")

# 6. Execute 5 Runs
experiments = [
    {"run_name": "Run_1_Baseline", "epochs": 5, "batch_size": 128, "lr": 0.001},
    {"run_name": "Run_2_High_LR", "epochs": 5, "batch_size": 128, "lr": 0.05},
    {"run_name": "Run_3_Low_LR", "epochs": 5, "batch_size": 128, "lr": 0.0001},
    {"run_name": "Run_4_Small_Batch", "epochs": 5, "batch_size": 32, "lr": 0.001},
    {"run_name": "Run_5_Large_Batch", "epochs": 5, "batch_size": 512, "lr": 0.001},
]

for exp in experiments:
    train_classifier(**exp)