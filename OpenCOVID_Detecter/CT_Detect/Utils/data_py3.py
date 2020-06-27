# python 3.6
# Contributors: Xinran Wei, Weixiang Chen
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms


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


def preprocess(np_lung, padding,
               start_pos, end_pos, spacing):

    end_pos = min(end_pos, np_lung.shape[0])
    padding = (end_pos - start_pos) // spacing
    np_lung = np_lung[start_pos:end_pos, :, :]

    print("padding, start_pos, end_pos, spacing:")
    print(padding, start_pos, end_pos, spacing)
    print("max min: ", np_lung.max(), np_lung.min())

    TOP = 2400
    FLOOR = -700

    np_lung[np_lung > TOP] = TOP
    np_lung[np_lung < FLOOR] = FLOOR
    np_lung -= FLOOR
    np_lung = np_lung / (TOP - FLOOR) * 255

    sliced_image = np.zeros([padding, np_lung.shape[1], np_lung.shape[2]])

    for cnt, i in enumerate(range(0, end_pos - start_pos, spacing)):
        if cnt >= padding:
            break
        sliced_image[cnt] = np_lung[i]

    sliced_image = sliced_image[:padding]

    return sliced_image


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
