import torch
import torch.nn as nn
from torchvision import transforms,models
from PIL import Image
import os
import configparser
from prepare_model import prepare_model

config = configparser.ConfigParser()
config.read('../config.ini')
model_name = config['models']['MODEL'].strip()
number_of_classes = int(config['models']['NUM_CLASSES'])
prediction_model = config['prediction']['PREDICTION_MODEL'].strip()
test_class_prediction = int(config['prediction']['TEST_CLASS'])
pretrained = config['models']['PRETRAINED']

model = prepare_model(model_name, number_of_classes,pretrained)
prediction_model_path = '../trained_models/prod/resnet50/' + prediction_model
model.load_state_dict(torch.load(prediction_model_path))
model.eval() 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.RandomHorizontalFlip(),
])


def preprocess_image(image_path):
    image = Image.open(image_path).convert('RGB')  
    image = transform(image) 
    image = image.unsqueeze(0) 
    return image.to(device)

false_predictions = []
true_counts=0
test_class=test_class_prediction
for image in os.listdir(f'../test-data/{test_class}/'): 
    image_path = f'../test-data/{test_class}/' + image
    image = preprocess_image(image_path)
    with torch.no_grad():
        outputs = model(image)
        _, predicted = outputs.max(1)
        predicted_label = predicted.item()
        if predicted_label == test_class :
            true_counts+=1
        else :
            false_predictions.append(predicted_label)
print('Total  : ', true_counts+ len(false_predictions), 'True Predictions:', true_counts, 'False Predictions: ', len(false_predictions), 'False Predictions : ', false_predictions)