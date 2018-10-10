import torch.nn as nn
import torch.utils.model_zoo as model_zoo

__all__ = ['ResNet', 'resnet54']


def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class BasicBlock(nn.Module):
	def __init__(self, inplanes, planes, stride=1, downsample=None):
		super(BasicBlock, self).__init__()
		self.conv1 = conv3x3(inplanes, planes, stride)
		self.bn1 = nn.BatchNorm2d(planes)
		self.relu = nn.ReLU(inplace=True)
		self.conv2 = conv3x3(planes, planes) 
		self.bn2 = nn.BatchNorm2d(planes)
		self.downsample = downsample
		self.stride = stride

	def forward(self, x):
		residual = x

		out = self.conv1(x)
		out = self.bn1(out)
		out = self.relu(out)

		out = self.conv2(out)
		out = self.bn2(out)

		if self.downsample is not None:
			residual = self.downsample(x)

		out += residual
		out = self.relu(out)
		return out


class ResNet(nn.Module):
	def __init__(self, block, layers, num_classes=10):
		super(ResNet, self).__init__()
		self.inplanes = 16
		self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, 
			                   padding=1, bias=False)
		self.bn1 = nn.BatchNorm2d(16)
		self.relu = nn.ReLU(inplace=True)

		self.layer1 = self._make_layer(block, 16, layers[0])
		self.layer2 = self._make_layer(block, 32, layers[1], stride=2) 
		self.layer3 = self._make_layer(block, 64, layers[2], stride=2)  
		self.avg_pool = nn.AvgPool2d(8, stride=1)
		self.fc_out = nn.Linear(64, num_classes)

		for m in self.modules():
			if isinstance(m, nn.Conv2d):
				nn.init.kaiming_normal_(m.weight, mode='fan_out', 
					                    nonlinearity='relu')
			elif isinstance(m, nn.BatchNorm2d):
				nn.init.constant_(m.weight, 1)
				nn.init.constant_(m.bias, 0)

	def _make_layer(self, block, planes, blocks, stride=1):
		downsample = None
		if stride != 1 or self.inplanes != planes:
			downsample = nn.Sequential(
				nn.Conv2d(self.inplanes, planes, kernel_size=1, 
					      stride=stride, bias=False),
				nn.BatchNorm2d(planes))
		layers = []
		layers.append(block(self.inplanes, planes, stride, downsample))
		self.inplanes = planes
		for i in range(1, blocks):
			layers.append(block(self.inplanes, planes))
		return nn.Sequential(*layers)

	def forward(self, x):
		x = self.conv1(x)
		x = self.bn1(x)
		x = self.relu(x)

		x = self.layer1(x)
		x = self.layer2(x)
		x = self.layer3(x)

		x = self.avg_pool(x)
		x = x.view(x.size(0), -1)
		x = self.fc_out(x)
		return x


def resnet54(**kwargs):
	model = ResNet(BasicBlock, [9, 9, 9], **kwargs) 
	return model
