# python 3.6
# Contributors: Xinran Wei, PeiYi Han
import os
import sys
import time
import socket
import logging
import argparse
import pickle
import traceback

SHOW_RES = False
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


def unzip_file(zip_src, dst_dir):
    import zipfile
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')


def load_modules():
    """load every module the project needs"""
    try:
        dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])
        if (sys.version.find('64 bit') > 0):
            include_path = dirPath + '/../../../Tools/required/required-amd64'
        else:
            include_path = dirPath + '/../../../Tools/required/required-win32'

        zip_path = include_path + '.zip'
        if not os.path.exists(include_path):
            os.mkdir(include_path)
            print("Unzip files...")
            unzip_file(zip_path, '/'.join(include_path.split('/')[:-1]))

        if (sys.version.find('64 bit') > 0):
            sys.path.insert(
                0, dirPath + '/../../../Tools/required/required-amd64')
        else:
            sys.path.insert(
                0, dirPath + '/../../../Tools/required/required-win32')
        sys.path.insert(0, dirPath)

        import numpy as np
        import nibabel as nib

        from data_py3 import concatenate, preprocess
        from segment_py3 import gen_mask
        import detect_py3
    except Exception as e:
        traceback.print_exc()


class DT_Server():
    """Backend as a server"""

    def __init__(self, use_cuda=True):
        self.address = ('127.0.0.1', 31500)
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSocket.bind(self.address)
        print("Loading...")

        self.ServerSocket.listen(5)
        self.ClientSocket, clientAddress = self.ServerSocket.accept()
        print('Initialize succesful.')

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

    load_modules()
    args = get_args()
    use_cuda = args.use_cuda

    try:
        server = DT_Server(use_cuda=use_cuda)
        server.run()
    except Exception as e:
        time.sleep(10)
        print(logging.exception(e))
