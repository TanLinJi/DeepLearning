# 为了规范，一般把模型单独提取出来
from torch import nn
import torch

#  搭建神经网络（CIFAR10是十分类的数据集，所以应该搭建一个十分类的网络）
class Tudui(nn.Module):
    def __init__(self):
        super(Tudui, self).__init__()
        self.model = nn.Sequential(
            nn.Conv2d(3, 32, 5, 1, 2),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 32, 5, 1, 2),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 5, 1, 2),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(1024, 64),
            nn.Linear(64, 10)
        )
    def forward(self, input):
        output = self.model(input)
        return output
    

if __name__=='__main__':
    tudui = Tudui()
    # 验证模型的正确性
    # 一般是给定一个输入的尺寸，看输出的尺寸是否和预期的相同
    input = torch.ones((64, 3, 32, 32))
    output = tudui(input)
    print(output.shape)