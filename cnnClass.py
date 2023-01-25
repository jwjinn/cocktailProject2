# basic packages
import numpy as np
import pandas as pd
import scipy
import pickle
import random
import os

# loading in and transforming data
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torchvision.utils import make_grid, save_image
import PIL
from PIL import Image
import imageio

# visualizing data
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init
import torch.optim as optim

import shutil


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        # BatchNorm에 bias가 포함되어 있으므로, conv2d는 bias=False로 설정합니다.
        self.residual_function = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.Conv2d(out_channels, out_channels * BasicBlock.expansion, kernel_size=3, stride=1, padding=1,
                      bias=False),
            nn.BatchNorm2d(out_channels * BasicBlock.expansion),
        )

        # identity mapping, input과 output의 feature map size, filter 수가 동일한 경우 사용.
        self.shortcut = nn.Sequential()

        self.relu = nn.ReLU()

        # projection mapping using 1x1conv
        if stride != 1 or in_channels != BasicBlock.expansion * out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels * BasicBlock.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * BasicBlock.expansion)
            )

    def forward(self, x):
        x = self.residual_function(x) + self.shortcut(x)
        x = self.relu(x)
        return x


class BottleNeck(nn.Module):
    expansion = 4

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        self.residual_function = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.Conv2d(out_channels, out_channels * BottleNeck.expansion, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(out_channels * BottleNeck.expansion),
        )

        self.shortcut = nn.Sequential()

        self.relu = nn.ReLU()

        if stride != 1 or in_channels != out_channels * BottleNeck.expansion:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels * BottleNeck.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * BottleNeck.expansion)
            )

    def forward(self, x):
        x = self.residual_function(x) + self.shortcut(x)
        x = self.relu(x)
        return x



class ResNet(nn.Module):
    def __init__(self, block, num_block, num_classes=32, init_weights=True):
        super().__init__()

        self.in_channels=64

        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )

        self.conv2_x = self._make_layer(block, 64, num_block[0], 1)
        self.conv3_x = self._make_layer(block, 128, num_block[1], 2)
        self.conv4_x = self._make_layer(block, 256, num_block[2], 2)
        self.conv5_x = self._make_layer(block, 512, num_block[3], 2)

        self.avg_pool = nn.AdaptiveAvgPool2d((1,1))
        self.fc = nn.Linear(512 * block.expansion, num_classes)

        # weights inittialization
        if init_weights:
            self._initialize_weights()

    def _make_layer(self, block, out_channels, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_channels, out_channels, stride))
            self.in_channels = out_channels * block.expansion

        return nn.Sequential(*layers)

    def forward(self,x):
        output = self.conv1(x)
        output = self.conv2_x(output)
        x = self.conv3_x(output)
        x = self.conv4_x(x)
        x = self.conv5_x(x)
        x = self.avg_pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

    # define weight initialization function
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

def resnet18():
    return ResNet(BasicBlock, [2,2,2,2])

def resnet34():
    return ResNet(BasicBlock, [3, 4, 6, 3])

def resnet50():
    return ResNet(BottleNeck, [3,4,6,3])

def resnet101():
    return ResNet(BottleNeck, [3, 4, 23, 3])

def resnet152():
    return ResNet(BottleNeck, [3, 8, 36, 3])


transform = transforms.ToPILImage()
device = torch.device('cpu')
convert_tensor = transforms.ToTensor()

def resize_in(input_img) :
    input1 = Image.open(input_img)
    input2 = input1.resize((256,256))
    input3 = convert_tensor(input2)
    return input3

def CNN_prc(image) :

    CNNLocation = os.path.abspath("model/Resnet_torch.pt")

    CNN = torch.load(CNNLocation, map_location=torch.device('cpu'))
    CNN.eval()
    image2 = resize_in(image)
    image3 = torch.unsqueeze(image2, 0)
    prc = CNN(image3)
    prc = prc.tolist()
    result = prc[0].index(max(prc[0]))
    return result, prc
# sample ="F:/Final project/data/CNN/train/Aviation2.jpg"


class cnnCover:

    def __init__(self):



        self.CNNLocation = os.path.abspath("model/Resnet_torch.pt")
        name = "Alexander, Aviation, B-52, Bacardi, Black Russian, Bramble, Casino, Clover Club, Cosmopolitan, Cuba Libre, Daliquiri, Dry Martini, Gin Fizz, Grasshopper, John Collins, Kamikaze, Kir,Long island iced Tea, Mai Tai, Manhattan, Margarita, Mojito, Moscow Mule, Paradise,Pina Colada, Rusty Nail, Sea breeze, Sex on the beach, Singapore Sling, Tequila Sunrise, Whiskey Sour, White lady"
        name = name.replace(" ", "")
        self.name = name.split(",")



    def setImage(self, imagelocation):
        self.imageLocation = imagelocation

    def evaluate(self):

        CNN = torch.load(self.CNNLocation, map_location=torch.device('cpu'))
        CNN.eval()
        image2 = resize_in(self.imageLocation)
        image3 = torch.unsqueeze(image2, 0)
        prc = CNN(image3)
        prc = prc.tolist()
        # result = prc[0].index(max(prc[0]))
        return prc

    def keyValue(self):
        value = self.evaluate()[0]

        posibleCocktail = []

        # print(value)

        dictCnn = dict(zip(self.name, value))

        sorted_dict = sorted(dictCnn.items(), key=lambda item: item[1], reverse=True)

        print("전체: ", sorted_dict)

        for i in range(0,4):
            posibleCocktail.append(sorted_dict[i])



        return posibleCocktail




if __name__ == '__main__':
    temp = cnnCover()


    # temp.setImage('./bramble.jpg') # 적중.

    # temp.setImage('./gracehopper.jpeg') # 적중 못함.

    temp.setImage('./margarita.png')


    rankCnn = temp.keyValue()

    print(rankCnn)

    print(rankCnn[0][0])





