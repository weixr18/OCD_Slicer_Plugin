# python 3.6
# Contributors: Xinran Wei, Weixiang Chen
import glob
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

transform = transforms.Compose([  # transforms.ToPILImage(),
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0, 0, 0], [1, 1, 1])
])


def temporary(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@temporary
def get_path(np_image_root, np_mask_lung_root):
    np_images = []
    masks = []
    # 读取肺部CT/mask路径
    if isinstance(np_image_root, list):
        for r1, r2 in zip(np_image_root, np_mask_lung_root):
            np_images += glob.glob(r1 + '/*.n*')
            masks += glob.glob(r2 + '/*.n*')
    return np_images, masks


def preprocess(np_lung, padding=35,
               start_pos=-300,
               end_pos=-40,
               spacing=5):

    start_pos += np_lung.shape[0]
    start_pos = min(0, np_lung.shape[0])
    np_lung = np_lung[start_pos:end_pos, :, :]

    TOP = 1200
    FLOOR = -700

    np_lung[np_lung > TOP] = TOP
    np_lung[np_lung < FLOOR] = FLOOR
    np_lung -= FLOOR
    np_lung = np_lung / (TOP - FLOOR) * 255

    if start_pos < 0:
        start_pos += np_lung.shape[0]
    if end_pos < 0:
        end_pos += np_lung.shape[0]

    padding = (end_pos - start_pos) // spacing
    sliced_image = np.zeros([padding, np_lung.shape[1], np_lung.shape[2]])

    for cnt, i in enumerate(range(start_pos, end_pos, spacing)):
        if cnt >= padding:
            break
        sliced_image[cnt] = np_lung[i]

    sliced_image = sliced_image[:padding]

    return sliced_image, padding


def concatenate(np_lung, np_mask, padding):
    # reshape
    sliced_image = np.zeros([3, padding, 224, 224])

    # slice
    for i in range(np_lung.shape[0]):
        d = np_lung[i:i + 1, :, :]

        d = np.concatenate(
            [np_mask[i:i + 1, :, :] * 255, d, d], 0)  # 0:mask ,1,2:data
        d = d.astype(np.uint8)
        d = Image.fromarray(d.transpose(1, 2, 0))
        result = transform(d)
        sliced_image[:, i] = result

    sliced_image = np.swapaxes(sliced_image, 0, 1)
    del np_lung, np_mask
    return sliced_image


@temporary
def concatenate_image_and_mask(np_lung, mask_path, padding=35):
    """get concatenated image and mask """

    # load raw data
    """
    if mask_path.split('.')[-1] == 'nii':
        sitk_mask = sitk.ReadImage(mask_path)
        np_mask = sitk.GetArrayFromImage(sitk_mask)
    elif mask_path.split('.')[-1] == 'npy':
        np_mask = np.load(mask_path)
    else:
        raise IOError("Incorrect input mask file suffix.")

    return concatenate(np_lung, np_mask)
    """
