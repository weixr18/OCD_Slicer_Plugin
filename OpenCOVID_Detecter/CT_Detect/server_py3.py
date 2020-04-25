# python 3.6
import time
import socket
import sys
import numpy as np
import pickle
import nibabel as nib
import logging

from Utils.data_py3 import concatenate
import Utils.detect_py3 as detect_py3

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


class DT_Server():

    def __init__(self):
        self.address = ('127.0.0.1', 31500)
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSocket.bind(self.address)
        print("Server start.")

        self.ServerSocket.listen(5)
        self.ClientSocket, clientAddress = self.ServerSocket.accept()
        print('got connected from', clientAddress)

        pass

    def __del__(self):
        self.ClientSocket.close()
        self.ServerSocket.close()

    def run(self):
        """主函数"""

        while True:

            # 获取图像
            a = self.ClientSocket.recv(5000000000)
            lung_image = pickle.loads(a, encoding='iso-8859-1')

            print("----------------Image get----------------")

            # 获取mask（暂时以路径中读取的代替）
            mask_path = r'D:\Codes\_Projects\Covid\OCD_Slicer_Plugin\Example\example1\seg\98_1-30.nii'
            if mask_path.split('.')[-1] == 'nii':
                nib_mask = nib.load(mask_path)
                np_mask = np.array(nib_mask.get_data())
            elif mask_path.split('.')[-1] == 'npy':
                np_mask = np.load(mask_path)
            else:
                raise IOError("Incorrect input mask file suffix.")

            print("----------------Mask get----------------")

            # 进行预测
            cnn_input = concatenate(lung_image, np_mask)
            res = detect_py3.process(cnn_input)
            print("----------------Prediction done----------------")

            # 发回client
            self.ClientSocket.send(pickle.dumps(res, protocol=2))
            print("----------------Array sent back----------------")

        pass

    pass


if __name__ == "__main__":
    # TODO: listen the port.
    # when data come, process it, then send back results.
    try:
        server = DT_Server()
        server.run()
    except Exception as e:
        time.sleep(10)
        print(logging.exception(e))
