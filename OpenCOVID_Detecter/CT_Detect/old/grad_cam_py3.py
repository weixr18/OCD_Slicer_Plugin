# python 3.6
# Contributors: Xinran Wei, Weixiang Chen
import cv2
import os
import numpy as np
import torch
from torch.autograd import Function
from torchvision import models
from .net2d_py3 import resnet152
import matplotlib.pyplot as plt

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
MODEL_PATH = '../model/classify_model.pt'
dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
ABS_MODEL_PATH = dirPath + '/' + MODEL_PATH


def load_classify_model(model_path=ABS_MODEL_PATH):
    """load the classify net model"""
    model = resnet152(2)
    model_dict = model.state_dict()

    pretrained_dict = torch.load(model_path)
    pretrained_dict = {k: v for k, v in pretrained_dict.items() if
                       k in model_dict.keys() and v.size() == model_dict[k].size()}
    model_dict.update(pretrained_dict)
    model.load_state_dict(model_dict)
    return model


class FeatureExtractor():
    """ Class for extracting activations and
    registering gradients from targetted intermediate layers """

    def __init__(self, model, target_layers):
        self.model = model
        self.target_layers = target_layers
        self.gradients = []

    def save_gradient(self, grad):
        self.gradients.append(grad)

    def __call__(self, x):
        outputs = []
        self.gradients = []
        for name, module in self.model._modules.items():
            x = module(x)
            if name in self.target_layers:
                x.register_hook(self.save_gradient)
                outputs += [x]
        return outputs, x


class ModelOutputs():
    """ Class for making a forward pass, and getting:
    1. The network output.
    2. Activations from intermeddiate targetted layers.
    3. Gradients from intermeddiate targetted layers. """

    def __init__(self, model, target_layers):
        self.model = model
        self.feature_extractor = FeatureExtractor(
            self.model.features, target_layers)

    def get_gradients(self):
        return self.feature_extractor.gradients

    def __call__(self, x):
        target_activations, output = self.feature_extractor(x)
        output = output.view(output.size(0), -1)
        output = self.model.classifier(output)
        return target_activations, output


def preprocess_image(img):
    means = [0, 0, 0]
    stds = [1, 1, 1]

    preprocessed_img = img.copy()[:, :, ::-1]
    for i in range(3):
        preprocessed_img[:, :, i] = preprocessed_img[:, :, i] - means[i]
        preprocessed_img[:, :, i] = preprocessed_img[:, :, i] / stds[i]
    preprocessed_img = \
        np.ascontiguousarray(np.transpose(preprocessed_img, (2, 0, 1)))
    preprocessed_img = torch.from_numpy(preprocessed_img)
    preprocessed_img.unsqueeze_(0)
    input = preprocessed_img.requires_grad_(True)
    return input


class GradCam:
    def __init__(self, model, target_layer_names, use_cuda):
        self.model = model
        self.model.eval()
        self.cuda = use_cuda
        if self.cuda:
            self.model = model.cuda()

        self.extractor = ModelOutputs(self.model, target_layer_names)

    def forward(self, input):
        return self.model(input)

    def __call__(self, input, index=None):
        if self.cuda:
            features, output = self.extractor(input.cuda())
        else:
            features, output = self.extractor(input)
        pred = np.exp(output.log_softmax(-1).cpu().data.numpy()[:, 1])
        if index == None:
            index = np.argmax(output.cpu().data.numpy())

        one_hot = np.zeros((1, output.size()[-1]), dtype=np.float32)
        one_hot[0][index] = 1
        one_hot = torch.from_numpy(one_hot).requires_grad_(True)
        if self.cuda:
            one_hot = torch.sum(one_hot.cuda() * output)
        else:
            one_hot = torch.sum(one_hot * output)

        self.model.features.zero_grad()
        self.model.classifier.zero_grad()
        one_hot.backward(retain_graph=True)

        grads_val = self.extractor.get_gradients()[-1].cpu().data.numpy()

        target = features[-1]
        target = target.cpu().data.numpy()[0, :]

        weights = np.mean(grads_val, axis=(2, 3))[0, :]
        cam = np.zeros(target.shape[1:], dtype=np.float32)

        for i, w in enumerate(weights):
            cam += w * target[i, :, :]

        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (224, 224))
        cam = cam - np.min(cam)
        cam = cam / np.max(cam)
        return cam, pred


class GuidedBackpropReLU(Function):

    @staticmethod
    def forward(self, input):
        positive_mask = (input > 0).type_as(input)
        output = torch.addcmul(torch.zeros(
            input.size()).type_as(input), input, positive_mask)
        self.save_for_backward(input, output)
        return output

    @staticmethod
    def backward(self, grad_output):
        input, output = self.saved_tensors
        grad_input = None

        positive_mask_1 = (input > 0).type_as(grad_output)
        positive_mask_2 = (grad_output > 0).type_as(grad_output)
        grad_input = torch.addcmul(torch.zeros(input.size()).type_as(input),
                                   torch.addcmul(torch.zeros(input.size()).type_as(input), grad_output,
                                                 positive_mask_1), positive_mask_2)

        return grad_input


class GuidedBackpropReLUModel:
    def __init__(self, model, use_cuda):
        self.model = model
        self.model.eval()
        self.cuda = use_cuda
        if self.cuda:
            self.model = model.cuda()

        # replace ReLU with GuidedBackpropReLU
        for idx, module in self.model.features._modules.items():
            if module.__class__.__name__ == 'ReLU':
                self.model.features._modules[idx] = GuidedBackpropReLU.apply

    def forward(self, input):
        return self.model(input)

    def __call__(self, input, index=None):
        if self.cuda:
            output = self.forward(input.cuda())
        else:
            output = self.forward(input)

        if index == None:
            index = np.argmax(output.cpu().data.numpy())

        one_hot = np.zeros((1, output.size()[-1]), dtype=np.float32)
        one_hot[0][index] = 1
        one_hot = torch.from_numpy(one_hot).requires_grad_(True)
        if self.cuda:
            one_hot = torch.sum(one_hot.cuda() * output)
        else:
            one_hot = torch.sum(one_hot * output)

        # self.model.features.zero_grad()
        # self.model.classifier.zero_grad()
        one_hot.backward(retain_graph=True)

        output = input.grad.cpu().data.numpy()
        output = output[0, :, :, :]

        return output


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-cuda', action='store_true', default=True,
                        help='Use NVIDIA GPU acceleration')
    parser.add_argument('--image_path', type=str, default='/mnt/data9/new_seg_set/nore/test_raw_jpgs2',
                        help='Input raw image path')
    parser.add_argument('--mask_path', type=str, default='/mnt/data9/new_seg_set/nore/test_masked_jpgs2',
                        help='Input mask image path')
    parser.add_argument('--model_path', type=str, default='../saves/for_xzw.pt',
                        help='Model path')
    parser.add_argument('--output_path', type=str, default='/mnt/data9/new_seg_set/cam/NCP_ill4',
                        help='Cam output path')
    args = parser.parse_args()
    args.use_cuda = args.use_cuda and torch.cuda.is_available()
    if args.use_cuda:
        print("Using GPU for acceleration")
    else:
        print("Using CPU for computation")

    return args


def deprocess_image(img, mask=None):
    """ see https://github.com/jacobgil/keras-grad-cam/blob/master/grad-cam.py#L65 """
    img = img - np.mean(img)
    img = img / (np.std(img) + 1e-5)
    img = img * 0.1
    img = img + 0.5
    img[mask == 0] = 0.5
    img = np.clip(img, 0, 1)

    return np.uint8(img * 255)


def show_cam_on_image(img, mask, extral=None):
    if isinstance(extral, np.ndarray):
        mask = mask * extral[:, :, 1]
    heatmap = cv2.applyColorMap(np.uint8(255 * mask), cv2.COLORMAP_JET)
    heatmap = np.float32(heatmap)
    heatmap = heatmap / 255

    cam = heatmap + np.float32(img)
    cam = cam / np.max(cam)
    cam[extral == 0] = np.float32(img)[extral == 0]
    # cv2.imwrite("cam.jpg", np.uint8(255 * cam))
    return np.uint8(255 * cam)


def model_get(path):
    model = resnet152(2)
    pretrained_dict = torch.load(path)
    # load only exists weights
    model_dict = model.state_dict()
    pretrained_dict = {k: v for k, v in pretrained_dict.items() if
                       k in model_dict.keys() and v.size() == model_dict[k].size()}
    # print('matched keys:', len(pretrained_dict))
    model_dict.update(pretrained_dict)
    model.load_state_dict(model_dict)
    return model


def get_CAM(model, data, use_cuda=True):
    """return the CAM picture of the selected slices"""
    grad_cam = GradCam(model=model,
                       target_layer_names=["6"],
                       use_cuda=use_cuda)
    gb_model = GuidedBackpropReLUModel(
        model=load_classify_model(), use_cuda=use_cuda)

    shape = data.shape
    # CAM_V = np.zeros([shape[0], shape[-2], shape[-1]])
    CAM_V = []

    for i in range(data.shape[0]):
        img = data[i, :, :, :]
        img_raw = img.copy()
        img_raw[0] = img_raw[1]
        img = np.transpose(img, (1, 2, 0)).astype(np.float32)
        img_raw = np.transpose(img_raw, (1, 2, 0)).astype(np.float32)

        input = preprocess_image(img)
        target_index = 1
        mask, pred = grad_cam(input, target_index)
        cam = show_cam_on_image(img_raw, mask)

        """

        print("mask-->cam_mask, attention_area")
        cam_mask = cv2.merge([mask, mask, mask])
        attention_area = cam_mask > 0.55

        print("img-->gb, gbt")
        gb = gb_model(input, index=target_index)
        gb = gb.transpose((1, 2, 0))
        print("gb_0:", gb.shape, gb.min(), gb.max())
        gbt = gb.copy()

        print("gb-->attention_area")
        gb = deprocess_image(gb)
        attention_area = attention_area*(np.abs(gb-128) > 64)
        attention_area = attention_area[:, :, 0] + \
            attention_area[:, :, 1]+attention_area[:, :, 2]
        attention_area = (attention_area >= 1).astype(np.uint8)
        kernel = np.ones((5, 5), np.uint8)
        attention_area = cv2.erode(cv2.morphologyEx(
            attention_area, cv2.MORPH_CLOSE, kernel), kernel)

        print("img-->lung_mask-->attention_area")
        lung_mask = cv2.erode(img[:, :, 2], kernel)
        attention_area = attention_area*lung_mask
        attention_area = np.stack(
            [attention_area, attention_area, attention_area], -1)

        print("cam_mask, gbt, attention_area-->cam_gb")
        cam_gb = deprocess_image(cam_mask * gbt, attention_area)
        """

        # cam = mask
        # CAM_V[i] = cam
        CAM_V.append(cam)

    CAM_V = np.array(CAM_V)

    return CAM_V


if __name__ == '__main__':

    print("Only use as a module. IMPORT it rather than execute it.")
