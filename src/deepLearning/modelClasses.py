
from torch import nn

class SmallSimpleCNN(nn.Module):
        def __init__(self):
            super(SmallSimpleCNN, self).__init__()
            self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
            self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
            self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
            self.conv4 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
            self.conv5 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)
            self.fc1 = nn.Linear(256 * 12 * 12, 512)
            self.fc2 = nn.Linear(512, 512)
            self.fc3 = nn.Linear(512, 2)
            self.activationF = nn.ReLU()
            self.maxpool = nn.MaxPool2d(kernel_size=2, stride=2)
            
        def forward(self, x):
            x = self.activationF(self.conv1(x))
            x = self.maxpool(x)
            x = self.activationF(self.conv2(x))
            x = self.maxpool(x)
            x = self.activationF(self.conv3(x))
            x = self.maxpool(x)
            x = self.activationF(self.conv4(x))
            x = self.maxpool(x)
            x = self.activationF(self.conv5(x))
            x = self.maxpool(x)
            x = x.view(x.size(0), -1)
            x = self.activationF(self.fc1(x))
            x = self.activationF(self.fc2(x))
            x = self.fc3(x)
            return x
 
