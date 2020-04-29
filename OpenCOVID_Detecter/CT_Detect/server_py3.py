# python 3.6
import time
import socket
import sys
import numpy as np
import pickle
import nibabel as nib
import logging

from Utils.data_py3 import concatenate, preprocess
import Utils.detect_py3 as detect_py3
from Utils.segment_py3 import gen_mask

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


class DT_Server():
    """Backend as a server"""

    def __init__(self):
        self.address = ('127.0.0.1', 31500)
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSocket.bind(self.address)
        print("Server start.")
        print("Loading...")

        self.ServerSocket.listen(5)
        self.ClientSocket, clientAddress = self.ServerSocket.accept()
        print('got connected from', clientAddress)

        pass

    def __del__(self):
        self.ClientSocket.close()
        self.ServerSocket.close()

    def run(self):
        """主函数"""

        try:
            while True:

                # 获取图像
                a = self.ClientSocket.recv(200000000)
                lung_image = pickle.loads(a, encoding='iso-8859-1')

                print("----------------Image get----------------")

                # 获取mask
                lung_image = preprocess(lung_image)
                np_mask = gen_mask(lung_image)

                print("----------------Mask get----------------")

                # 进行预测
                cnn_input = concatenate(lung_image, np_mask)
                res = detect_py3.process(cnn_input)
                print(res['slice_scores'])
                print("----------------Prediction done----------------")

                # 发回client
                self.ClientSocket.send(pickle.dumps(res, protocol=2))
                del res
                print("----------------Array sent back----------------")

        except Exception as e:
            raise e

        pass  # end run

    pass  # end class


if __name__ == "__main__":
    # TODO: listen the port.
    # when data come, process it, then send back results.
    try:
        server = DT_Server()
        server.run()
    except Exception as e:
        time.sleep(10)
        print(logging.exception(e))
