  # BarkVisionAI: Novel dataset for rapid tree species identification

Tree species identification and mapping is crucial for forest management, biodiversity conservation, and ecological research. Bark images can be captured easily from the ground level and can provide vast amounts of information about the tree species and its health. Yet, existing datasets for tree bark images are often limited in scope, lacking diversity in species representation and temporal attributes.

To address these limitations, we present **BarkVisionAI**, a comprehensive dataset of **156,001 tree bark images** representing **13 species** collected from diverse forests across India. Each image is meticulously labeled with:

- **Species Name**
- **Device Attributes**
- **Location**
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
- **Scale**: A large dataset with 156,001 images, ensuring comprehensive representation.
- **Utility**: Suitable for a range of applications, including automated tree species identification and monitoring environmental changes.

## Geographical Distribution of BarkVisionAI Dataset
To illustrate the diversity of our dataset, we have mapped the **geographical distribution** of bark image collection sites across India. The BarkVisionAI dataset spans multiple **eco-regions** ensuring representation across varied ecological conditions.

- **Distribution of tree locations collected in Himachal Pradesh**

![Himachal Pradesh Species Distribution](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/distribution+map/Himachal+Pradesh+Species+Distribution.png)

- **Distribution of tree locations collected in Odisha**

![Odisha Species Distribution](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/distribution+map/Odisha+Species+Distribution.png)

- **Ecoregion-wise tree species count**

   This table presents the point counts for key tree species across various Ecoregions. The counts reflect the abundance of each species within the specified ecoregion.

| Ecoregion | *Shorea robusta* | *Madhuca longifolia* | *Buchanania lanzan* | *Senegalia catechu* | *Rhododendron arboreum* | *Pinus roxburghii* | *Mangifera sylvatica* | *Eucalyptus globulus* | *Phyllanthus emblica* | *Taxus baccata* | *Aesculus indica* | *Cedrus deodara* | *Quercus leucotrichophora* | **Total Count** |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Himalayan subtropical pine forests | 228 | 0 | 0 | 11,177 | 2,413 | 25,282 | 2,125 | 2,600 | 3,525 | 1,313 | 552 | 6,612 | 5,019 | **60,846** |
| Northwestern Himalayan alpine shrub and meadow | 1 | 0 | 0 | 2 | 41 | 170 | 0 | 0 | 0 | 126 | 759 | 569 | 9 | **1,677** |
| WS Northwestern thorn scrub forests | 13,253 | 0 | 0 | 3,110 | 0 | 3,496 | 461 | 3,301 | 260 | 3 | 4 | 1 | 122 | **24,011** |
| Upper Gangetic Plains moist deciduous forests | 1,396 | 0 | 0 | 908 | 0 | 0 | 22 | 462 | 20 | 0 | 0 | 0 | 0 | **2,808** |
| Western Himalayan broadleaf forests | 2 | 0 | 0 | 7,833 | 2,232 | 11,502 | 2,105 | 1,841 | 2,457 | 1,356 | 2,804 | 13,450 | 1,335 | **46,917** |
| Western Himalayan subalpine conifer forests | 0 | 0 | 0 | 0 | 33 | 1 | 1 | 0 | 0 | 57 | 114 | 1 | 0 | **207** |
| Chhota-Nagpur dry deciduous forests | 468 | 1 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **482** |
| Eastern highlands moist deciduous forests | 5,997 | 5,318 | 2,299 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **13,614** |
| Northern dry deciduous forests | 3,623 | 765 | 1,051 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5,439** |
| &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| 24,968 | 6,084 | 3,363 | 23,030 | 4,719 | 40,451 | 4,714 | 8,204 | 6,262 | 2,855 | 4,233 | 20,633 | 4,685 | **156,001** |

## Temporal Distribution of BarkVisionAI Dataset 
![Collected Species Distribution](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/distribution+map/Months+Distribution.png)

![Collected Species Distribution](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/distribution+map/Daytime+Distribution.png)


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
| ResNet18         | 84.90         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet18/best_resnet18.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet18/resnet18_confusion_matrix.png)    |
| ResNet34  | 86.42         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet34/best_resnet34.pth)                      | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet34/resnet34_confusion_matrix.png)|
| ResNet50      | 87.42         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet50/best_resnet50.pth)                         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet50/resnet50_confusion_matrix.png) |
| VGG16      | 80.45         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/VGG16/best_VGG16.pth)                         | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/VGG16/VGG16_confusion_matrix.png) |
| EfficientNetB0         | 83.96        | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/EfficientNetB0/best_EfficientNetB0.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/EfficientNetB0/EfficientNetB0_confusion_matrix.png)    |
| NvidiaEfficientNetB4         | 72.17        | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/NvidiaEfficientNetB4/best_NvidiaEfficientNetB4.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/NvidiaEfficientNetB4/NvidiaEfficientNetB4_confusion_matrix.png)    |
| VIT Based Model (vit_base_patch14_reg4_dinov2.lvd142m)      | 85.03        | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/VIT_based_model/best_CustomViT.pth)                            | [Download](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/VIT_based_model/confusion_matrix.png)    |

To reproduce the results you can download the [metadata csv](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/training-data/metadata.csv) file which provides detailed information about the images used during training, including species names, timestamps, and device attributes.

## Model Analysis: ResNet50 (Best Performing Model)
Among all trained architectures, **ResNet50** achieved an overall accuracy of 87.42%, with 7,956 correct predictions out of 9,100 samples. A detailed breakdown of model performance across temporal and environmental conditions reveals important insights:  

| Metric              | Value  |
|----------------------|--------|
| Correct Predictions  | 7,956  |
| Incorrect Predictions| 1,144  |
| Total Predictions    | 9,100  |
| **Accuracy**         | **87.42%** |


### **Confusion Matrix**
The confusion matrix below illustrates inter-class prediction accuracy for ResNet50.
![ResNet50 Confusion Matrix](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/models/resnet50/resnet50_confusion_matrix.png)

### Misclassification Rate by Time of Day 
The highest misclassification rate was observed during the evening, while morning and afternoon rates remained consistently lower and similar. This suggests that diminished natural light during evening hours may have affected image quality, leading to reduced feature clarity and increased prediction errors. The model performed more reliably when lighting was relatively stable, as seen during morning and afternoon periods. 

![Misclassification Rate by Time of Day](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/resnet50+analysis/misclassification+by+time+of+the+day.png)

### Misclassification Rate by Elevation:  
The model performed better at low altitudes, with misclassification rates increasing at medium and high elevations. This may be due to greater species overlap and environmental variability at higher elevations, which introduces complexity in visual patterns.

![Misclassification Rate by Elevation](https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/resnet50+analysis/misclassification+by+elevation.png)

### Accuracy by Month and Time of Day  

Model accuracy varied across both months and times of day, with clear patterns influenced by environmental and lighting conditions:  

- **Peak Accuracy** was observed in *September*, particularly during the *evening* and *morning* (both **92%**).  
- **December** showed perfect accuracy (**100%**) across all time slots; however, this is due to an extremely small sample size (n=6).  
- **Midday (Afternoon)** generally resulted in higher accuracy compared to morning or evening in most months, likely due to better and more consistent lighting.  
- **Lower Accuracy** was seen in *October mornings* (79%) and *April evenings* (81%), both of which also had relatively fewer images, potentially contributing to less robust performance.  

<p align="center">
  <img src="https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/resnet50+analysis/Accuracy+by+month+and+time+of+day.png" alt="Accuracy by month and time of day" width="48%">
  <img src="https://iofe-greenbase-bucket.s3.us-east-1.amazonaws.com/nCount/released-data-models/resnet50+analysis/Image+Count+by+month+and+time+of+day.png" alt="Image Count by month and time of day" width="48%">
</p>

 

## Get Started
This GitHub repository provides tools to train and test models using the BarkVisionAI dataset. By modifying the configuration file, users can:

- Specify the dataset path.
- Select model architectures.
- Set hyperparameters like learning rate, batch size, and epochs.

## Acknowledgments

We thank all contributors and collaborators who helped in the creation and validation of the [BarkVisionAI dataset](https://zenodo.org/records/14650999).







