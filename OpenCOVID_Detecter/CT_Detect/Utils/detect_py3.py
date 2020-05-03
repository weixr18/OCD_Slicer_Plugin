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


from .net2d_py3 import resnet152
# from .grad_cam_py3 import get_CAM


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


def process(numpy_image, use_cuda=True):
    dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
    model_path = dirPath + '/' + MODEL_PATH
    model = load_classify_model(model_path)
    CAM = None

    # Predict scores
    prediction = classify_CT(model, numpy_image, use_cuda=use_cuda)
    slice_scores = np.argmax(prediction, axis=1)

    # results
    mean_score = np.mean(np.sort(slice_scores)[-3:])
    is_COVID = (mean_score > 0.5)
    key_position = np.argsort(slice_scores)[-3:]
    print("key_position:", key_position)
    support_data = numpy_image[key_position]

    return {
        "is_COVID": is_COVID,
        "slice_scores": slice_scores,
        "CAM_slices": support_data,
    }


if __name__ == "__main__":

    # Do nothing in this main.
    # everything else should be done in server_py3.py
    pass
