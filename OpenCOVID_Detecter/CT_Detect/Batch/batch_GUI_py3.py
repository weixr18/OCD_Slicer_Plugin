# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Batch_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(753, 531)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.main = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.main.sizePolicy().hasHeightForWidth())
        self.main.setSizePolicy(sizePolicy)
        self.main.setObjectName("main")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main)
        self.verticalLayout.setObjectName("verticalLayout")
        self.b1 = QtWidgets.QHBoxLayout()
        self.b1.setObjectName("b1")
        self.label = QtWidgets.QLabel(self.main)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.b1.addWidget(self.label)
        self.data_dir = QtWidgets.QLineEdit(self.main)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.data_dir.setFont(font)
        self.data_dir.setObjectName("data_dir")
        self.b1.addWidget(self.data_dir)
        self.b_data_choose = QtWidgets.QPushButton(self.main)
        self.b_data_choose.setObjectName("b_data_choose")
        self.b1.addWidget(self.b_data_choose)
        self.verticalLayout.addLayout(self.b1)
        self.b2 = QtWidgets.QHBoxLayout()
        self.b2.setObjectName("b2")
        self.label_2 = QtWidgets.QLabel(self.main)
        self.label_2.setObjectName("label_2")
        self.b2.addWidget(self.label_2)
        self.out_dir = QtWidgets.QLineEdit(self.main)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.out_dir.setFont(font)
        self.out_dir.setObjectName("out_dir")
        self.b2.addWidget(self.out_dir)
        self.b_out_choose = QtWidgets.QPushButton(self.main)
        self.b_out_choose.setObjectName("b_out_choose")
        self.b2.addWidget(self.b_out_choose)
        self.verticalLayout.addLayout(self.b2)
        self.b3 = QtWidgets.QHBoxLayout()
        self.b3.setObjectName("b3")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.b3.addItem(spacerItem)
        self.table = QtWidgets.QTableWidget(self.main)
        self.table.setMinimumSize(QtCore.QSize(0, 250))
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.b3.addWidget(self.table)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.b3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.b3)
        self.b4 = QtWidgets.QHBoxLayout()
        self.b4.setObjectName("b4")
        spacerItem2 = QtWidgets.QSpacerItem(
            400, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.b4.addItem(spacerItem2)
        self.start = QtWidgets.QPushButton(self.main)
        self.start.setObjectName("start")
        self.b4.addWidget(self.start)
        self.cancel = QtWidgets.QPushButton(self.main)
        self.cancel.setObjectName("cancel")
        self.b4.addWidget(self.cancel)
        self.verticalLayout.addLayout(self.b4)
        self.horizontalLayout.addWidget(self.main)
        self.label.raise_()
        self.label.raise_()
        self.label.raise_()
        self.main.raise_()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "选择数据目录"))
        self.b_data_choose.setText(_translate("Form", "选择..."))
        self.label_2.setText(_translate("Form", "诊断结果保存目录"))
        self.b_out_choose.setText(_translate("Form", "选择..."))
        self.start.setText(_translate("Form", "开始诊断"))
        self.cancel.setText(_translate("Form", "取消"))
