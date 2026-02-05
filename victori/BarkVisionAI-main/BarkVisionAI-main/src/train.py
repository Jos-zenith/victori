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
from torchvision.utils import save_image
from tqdm import tqdm
import datetime
import matplotlib.pyplot as plt


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.confusion_matrix import plot_confusion_matrix


config = configparser.ConfigParser()
config.read('../config.ini')

model_name = config['models']['MODEL'].strip()
pretrained = config.getboolean('models', 'PRETRAINED')
number_of_classes = int(config['models']['NUM_CLASSES'])
dataset_path = config['data']['DATASET_PATH'].strip()
train_split = float(config['training']['TRAIN_SPLIT'])
test_split = float(config['training']['TEST_SPLIT'])
val_split = float(config['training']['VAL_SPLIT'])
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
model = prepare_model(model_name, number_of_classes,pretrained)
# print("model",model)
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(
        brightness=0.2, contrast=0.2, saturation=0.2, hue=0.02
    ),
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    )
])

# Validation/Test transforms (no augmentation)
eval_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    )
])

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

# Improved ImageFolderWithPaths that works with random_split
class ImageFolderWithPaths(datasets.ImageFolder):
    def __getitem__(self, index):
        original_tuple = super().__getitem__(index)
        path = self.imgs[index][0]
        return original_tuple + (path,)
    
    def __len__(self):
        return super().__len__()

# Enhanced save_classified_images function
def save_classified_images(model, dataloader, device, output_dir, phase='test', class_names=None):
    """Save correctly classified and misclassified images with proper organization.
    
    Args:
        model: Trained model
        dataloader: DataLoader with images and paths
        device: Device to run inference on
        output_dir: Base output directory
        phase: 'val' or 'test' phase
        class_names: List of class names for readable folder names
    """
    try:
        model.eval()
        phase_dir = os.path.join(output_dir, phase)
        os.makedirs(phase_dir, exist_ok=True)
        
        # Create directories
        correct_dir = os.path.join(phase_dir, 'correct')
        misclassified_dir = os.path.join(phase_dir, 'misclassified')
        print("saving image",correct_dir,misclassified_dir)
        for dir_path in [correct_dir, misclassified_dir]:
            os.makedirs(dir_path, exist_ok=True)
            if not os.path.exists(dir_path):
                raise RuntimeError(f"Failed to create directory: {dir_path}")

        with torch.no_grad():
            for images, labels, paths in tqdm(dataloader, desc=f"Saving {phase} images"):
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)

                for img, label, pred, path in zip(images, labels, preds, paths):
                    # Get class names if available
                    true_class = class_names[label.item()] if class_names else str(label.item())
                    pred_class = class_names[pred.item()] if class_names else str(pred.item())
                    
                    # Create descriptive filename
                    filename = os.path.basename(path)
                    save_name = f"true_{true_class}_pred_{pred_class}_{filename}"
                    
                    # Save to appropriate directory
                    save_dir = correct_dir if label == pred else misclassified_dir
                    save_path = os.path.join(save_dir, save_name)
                    
                    # Denormalize and save
                    img = denormalize(img.cpu())
                    save_image(img, save_path)
                    
    except Exception as e:
        print(f"Error saving classified images: {e}")
        raise

def denormalize(tensor):
    """Reverse the normalization applied to images with proper device handling."""
    device = tensor.device
    mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225], device=device).view(3, 1, 1)
    return tensor * std + mean

# Then use this class for your dataset

full_dataset = ImageFolderWithPaths(
    root=dataset_path, 
    transform=None  # We'll handle this differently
)
 
if not os.path.exists(dataset_path):
    raise ValueError(f"Dataset path does not exist: {dataset_path}")

if not (0 < train_split < 1) or not (0 < val_split < 1) or not (0 < test_split < 1):
    raise ValueError("Train/val/test splits must be between 0 and 1")

if train_split + val_split + test_split != 1.0:
    print("Warning: Train/val/test splits don't sum to 1.0 - normalizing...")
    total = train_split + val_split + test_split
    train_split /= total
    val_split /= total
    test_split /= total
train_ratio = train_split
val_ratio = val_split 
total_size = len(full_dataset)
train_size = int(train_split * total_size)
val_size = int(val_split * total_size)
test_size = total_size - train_size - val_size  

train_dataset, val_dataset, test_dataset = random_split(
    full_dataset, [train_size, val_size, test_size],
    generator=torch.Generator().manual_seed(42)
)

# 3. Create new transform-applying datasets
class TransformSubset(torch.utils.data.Dataset):
    def __init__(self, subset, transform=None):
        self.subset = subset
        self.transform = transform
        
    def __getitem__(self, index):
        img, label, path = self.subset[index]
        if self.transform:
            img = self.transform(img)
        return img, label, path
        
    def __len__(self):
        return len(self.subset)

# 4. Apply transforms to each subset
train_dataset = TransformSubset(train_dataset, transform=train_transform)
val_dataset = TransformSubset(val_dataset, transform=eval_transform)
test_dataset = TransformSubset(test_dataset, transform=eval_transform)


# Create dataloaders as before
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, 
                         num_workers=4, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False,
                       num_workers=4, pin_memory=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False,
                        num_workers=4, pin_memory=True)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)  
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device info : " ,device)
model.to(device)
 

def adjust_learning_rate(optimizer, epoch):
    """
    Custom LR schedule:
    - Epochs 0–1: 1e-4
    - Epochs 2–3: 1e-5
    - Epoch 4 onwards: 1e-6
    """
    if epoch < 3:
        new_lr = 1e-4
    elif epoch < 5:
        new_lr = 1e-5
    else:
        new_lr = 1e-6

    for param_group in optimizer.param_groups:
        param_group['lr'] = new_lr
    print(f"Learning rate adjusted to: {new_lr:.6f}")



def train_model(model, train_loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for batch in train_loader:
        # Handle both (img, label) and (img, label, path) cases
        inputs = batch[0].to(device)
        labels = batch[1].to(device)

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
        for batch in val_loader:
            inputs = batch[0].to(device)
            labels = batch[1].to(device)

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

def test_model(model, test_loader, criterion, device):
    model.eval()
    test_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            inputs = batch[0].to(device)
            labels = batch[1].to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            test_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    avg_loss = test_loss / total
    accuracy = correct / total
    return avg_loss, accuracy, all_preds, all_labels

def start_training(num_epochs, patience=5,base_lr=learning_rate ):
    train_losses, val_losses = [], []
    train_accuracies, val_accuracies = [], []

    best_val_loss = float('inf')
    epochs_without_improvement = 0
    best_model_state = None

    # Set the initial learning rate
    for param_group in optimizer.param_groups:
        param_group['lr'] = base_lr

    for epoch in range(num_epochs):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\nStarted epoch {epoch+1}/{num_epochs} at: {current_time}")

        # Adjust learning rate after epoch 3
        adjust_learning_rate(optimizer, epoch)

        train_loss, train_acc = train_model(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_preds, val_labels = validate_model(model, val_loader, criterion, device) 
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accuracies.append(train_acc)
        val_accuracies.append(val_acc)

        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"Train Loss: {train_loss:.4f}, Train Accuracy: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val Accuracy: {val_acc:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_without_improvement = 0
            best_model_state = model.state_dict()
            os.makedirs("../v1/models_output", exist_ok=True)
            torch.save({
                'model_state_dict': best_model_state,
                'class_names': full_dataset.classes,
                'epoch': epoch + 1,
                'val_loss': best_val_loss,
                'train_accuracy': train_acc,
                'val_accuracy': val_acc
            }, f"../v1/models_output/best_{model_name}.pth")

        else:
            epochs_without_improvement += 1
            print(f"No improvement for {epochs_without_improvement} epoch(s).")

        if epochs_without_improvement >= patience:
            print(f"\nEarly stopping at epoch {epoch+1} due to no improvement in validation loss for {patience} consecutive epochs.")
            break

    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    return train_losses, val_losses, train_accuracies, val_accuracies

def plot_loss_vs_epochs(train_loss, val_loss):
    epochs = range(len(train_loss))  # match actual number of epochs
    plt.plot(epochs, train_loss, label='Train Loss', marker='o', color='blue')
    plt.plot(epochs, val_loss, label='Val Loss', marker='o', color='orange')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Loss vs Epochs')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    try:
        # Get class names
        class_names = full_dataset.classes
         
        train_losses, val_losses, train_acc, val_acc = start_training(number_of_epochs)
         
        val_loss, val_acc, val_preds, val_labels = validate_model(model, val_loader, criterion, device)
        print(f"\nFinal Validation Results:")
        print(f"Loss: {val_loss:.4f}, Accuracy: {val_acc:.4f}")
        
        # 3. Save validation images (using the validation results we just got)
        save_classified_images(model, val_loader, device, 'classified_images',
                             phase='val', class_names=class_names)
        
        # 4. Final test evaluation
        test_loss, test_acc, test_preds, test_labels = test_model(model, test_loader, criterion, device)
        print(f"\nTest Results:")
        print(f"Loss: {test_loss:.4f}, Accuracy: {test_acc:.4f}")
        
        # 5. Save test images
        save_classified_images(model, test_loader, device, 'classified_images',
                             phase='test', class_names=class_names)
        
        # 6. Plot results
        plot_loss_vs_epochs(train_losses, val_losses)
        plot_confusion_matrix(val_labels, val_preds, class_names, model_name)

        final_model_path = f'../v1/models_output/{model_name}.pth'
        
        
        # 7. Save model
        model_save_path = f'../v1/models_output/{model_name}.pth'
        os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
        torch.save({
            'model_state_dict': model.state_dict(),
            'class_names': class_names,
            'val_accuracy': val_acc,
            'test_accuracy': test_acc
        }, model_save_path)
        
    except Exception as e:
        print(f"Error during execution: {e}")
        sys.exit(1) 