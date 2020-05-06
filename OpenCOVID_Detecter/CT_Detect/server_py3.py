# python 3.6
# Contributors: Xinran Wei, Bolun Liu,
import time
import socket
import sys
import numpy as np
import pickle
import nibabel as nib
import logging
import argparse
import matplotlib.pyplot as plt

from Utils.data_py3 import concatenate, preprocess
from Utils.segment_py3 import gen_mask
import Utils.detect_py3 as detect_py3


if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

SHOW_RES = False


class DT_Server():
    """Backend as a server"""

    def __init__(self, use_cuda=True):
        self.address = ('127.0.0.1', 31500)
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSocket.bind(self.address)
        print("Server start.")
        print("Loading...")

        self.ServerSocket.listen(5)
        self.ClientSocket, clientAddress = self.ServerSocket.accept()
        print('got connected from', clientAddress)

        self.use_cuda = use_cuda

        pass

    def __del__(self):
        self.ClientSocket.close()
        self.ServerSocket.close()

    def run(self):
        """主函数"""

        while True:

            # 获取图像
            a = self.ClientSocket.recv(200000000)
            lung_pack = pickle.loads(a, encoding='iso-8859-1')
            lung_image = lung_pack["data"]
            info = lung_pack['info']

            print("----------------Image get----------------")

            # 获取mask
            lung_image, padding = preprocess(lung_image,
                                             start_pos=info['start_pos'],
                                             end_pos=info['end_pos'],
                                             spacing=info['spacing'])
            np_mask = gen_mask(lung_image)

            print("----------------Mask get----------------")

            # 进行预测
            cnn_input = concatenate(lung_image, np_mask, padding)
            res = detect_py3.process(cnn_input, use_cuda=self.use_cuda)
            print('slice_scores:', res['slice_scores'])
            print("----------------Prediction done----------------")

            # 发回client
            self.ClientSocket.send(pickle.dumps(res, protocol=2))

            if SHOW_RES:
                ROWS = 2
                SAMPLE_NUM = 3
                for i in range(SAMPLE_NUM):

                    plt.subplot(ROWS, SAMPLE_NUM, 1 + i + SAMPLE_NUM * 0)
                    plt.title('raw data')
                    plt.imshow(res['demo_slices'][i][1], cmap=plt.cm.gray)

                    plt.subplot(ROWS, SAMPLE_NUM, 1 + i + SAMPLE_NUM * 1)
                    plt.title('data & segment')
                    plt.imshow(np.transpose(
                        res['demo_slices'][i], (1, 2, 0)))

                plt.show()

            del res
            print("----------------Array sent back----------------")

        pass  # end run

    pass  # end class


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_cuda", default=True)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    use_cuda = args.use_cuda

    try:
        server = DT_Server(use_cuda=use_cuda)
        server.run()
    except Exception as e:
        time.sleep(10)
        print(logging.exception(e))
