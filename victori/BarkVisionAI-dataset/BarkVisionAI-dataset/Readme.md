  # BarkVisionAI: Dataset for Tree Species Identification with AI

Tree species identification and mapping is crucial for forest management, biodiversity conservation, and ecological research. Bark images can be captured easily from the ground level and can provide vast amounts of information about the tree species and its health. Yet, existing datasets for tree bark images are often limited in scope, lacking diversity in species representation and temporal attributes.

To address these limitations, we present **BarkVisionAI**, a comprehensive dataset of **167,361 tree bark images** representing **13 species** collected from diverse forests across India. Each image is meticulously labeled with:

- **Species Name**
- **Device Attributes**
- **Timestamp**

This dataset provides a robust foundation for:

- Studying species identification
- Analyzing variability in bark characteristics
- Supporting ecological research
- Training machine learning models
- Conducting environmental monitoring

## Key Features
- **Diversity**: Images collected from multiple forests across India, representing a wide variety of species and ecological conditions.
- **Metadata**: Detailed metadata for each image, enabling rich analytical possibilities.
- **Scale**: A large dataset with 167,361 images, ensuring comprehensive representation.
- **Utility**: Suitable for a range of applications, including automated tree species identification and monitoring environmental changes.

## Applications
1. **Ecological Research**: Gain insights into tree species distribution and bark variability.
2. **Machine Learning**: Train and benchmark AI models for tree species classification.
3. **Environmental Monitoring**: Detect and monitor environmental changes through bark condition analysis.

## Benchmarking
Benchmarking experiments using standard image classification models demonstrate the dataset’s utility and effectiveness. These results highlight its potential as a valuable resource for developing robust, real-world applications in automated tree species identification and environmental change monitoring.

---

## Trained Models
We have trained several models on the BarkVisionAI dataset. The details of these models, along with their performance metrics and downloadable resources, are provided below:

| Model Name       | Accuracy (%) | Model Weights                                                                 | Confusion Matrix Download Link                                 |
|------------------|--------------|-------------------------------------------------------------------------------|---------------------------------|
| ResNet18         | 88.07         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet18/resnet18.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/Resnet18.png)    |
| ResNet34  | 87.66         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet34/resnet34.pth)                      | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/Resnet34.png)|
| ResNet50      | 89.88         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet50/resnet50.pth)                         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/Resnet50.png) |
| VGG16      | 85.65         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/VGG16/VGG16.pth)                         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/VGG16.png) |
| EfficientNetB0         | 90.70        | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/EfficientNetB0/EfficientNetB0.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/EfficientNetB0.png)    |
| NvidiaEfficientNetB4         | 90.47        | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/NvidiaEfficientNetB4/NvidiaEfficientNetB4.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/NvidiaEfficientNetB4.png)    |

To reproduce the results you can download the [metadata csv](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/training-data/metadata.csv) file which provides detailed information about the images used during training, including species names, timestamps, and device attributes.


### BarkNet 1.0 Dataset
We also trained the same models with a subset of **200 images** representing **3 different species** from the BarkNet 1.0 dataset:
- **Abies balsamea**
- **Tsuga canadensis**
- **Quercus rubra**

The results are summarized below:

| Model Name       | Accuracy (%) | Model Weights                                                                 | Confusion Matrix Download Link                                 |
|------------------|--------------|-------------------------------------------------------------------------------|--------------------------------------------------------------|
| ResNet18         | 86.11         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/Barknet+Trained+Models/resnet18/resnet18+.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/Resnet18_barknet.png)    |
| ResNet34  | 79.37         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/Barknet+Trained+Models/resnet34/resnet34.pth)                      | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/Resnet34_barknet.png)|
| ResNet50      | 89.53         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/Barknet+Trained+Models/resnet50/resnet50.pth)                         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/Resnet50_barknet.png) |
| VGG16      | 89.06         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/Barknet+Trained+Models/VGG16/VGG16.pth)                         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/VGG16_barknet.png) |
| EfficientNetB0         | 94.37        | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/Barknet+Trained+Models/EfficientNetB0/EfficientNetB0.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/EfficientNetB0_barknet.png)    |
| NvidiaEfficientNetB4         | 93.75        | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/Barknet+Trained+Models/NvidiaEfficientNetB4/NvidiaEfficientNetB4.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/confusion+matrix/NvidiaEfficientNetB4_barknet.png)    |


## Get Started
This GitHub repository provides tools to train and test models using the BarkVisionAI dataset. By modifying the configuration file, users can:

- Specify the dataset path.
- Select model architectures.
- Set hyperparameters like learning rate, batch size, and epochs.

## Acknowledgments

We thank all contributors and collaborators who helped in the creation and validation of the [BarkVisionAI dataset](#).


