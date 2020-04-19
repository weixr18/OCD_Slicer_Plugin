# OCD 插件 后端代码
# python 3.6
import os
import sys
import time

import cv2
import torch
import numpy as np
import torch.nn as nn
from torch.autograd import Variable
from torch.utils.data import DataLoader
import argparse
import matplotlib.pyplot as plt

from Utils.data_py3 import *
from Utils.net2d_py3 import resnet152
from grad_cam_py3 import GradCam, preprocess_image


MODEL_PATH = '../model/classify_model.pt'


def load_classify_model(model_path):
    """load the classify net model"""
    model = resnet152(2)
    model_dict = model.state_dict()

    pretrained_dict = torch.load(model_path)
    pretrained_dict = {k: v for k, v in pretrained_dict.items() if
                       k in model_dict.keys() and v.size() == model_dict[k].size()}
    model_dict.update(pretrained_dict)
    model.load_state_dict(model_dict)
    return model


def classify_CT(model, data):
    """return the classify scores of the CT slices"""
    output = None
    data = torch.tensor(data, dtype=torch.float32)
    with torch.no_grad():
        # data size: [-1, 3, 224, 224]
        model.eval()
        net = nn.DataParallel(model).cuda()
        model = model.cuda()
        input = Variable(data).cuda()
        output = net(input)

    if output is not None:
        return output.cpu().numpy()


def get_CAM(model, data):
    """return the CAM picture of the selected slices"""
    grad_cam = GradCam(model=model,
                       target_layer_names=["6"],
                       use_cuda=True)

    CAM_V = []
    for i in range(data.shape[0]):
        d = data[i, :, :, :]
        d = np.transpose(d, (1, 2, 0)).astype(np.float32)
        raw_shape = (d.shape[1], d.shape[0])
        input = preprocess_image(d)

        target_index = 1
        cam, pred = grad_cam(input, target_index)
        CAM_V.append(cam)

    CAM_V = np.array(CAM_V)
    return CAM_V


def get_args():
    """get the command line arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--image_path', type=str, default='../../Example/example1/data/98_1-30.nii',
                        help='Input raw image path')

    parser.add_argument('--mask_path', type=str, default='../../Example/example1/seg/98_1-30.nii',
                        help='Input mask image path')
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    # Prepare data and model
    args = get_args()
    image_path = args.image_path
    dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])
    mask_path = dirPath + '/' + args.mask_path
    numpy_image = concatenate_image_and_mask(image_path, mask_path)
    model_path = dirPath + '/' + MODEL_PATH
    model = load_classify_model(model_path)
    CAM = None

    # Predicrt scores
    prediction = classify_CT(model, numpy_image)
    slice_scores = np.argmax(prediction, axis=1)
    print(image_path.split('/')[-1], np.sort(slice_scores)
          [-3:], np.argsort(slice_scores)[-3:])

    # CAM pictures
    mean_score = np.mean(np.sort(slice_scores)[-3:])
    if mean_score > 0.5:
        support_data = numpy_image[np.argsort(slice_scores)[-3:]]
        numpy_CAM = get_CAM(model, support_data)
        numpy_CAM = numpy_CAM * 255

        # TODO: use socket to pass parameters, rather than files.
        CAM_path = '../__cache/__cache_CAM.npy'
        np.save(dirPath + '/' + CAM_path, numpy_CAM)
