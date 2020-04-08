# python 3.6
import glob
import torch
import numpy as np
import SimpleITK as sitk
from PIL import Image
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


def concatenate_image_and_mask(image_path, mask_path, padding=35):
    """get concatenated image and mask via path"""
    # load video into a tensor
    if image_path[-1] == '\n':
        image_path = image_path[:-1]

    # load raw data
    if mask_path.split('.')[-1] == 'nii':
        sitk_mask = sitk.ReadImage(mask_path)
        np_mask = sitk.GetArrayFromImage(sitk_mask)
    elif mask_path.split('.')[-1] == 'npy':
        np_mask = np.load(mask_path)
    else:
        raise IOError("Incorrect input mask file suffix.")

    if image_path.split('.')[-1] == 'nii':
        sitk_image = sitk.ReadImage(image_path)
        np_image = sitk.GetArrayFromImage(sitk_image)
    elif image_path.split('.')[-1] == 'npy':
        np_image = np.load(image_path)
    else:
        raise IOError("Incorrect input image file suffix.")

    # reshape
    np_image = np_image[-300:-40, :, :]
    np_mask = np_mask[-300:-40, :np_image.shape[1], :np_image.shape[2]]
    np_image = np_image[:np_mask.shape[0],
                        :np_mask.shape[1], :np_mask.shape[2]]

    sliced_image = np.zeros([3, padding, 224, 224])

    # slice
    for cnt, i in enumerate(range(np_image.shape[0]-40, 45, -5)):
        # for cnt, i in enumerate(range(np_image.shape[0]-5,5, -3)):
        if cnt >= padding:
            break
        d = np_image[i - 1:i + 1, :, :]
        d[d > 700] = 700
        d[d < -1200] = -1200
        d = d * 255.0 / 1900
        d = d - d.min()
        d = np.concatenate(
            [np_mask[i:i + 1, :, :] * 255, d], 0)  # mask one channel
        d = d.astype(np.uint8)
        d = Image.fromarray(d.transpose(1, 2, 0))
        result = transform(d)
        sliced_image[:, cnt] = result

    tshape = sliced_image.shape
    sliced_image.resize([tshape[1], tshape[0], tshape[2], tshape[3]])
    return sliced_image
