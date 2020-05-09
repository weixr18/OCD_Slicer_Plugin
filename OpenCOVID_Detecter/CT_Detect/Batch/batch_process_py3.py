# python 3.6
# Contributors: Xinran Wei,
import pydicom
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

if True:
    o_path = os.path.realpath(__file__)
    o_path = o_path.split('\\')[:-1]
    o_path = "/".join(o_path)
    sys.path.append(o_path + "/..")
    from Utils.data_py3 import concatenate, preprocess
    from Utils.segment_py3 import gen_mask
    import Utils.detect_py3 as detect_py3


def read_dicom_by_path(case_dir):
    """read the dicom files in the directory"""
    file_names = os.listdir(case_dir)
    slices = []
    for name in file_names:
        try:
            dcm = pydicom.read_file(case_dir + '/' + name)
        except:
            continue
        rows = dcm.Rows
        cols = dcm.Columns
        padding = dcm.PixelPaddingValue

        dtype = np.__getattribute__('int' + str(dcm.BitsStored))
        slc = np.frombuffer(dcm.PixelData, dtype=dtype)
        slc = np.reshape(slc, [rows, cols])
        slices.append(slc)

    slices = np.array(slices)
    return slices


def get_res(lung_image, info, use_cuda):

    print("----------------Image get----------------")

    # 获取mask
    lung_image = preprocess(lung_image,
                            start_pos=info['start_pos'],
                            end_pos=info['end_pos'],
                            spacing=info['spacing'],
                            padding=info['padding'])

    np_mask = gen_mask(lung_image)

    padding = info['padding']
    print("----------------Mask get----------------")

    # 进行预测
    cnn_input = concatenate(lung_image, np_mask, padding)
    res = detect_py3.process(cnn_input, use_cuda=use_cuda)
    print('slice_scores:', res['slice_scores'])
    print("----------------Prediction done----------------")

    return res


if __name__ == "__main__":

    # settings
    info = {
        "start_pos": 0,
        "end_pos": 300,
        "spacing": 5,
    }
    info["padding"] = (info["end_pos"] - info["start_pos"]
                       ) // info["spacing"]
    use_cuda = False

    # image
    case_dir = "D:/Codes/_Projects/Covid/OCD_Slicer_Plugin/Example/raw/Q3GAGR3Z"
    if case_dir[-1] == '/':
        case_dir = case_dir[:-1]
    lung_image = read_dicom_by_path(case_dir)

    # process
    res = get_res(lung_image, info, use_cuda)

    # output
    output_dir = case_dir + "/" + "../output/"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_full_path = output_dir + case_dir.split('/')[-1] + '_res.npz'
    np.savez(output_full_path, **res)

    pass
