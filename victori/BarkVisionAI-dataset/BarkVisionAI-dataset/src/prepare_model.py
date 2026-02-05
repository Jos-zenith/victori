import torch.nn as nn
from torchvision import models
from efficientnet_pytorch import EfficientNet
from torchvision.models import efficientnet_b4

def prepare_model(model_name,number_of_classes,pretrained):
    print(f"prepare_model called with model_name: {model_name}, number_of_classes: {number_of_classes}", f"pretrained: {pretrained}")
    if model_name == 'resnet18':
        print('Preparing ResNet18 model')
        class ResNet18(nn.Module):
            def __init__(self, num_classes=number_of_classes, pretrained=pretrained):
                super(ResNet18, self).__init__()
                self.model = models.resnet18(pretrained=pretrained)
                self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
                self.model.conv1.weight.requires_grad = False

            def forward(self, x):
                return self.model(x)

        num_classes = number_of_classes
        model = ResNet18(num_classes=num_classes, pretrained=pretrained)
        return model
    elif model_name == 'resnet34':
        print('Preparing ResNet34 model')
        class ResNet34(nn.Module):
            def __init__(self, num_classes=number_of_classes, pretrained=pretrained):
                super(ResNet34, self).__init__()
                self.model = models.resnet34(pretrained=pretrained)
                self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
                self.model.conv1.weight.requires_grad = False

            def forward(self, x):
                return self.model(x)

        num_classes = number_of_classes
        model = ResNet34(num_classes=num_classes, pretrained=pretrained)
        return model
    elif model_name == 'resnet50':
        print('Preparing ResNet50 model')
        class ResNet50(nn.Module):
            def __init__(self, num_classes=number_of_classes, pretrained=pretrained):
                super(ResNet50, self).__init__()
                self.model = models.resnet50(pretrained=pretrained)
                self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
                self.model.conv1.weight.requires_grad = False

            def forward(self, x):
                return self.model(x)

        num_classes = number_of_classes
        model = ResNet50(num_classes=num_classes, pretrained=pretrained)
        return model
    elif model_name == 'VGG16':
        print('Preparing VGG16 model')
        class VGG16(nn.Module):
            def __init__(self, num_classes, pretrained=pretrained):
                super(VGG16, self).__init__()
                self.model = models.vgg16(pretrained=pretrained)
                
                for param in list(self.model.features.children())[0].parameters():
                    param.requires_grad = False
                classifier = self.model.classifier
                linear = classifier[6]
                if not isinstance(linear, nn.Linear):
                    raise TypeError('Expected classifier[6] to be nn.Linear')
                in_features = linear.in_features
                classifier[6] = nn.Linear(in_features, num_classes)

            def forward(self, x):
                return self.model(x)
        num_classes = number_of_classes
        model = VGG16(num_classes=num_classes, pretrained=pretrained)
        return model
    elif model_name == 'EfficientNetB0':
        print('Preparing EfficientNetB0 model')
        class EfficientNetB0(nn.Module):
            def __init__(self, num_classes, pretrained=pretrained):
                super(EfficientNetB0, self).__init__()
                self.model = EfficientNet.from_pretrained('efficientnet-b0') if pretrained else EfficientNet.from_name('efficientnet-b0')
                linear = self.model._fc
                if not isinstance(linear, nn.Linear):
                    raise TypeError('Expected _fc to be nn.Linear')
                self.model._fc = nn.Linear(linear.in_features, num_classes)

            def forward(self, x):
                return self.model(x)
        num_classes = number_of_classes
        model = EfficientNetB0(num_classes=num_classes, pretrained=pretrained)
        return model   
    elif model_name == 'NvidiaEfficientNetB4':
        print('Preparing Nvidia EfficientNetB4 model')
        class NvidiaEfficientNetB4(nn.Module):
            def __init__(self, num_classes, pretrained=pretrained):
                super(NvidiaEfficientNetB4, self).__init__()
                self.model = efficientnet_b4(weights='IMAGENET1K_V1' if pretrained else None)
                classifier = self.model.classifier
                linear = classifier[1]
                if not isinstance(linear, nn.Linear):
                    raise TypeError('Expected classifier[1] to be nn.Linear')
                in_features = linear.in_features
                classifier[1] = nn.Linear(in_features, num_classes)

            def forward(self, x):
                return self.model(x)
        num_classes = number_of_classes
        model = NvidiaEfficientNetB4(num_classes=num_classes, pretrained=pretrained)
        return model
    else :
        print('Model not found')
        return None