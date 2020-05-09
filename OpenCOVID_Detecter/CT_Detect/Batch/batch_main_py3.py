import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
from batch_GUI_py3 import Ui_Form


class COVID_Diag(QWidget, Ui_Form):

    def __init__(self):
        super(COVID_Diag, self).__init__(None)
        self.setupUi(self)
        self.setGeometry(300, 300, 1000, 600)
        self.setWindowTitle('新冠肺炎CT批诊断工具')
        self.setWindowIcon(QIcon('../Resources/Icons/CT_Detect.png'))
        self.show()

        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    d = COVID_Diag()
    d.show()
    sys.exit(app.exec_())
