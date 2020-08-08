# -*- coding: utf-8 -*-
# encoding: utf-8

import os
import unittest
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import logging
import json
import codecs
#
# CT_Characteristic
#


class CT_Characteristic(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        # TODO make this more human readable by adding spaces
        self.parent.title = "CT_Characteristic"
        self.parent.categories = ["COVID Research Tools"]
        self.parent.dependencies = []
        self.parent.contributors = ["XinRan Wei, Kaiwen Men, PeiYi Han, BoLun Liu, \
                                    WeiXiang Chen, (Tsinghua Univ.)"]
        self.parent.helpText = ""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        # replace with organization, grant and thanks.
        self.parent.acknowledgementText = ""

#
# CT_CharacteristicWidget
#


DICT = {

    "bblx_": u"病变类型",
    "bbfb_": u"病变分布",
    "bzdx_": u"病灶大小",
    "bbsm_": u"病变数目",
    "bbwz_": u"病变位置",

    "mbly": u"磨玻璃影",
    "shb": u"实变",
    "dmdy": u"低密度影",
    "jxzbb": u"间歇质病变",
    "fwzgb": u"蜂窝状改变",
    "fqz": u"肺气肿",
    "fdp": u"肺大泡",
    "qx": u"气胸",
    "zqgkz": u"支气管扩张",
    "xxy": u"线性影",

    "zy": u"中央",
    "yzqgfb": u"沿支气管分布",
    "xmfj": u"胸膜附近",
    "wz": u"外周",
    "sj": u"随机",

    "jiejie": u"<3cm结节",
    "bankuai": u"3-10cm斑块",
    "dapian": u">10cm大片",
    "msx": u"弥散性",
    "wfcl": u"无法测量",

    "danfa": u"单发",
    "duofa24": u"2-4，多发",
    "duofa5": u"5以上，多发",
    "msx_2": u"弥散性2",

    "zs": u"左上",
    "zx": u"左下",
    "ys": u"右上",
    "yz": u"右中",
    "yx": u"右下",

    "wgbh_": u"微观变化",
    "qttz_": u"其他特征",
    "qttz__": u"其他特征",

    "xyjgzh": u"小叶间隔增厚",
    "zqgbzh": u"支气管壁增厚",
    "xmzh": u"胸膜增厚",
    "xqjy": u"胸腔积液",
    "kqzqgz": u"空气支气管征",
    "plsz": u"铺路石征",
    "yz_2": u"晕征",
    "fyz": u"反晕征",

    "syz": u"树芽征",
    "zjxy": u"坠积效应",
    "dfxxjj": u"多发性小结节",
    "xyzxjj": u"小叶中心结节",
    "lbjzd": u"淋巴结肿大",
    "zqgjd": u"支气管截断",

    "xwzbtmd": u"细网状不透明度",
    "zbzzwdjj": u"主病灶之外的结节",
    "dmzc": u"动脉增粗",
    "kqzqgz": u"空气支气管症",
    "zgzh": u"纵膈增厚",
    "xzxy": u"血坠效应",
}


class CT_CharacteristicWidget(ScriptedLoadableModuleWidget):

    def setup(self):
        # Father content setup
        ScriptedLoadableModuleWidget.setup(self)

        # Logic Component Setup
        self.logic = CT_CharacteristicLogic()

        # Load widget from .ui file (created by Qt Designer)
        uiWidget = slicer.util.loadUI(
            self.resourcePath('UI/CT_Characteristic.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)
        # self.ui.FileSelect.inputw.inputSelector.setMRMLScene(slicer.mrmlScene)

        # components
        self.saveButton = self.ui.Save
        self.fileDirSelector = self.ui.FileSelect.children()[1].PathLineEdit
        self.spinbox = self.ui.FileSelect.children()[2].idSpinBox

        # connections
        self.saveButton.connect('clicked(bool)', self.saveCurrentPage)
        self.fileDirSelector.connect(
            'currentPathChanged(QString)', self.onDirSelected)
        self.spinbox.connect('valueChanged(int)', self.onIndexChange)

        # enables
        self.setEnables()

    def setEnables(self):
        self.ENABLE = not (self.fileDirSelector.currentPath == "")
        self.saveButton.setEnabled(self.ENABLE)
        self.spinbox.setEnabled(self.ENABLE)
        self.ui.zybz.setEnabled(self.ENABLE)
        self.ui.qtzx.setEnabled(self.ENABLE)
        self.ui.ypzd.setEnabled(self.ENABLE)
        self.ui.zdbw.setEnabled(self.ENABLE)

    def cleanup(self):
        pass

    def onDirSelected(self, file_dir):
        """文件夹选择后"""

        if file_dir is not '\n':
            self.setEnables()

            # 获取已有数据
            txt_path = file_dir + "/result.txt"

            if os.path.exists(txt_path):
                self.txt = open(txt_path, mode='r')
                sample_json = self.txt.read()
                self.txt.close()
                self.res = json.loads(sample_json.decode("gb2312"))
            else:
                self.txt = open(txt_path, mode='w')
                self.txt.write("{}")
                self.txt.close()
                self.res = dict()

            # 设置数据选择范围
            file_list = os.listdir(file_dir)
            n_file_list = []
            for f in file_list:
                if f[-3:] == u"nii":
                    n_file_list.append(f)
            file_list = n_file_list
            self.spinbox.setMaximum(len(file_list) - 1)

            # 更新界面
            self.lastIndex = self.spinbox.value
            self.onIndexChange(self.spinbox.value)

        pass

    def onIndexChange(self, sample_id):
        """加载已有结果"""

        # 载入数据
        file_dir = self.fileDirSelector.currentPath
        data_path = file_dir + "/" + str(sample_id) + ".nii"
        flag = slicer.util.loadVolume(data_path)
        self.currentVolume = slicer.util.getNode(str(sample_id) + "*")

        if self.lastIndex != sample_id:
            # 若非初次打开
            lastNode = slicer.util.getNode(self.lastVolumeName)
            slicer.mrmlScene.RemoveNode(lastNode)
            self.lastIndex = sample_id
            self.lastVolumeName = self.currentVolume.GetName()

        else:
            # 若为初次打开
            self.lastVolumeName = self.currentVolume.GetName()

        # 判断是否已有记录
        if not hasattr(self, "res"):
            return None
        if self.res == dict():
            return None
        if str(sample_id) not in self.res:
            self.pageRefresh()
            return None

        # 页面刷新
        data = self.res[str(sample_id)]
        self.pageRefresh(data)

        pass

    def pageRefresh(self, data=None):
        """页面刷新"""

        if data is not None:
            # 主要病灶
            ZYBZ = list(self.ui.zybz.children())

            if True:
                if u"磨玻璃影" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[2].setChecked(True)
                else:
                    ZYBZ[2].setChecked(False)
                if u"实变" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[3].setChecked(True)
                else:
                    ZYBZ[3].setChecked(False)
                if u"低密度影" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[4].setChecked(True)
                else:
                    ZYBZ[4].setChecked(False)
                if u"间歇质病变" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[5].setChecked(True)
                else:
                    ZYBZ[5].setChecked(False)

                if u"蜂窝状改变" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[6].setChecked(True)
                else:
                    ZYBZ[6].setChecked(False)
                if u"肺气肿" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[7].setChecked(True)
                else:
                    ZYBZ[7].setChecked(False)
                if u"肺大泡" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[8].setChecked(True)
                else:
                    ZYBZ[8].setChecked(False)
                if u"气胸" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[9].setChecked(True)
                else:
                    ZYBZ[9].setChecked(False)
                if u"支气管扩张" in data[u"主要病灶"][u"病变类型"]:
                    ZYBZ[10].setChecked(True)
                else:
                    ZYBZ[10].setChecked(False)

                if u"单发" in data[u"主要病灶"][u"病变数目"]:
                    ZYBZ[12].setChecked(True)
                else:
                    ZYBZ[12].setChecked(False)
                if u"2-4，多发" in data[u"主要病灶"][u"病变数目"]:
                    ZYBZ[13].setChecked(True)
                else:
                    ZYBZ[13].setChecked(False)
                if u"5以上，多发" in data[u"主要病灶"][u"病变数目"]:
                    ZYBZ[14].setChecked(True)
                else:
                    ZYBZ[14].setChecked(False)
                if u"弥散性2" in data[u"主要病灶"][u"病变数目"]:
                    ZYBZ[15].setChecked(True)
                else:
                    ZYBZ[15].setChecked(False)

                if u"中央" in data[u"主要病灶"][u"病变分布"]:
                    ZYBZ[17].setChecked(True)
                else:
                    ZYBZ[17].setChecked(False)
                if u"沿支气管分布" in data[u"主要病灶"][u"病变分布"]:
                    ZYBZ[18].setChecked(True)
                else:
                    ZYBZ[18].setChecked(False)
                if u"外周" in data[u"主要病灶"][u"病变分布"]:
                    ZYBZ[19].setChecked(True)
                else:
                    ZYBZ[19].setChecked(False)
                if u"随机" in data[u"主要病灶"][u"病变分布"]:
                    ZYBZ[20].setChecked(True)
                else:
                    ZYBZ[20].setChecked(False)

                if u"<3cm结节" in data[u"主要病灶"][u"病灶大小"]:
                    ZYBZ[22].setChecked(True)
                else:
                    ZYBZ[22].setChecked(False)
                if u"3-10cm斑块" in data[u"主要病灶"][u"病灶大小"]:
                    ZYBZ[23].setChecked(True)
                else:
                    ZYBZ[23].setChecked(False)
                if u">10cm大片" in data[u"主要病灶"][u"病灶大小"]:
                    ZYBZ[24].setChecked(True)
                else:
                    ZYBZ[24].setChecked(False)
                if u"无法测量" in data[u"主要病灶"][u"病灶大小"]:
                    ZYBZ[25].setChecked(True)
                else:
                    ZYBZ[25].setChecked(False)

                if u"左上" in data[u"主要病灶"][u"病变位置"]:
                    ZYBZ[27].setChecked(True)
                else:
                    ZYBZ[27].setChecked(False)
                if u"左下" in data[u"主要病灶"][u"病变位置"]:
                    ZYBZ[28].setChecked(True)
                else:
                    ZYBZ[28].setChecked(False)
                if u"右上" in data[u"主要病灶"][u"病变位置"]:
                    ZYBZ[29].setChecked(True)
                else:
                    ZYBZ[29].setChecked(False)
                if u"右中" in data[u"主要病灶"][u"病变位置"]:
                    ZYBZ[30].setChecked(True)
                else:
                    ZYBZ[30].setChecked(False)
                if u"右下" in data[u"主要病灶"][u"病变位置"]:
                    ZYBZ[31].setChecked(True)
                else:
                    ZYBZ[31].setChecked(False)

            # 其他征象
            QTZX = list(self.ui.qtzx.children())

            if True:
                if u"小叶间隔增厚" in data[u"其他征象"]:
                    QTZX[1].setChecked(True)
                else:
                    QTZX[1].setChecked(False)
                if u"支气管壁增厚" in data[u"其他征象"]:
                    QTZX[2].setChecked(True)
                else:
                    QTZX[2].setChecked(False)

                if u"胸膜增厚" in data[u"其他征象"]:
                    QTZX[3].setChecked(True)
                else:
                    QTZX[3].setChecked(False)
                if u"胸腔积液" in data[u"其他征象"]:
                    QTZX[4].setChecked(True)
                else:
                    QTZX[4].setChecked(False)
                if u"空气支气管征" in data[u"其他征象"]:
                    QTZX[5].setChecked(True)
                else:
                    QTZX[5].setChecked(False)
                if u"铺路石征" in data[u"其他征象"]:
                    QTZX[6].setChecked(True)
                else:
                    QTZX[6].setChecked(False)
                if u"晕征" in data[u"其他征象"]:
                    QTZX[7].setChecked(True)
                else:
                    QTZX[7].setChecked(False)

                if u"反晕征" in data[u"其他征象"]:
                    QTZX[8].setChecked(True)
                else:
                    QTZX[8].setChecked(False)
                if u"树芽征" in data[u"其他征象"]:
                    QTZX[9].setChecked(True)
                else:
                    QTZX[9].setChecked(False)
                if u"坠积效应" in data[u"其他征象"]:
                    QTZX[10].setChecked(True)
                else:
                    QTZX[10].setChecked(False)

                if u"多发性小结节" in data[u"其他征象"]:
                    QTZX[11].setChecked(True)
                else:
                    QTZX[11].setChecked(False)
                if u"小叶中心结节" in data[u"其他征象"]:
                    QTZX[12].setChecked(True)
                else:
                    QTZX[12].setChecked(False)
                if u"淋巴结肿大" in data[u"其他征象"]:
                    QTZX[13].setChecked(True)
                else:
                    QTZX[13].setChecked(False)
                if u"支气管截断" in data[u"其他征象"]:
                    QTZX[14].setChecked(True)
                else:
                    QTZX[14].setChecked(False)

            # 诊断和把握程度
            YPZD = list(self.ui.ypzd.children())

            if True:
                if data[u"阅片诊断"] == 0:
                    YPZD[1].setChecked(True)
                    YPZD[2].setChecked(False)
                elif data[u"阅片诊断"] == 1:
                    YPZD[1].setChecked(False)
                    YPZD[2].setChecked(True)
                else:
                    YPZD[1].setChecked(False)
                    YPZD[2].setChecked(False)

                ZDBW = list(self.ui.zdbw.children())
                if data[u"诊断把握"] == 0:
                    ZDBW[1].setChecked(True)
                    ZDBW[2].setChecked(False)
                    ZDBW[3].setChecked(False)
                elif data[u"诊断把握"] == 1:
                    ZDBW[1].setChecked(False)
                    ZDBW[2].setChecked(True)
                    ZDBW[3].setChecked(False)
                elif data[u"诊断把握"] == 2:
                    ZDBW[1].setChecked(False)
                    ZDBW[2].setChecked(False)
                    ZDBW[3].setChecked(True)
                else:
                    ZDBW[1].setChecked(False)
                    ZDBW[2].setChecked(False)
                    ZDBW[3].setChecked(False)

        else:

            ################################################
            ZYBZ = list(self.ui.zybz.children())

            ZYBZ[2].setChecked(False)
            ZYBZ[3].setChecked(False)
            ZYBZ[4].setChecked(False)
            ZYBZ[5].setChecked(False)
            ZYBZ[6].setChecked(False)
            ZYBZ[7].setChecked(False)
            ZYBZ[8].setChecked(False)
            ZYBZ[9].setChecked(False)
            ZYBZ[10].setChecked(False)

            ZYBZ[12].setChecked(False)
            ZYBZ[13].setChecked(False)
            ZYBZ[14].setChecked(False)
            ZYBZ[15].setChecked(False)

            ZYBZ[17].setChecked(False)
            ZYBZ[18].setChecked(False)
            ZYBZ[19].setChecked(False)
            ZYBZ[20].setChecked(False)

            ZYBZ[22].setChecked(False)
            ZYBZ[23].setChecked(False)
            ZYBZ[24].setChecked(False)
            ZYBZ[25].setChecked(False)

            ZYBZ[27].setChecked(False)
            ZYBZ[28].setChecked(False)
            ZYBZ[29].setChecked(False)
            ZYBZ[30].setChecked(False)
            ZYBZ[31].setChecked(False)

            ################################################

            QTZX = list(self.ui.qtzx.children())

            QTZX[1].setChecked(False)
            QTZX[2].setChecked(False)
            QTZX[3].setChecked(False)
            QTZX[4].setChecked(False)
            QTZX[5].setChecked(False)
            QTZX[6].setChecked(False)
            QTZX[7].setChecked(False)

            QTZX[8].setChecked(False)
            QTZX[9].setChecked(False)
            QTZX[10].setChecked(False)
            QTZX[11].setChecked(False)
            QTZX[12].setChecked(False)
            QTZX[13].setChecked(False)
            QTZX[14].setChecked(False)

            ################################################

            YPZD = list(self.ui.ypzd.children())
            YPZD[1].setChecked(False)
            YPZD[2].setChecked(False)

            ################################################

            ZDBW = list(self.ui.zdbw.children())
            ZDBW[1].setChecked(False)
            ZDBW[2].setChecked(False)
            ZDBW[3].setChecked(False)

        pass

    def saveCurrentPage(self):
        """点击保存按钮"""
        # id
        file_dir = self.fileDirSelector.currentPath
        sample_id = self.spinbox.value

        # 主要病灶
        ZYBZ = list(self.ui.zybz.children())
        n_ZYBZ = dict()
        cur_list = []
        for z in ZYBZ:
            if str(z.__class__) == "<class 'PythonQt.QtGui.QLabel'>":
                if DICT[z.objectName] not in n_ZYBZ:
                    n_ZYBZ[DICT[z.objectName]] = []
                cur_list = n_ZYBZ[DICT[z.objectName]]
            elif str(z.__class__) == "<class 'PythonQt.QtGui.QCheckBox'>" and z.checked:
                cur_list.append(DICT[z.objectName])

        # 其他征象
        QTZX = list(self.ui.qtzx.children())
        n_QTZX = list()
        for z in QTZX:
            if str(z.__class__) == "<class 'PythonQt.QtGui.QCheckBox'>" and z.checked:
                n_QTZX.append(DICT[z.objectName])

        # 诊断和把握程度
        YPZD = list(self.ui.ypzd.children())
        if YPZD[2].checked:
            n_YPZD = 1
        else:
            n_YPZD = 0

        ZDBW = list(self.ui.zdbw.children())
        if ZDBW[1].checked:
            n_ZDBW = 0
        elif ZDBW[2].checked:
            n_ZDBW = 1
        else:
            n_ZDBW = 2

        # 同步数据
        self.res[str(sample_id)] = {
            u"主要病灶": n_ZYBZ,
            u"其他征象": n_QTZX,
            u"阅片诊断": n_YPZD,
            u"诊断把握": n_ZDBW,
        }

        # 序列化和存盘
        sample_json = json.dumps(
            self.res,
            sort_keys=True,
            ensure_ascii=False
        )

        #import sys
        # reload sys
        # sys.setdefaultencoding('utf-8')

        if hasattr(self, "txt"):
            txt_path = self.fileDirSelector.currentPath + '/result.txt'
            self.txt = open(txt_path, 'w')
            # self.txt.write(codecs.BOM_UTF8)
            self.txt.write(sample_json)
            self.txt.close()

        pass

    def BBSM_SingleCheck(self):
        checkBox = self.sender()

        ZYBZ = list(self.ui.zybz.children())
        ZYBZ[16].setChecked(False)
        ZYBZ[17].setChecked(False)
        ZYBZ[18].setChecked(False)
        ZYBZ[19].setChecked(False)
        checkBox.setChecked(True)

        pass

    pass
