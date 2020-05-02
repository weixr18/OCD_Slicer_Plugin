# OCD 插件 后端代码
# python 3.6
import os
import sys
import time

import torch
import numpy as np
import torch.nn as nn
from torch.autograd import Variable
import argparse
# import matplotlib.pyplot as plt


from .net2d_py3 import resnet152
from .grad_cam_py3 import GradCam, preprocess_image  # get_CAM


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


def classify_CT(model, data, use_cuda=True):
    """return the classify scores of the CT slices"""
    output = None
    data = torch.tensor(data, dtype=torch.float32)

    if use_cuda:
        with torch.no_grad():
            # data size: [-1, 3, 224, 224]
            model.eval()
            net = nn.DataParallel(model).cuda()
            model = model.cuda()
            input = Variable(data).cuda()
            output = net(input)

        if output is not None:
            return output.cpu().numpy()
    else:
        with torch.no_grad():
            # data size: [-1, 3, 224, 224]
            model.eval()
            net = nn.DataParallel(model)
            input = Variable(data)
            output = net(input)

        if output is not None:
            return output.cpu().numpy()


def get_CAM(model, data, use_cuda=True):
    """return the CAM picture of the selected slices"""
    grad_cam = GradCam(model=model,
                       target_layer_names=["6"],
                       use_cuda=use_cuda)

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


def process(numpy_image, use_cuda=True):
    dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
    model_path = dirPath + '/' + MODEL_PATH
    model = load_classify_model(model_path)
    CAM = None

    # Predict scores
    prediction = classify_CT(model, numpy_image, use_cuda=use_cuda)
    slice_scores = np.argmax(prediction, axis=1)
    print("------------------Scoring done!------------------")

    # CAM pictures
    mean_score = np.mean(np.sort(slice_scores)[-3:])
    is_COVID = (mean_score > 0.5)
    if True:  # is_COVID:
        print(np.argsort(slice_scores)[-3:])
        a = np.argsort(slice_scores)[-3:]

        support_data = numpy_image[np.argsort(slice_scores)[-3:]]
        numpy_CAM = get_CAM(model, support_data, use_cuda=use_cuda)

        return {
            "is_COVID": is_COVID,
            "numpy_CAM": numpy_CAM,
            "slice_scores": slice_scores,
            "CAM_slices": support_data,
        }
    else:
        return {
            "is_COVID": is_COVID,
            "slice_scores": slice_scores,
        }


if __name__ == "__main__":

    # TODO: do nothing in this main.
    # everything else should be done in server_py3.py
    pass
