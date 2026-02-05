from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split

def prepare_data_loader(data_dir, batch_size):    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.RandomHorizontalFlip(),
    ])
    dataset = datasets.ImageFolder(data_dir, transform=transform)   
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)