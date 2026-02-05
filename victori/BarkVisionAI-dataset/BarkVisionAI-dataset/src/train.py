import configparser
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from prepare_model import prepare_model
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score
import numpy as np
import sys
import os
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.confusion_matrix import plot_confusion_matrix


config = configparser.ConfigParser()
config.read('../config.ini')
model_name = config['models']['MODEL'].strip()
pretrained = config['models']['PRETRAINED']
number_of_classes = int(config['models']['NUM_CLASSES'])
dataset_path = config['data']['DATASET_PATH'].strip()
train_split = float(config['training']['TRAIN_SPLIT'])
test_split = float(config['training']['TEST_SPLIT'])
learning_rate = float(config['training']['LR'])
weight_decay = float(config['training']['WEIGHT_DECAY'])
number_of_epochs = int(config['training']['N_EPOCHS'])
batch_size = int(config['training']['BATCH_SIZE'])
print(f"training with these variables\n"
    f"model_name: {model_name}\n"
      f"pretrained: {pretrained}\n"
      f"number_of_classes: {number_of_classes}\n"
      f"dataset_path: {dataset_path}\n"
      f"train_split: {train_split}\n"
      f"test_split: {test_split}\n"
      f"learning_rate: {learning_rate}\n"
      f"weight_decay: {weight_decay}\n"
      f"number_of_epochs: {number_of_epochs}\n"
      f"batch_size: {batch_size}")
model = prepare_model(model_name, number_of_classes, pretrained)
if model is None:
    raise ValueError(
        "prepare_model() returned None. Check model_name, number_of_classes, and pretrained parameters."
    )
# print("model",model)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
     transforms.RandomHorizontalFlip(),
])


full_dataset = datasets.ImageFolder(root=dataset_path, transform=transform)
train_ratio = train_split
val_ratio = test_split
train_size = int(train_ratio * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])


train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)  
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device info : " ,device)
model.to(device)


def train_model(model, train_loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
    
    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


def validate_model(model, val_loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc, all_preds, all_labels


def start_training(num_epochs): 
    for epoch in range(num_epochs):
        current_time = datetime.datetime.now()
        print(f" started the epoch {epoch+1}/{num_epochs} at current time: {current_time}")
        train_loss, train_acc = train_model(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_preds, val_labels = validate_model(model, val_loader, criterion, device)
        
        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"Train Loss: {train_loss:.4f}, Train Accuracy: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val Accuracy: {val_acc:.4f}")
        # print(f"{val_labels,val_preds}")


start_training(number_of_epochs)
val_loss, val_acc, val_preds, val_labels = validate_model(model, val_loader, criterion, device)
plot_confusion_matrix(val_labels, val_preds, full_dataset,model_name)
model_save_path = f'{model_name}.pth'
try:
    torch.save(model.state_dict(), model_save_path)
    print(f'Model saved to {model_save_path}')
except Exception as e:
    print(f'Error saving the model: {e}')
print('closing the training')
