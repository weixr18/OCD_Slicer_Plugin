import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from batch_GUI_py3 import Ui_Form
from batch_process_py3 import read_dicom_by_path, get_res


class COVID_Diag(QWidget, Ui_Form):

    def __init__(self):
        super(COVID_Diag, self).__init__(None)
        self.setupUi(self)
        self.setGeometry(300, 300, 1000, 600)
        self.setWindowTitle('新冠肺炎CT批诊断工具')
        self.setWindowIcon(QIcon('../Resources/Icons/CT_Detect.png'))
        self.show()

        self.b_data_choose.clicked.connect(self.chooseInput)
        self.b_data_choose.clicked.connect(self.setForm)
        self.b_out_choose.clicked.connect(self.choossOutput)
        self.start.clicked.connect(self.startProcess)

        self.table.setColumnCount(5)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['选择', '编号', '文件夹名', '文件数', '状态'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        pass

    def chooseInput(self):
        self.t_inputDir = QFileDialog.getExistingDirectory()
        self.data_dir.setText(self.t_inputDir)
        pass

    def choossOutput(self):
        self.t_outputDir = QFileDialog.getExistingDirectory()
        self.out_dir.setText(self.t_outputDir)
        pass

    def setForm(self):
        self.dirs = []
        for _, dirnames, __ in os.walk(self.t_inputDir):
            self.dirs = dirnames
            break

        self.table.setRowCount(len(self.dirs))
        for i in range(len(self.dirs)):
            checkbx = QTableWidgetItem()
            checkbx.setCheckState(QtCore.Qt.Checked)
            self.table.setItem(i, 0, checkbx)
            self.table.setItem(i, 1, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 2, QTableWidgetItem(self.dirs[i]))
            for _, __, filenames in os.walk(self.t_inputDir + '/' + self.dirs[i]):
                n = len(filenames)
                break
            self.table.setItem(i, 3, QTableWidgetItem(str(n)))
            self.table.setItem(i, 4, QTableWidgetItem("未诊断"))

        pass

    def startProcess(self):
        # get checked
        p_checkdirs = []
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).checkState() > 0:
                p_checkdirs.append((i, self.dirs[i]))

        print(p_checkdirs)

        # get info
        info = {
            "start_pos": 0,
            "end_pos": 300,
            "spacing": 5,
        }
        info["padding"] = (info["end_pos"] - info["start_pos"]
                           ) // info["spacing"]
        use_cuda = False

        for i, case_dir in p_checkdirs:
            case_dir = self.t_inputDir + '/' + case_dir
            lung_image = read_dicom_by_path(case_dir)
            if lung_image is None:
                self.table.setItem(i, 4, QTableWidgetItem("读取失败"))
                continue

            res = get_res(lung_image, info, use_cuda)

            output_dir = self.t_outputDir
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            output_full_path = output_dir + \
                case_dir.split('/')[-1] + '_res.npz'
            np.savez(output_full_path, **res)

            self.table.setItem(i, 4, QTableWidgetItem("诊断完成"))

        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    d = COVID_Diag()
    d.show()
    sys.exit(app.exec_())
