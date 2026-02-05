import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score
import numpy as np
import os


def plot_confusion_matrix(val_labels, val_preds, full_dataset,model_name):
    conf_matrix = confusion_matrix(val_labels, val_preds)
    class_names = full_dataset.classes 

    plt.figure(figsize=(10, 8))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    output_path = '../trained_models/prod/'
    os.makedirs(output_path, exist_ok=True)
    filename = f'{model_name}_confusion_matrix.png'
    plt.savefig(os.path.join(output_path, filename))
    plt.show()
    plt.close()
