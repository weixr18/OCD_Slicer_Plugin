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
    "xxy": u"线性影",

    "zy": u"中央",
    "yzqgfb": u"沿支气管分布",
    "xmfj": u"胸膜附近",

    "jiejie": u"<3cm结节",
    "bankuai": u"3-10cm斑块",
    "dapian": u">10cm大片",
    "msx": u"弥散性",

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
    "xwzbtmd": u"细网状不透明度",

    "zbzzwdjj": u"主病灶之外的结节",
    "dmzc": u"动脉增粗",
    "zqgbzh": u"支气管壁增厚",
    "kqzqgz": u"空气支气管症",

    "zbzzwdjj": u"主病灶之外的结节",
    "dmzc": u"动脉增粗",
    "zqgbzh": u"支气管壁增厚",
    "kqzqgz": u"空气支气管症",

    "plsz": u"铺路石征",
    "yz_2": u"晕征",
    "fyz": u"反晕征",
    "xmzh": u"胸膜增厚",
    "xqjy": u"胸腔积液",
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
            self.onIndexChange(self.spinbox.value)

        pass

    def onIndexChange(self, sample_id):
        """加载已有结果"""

        # 载入数据
        file_dir = self.fileDirSelector.currentPath
        data_path = file_dir + "/" + str(self.spinbox.value) + ".nii"

        # TODO: release the exist volume node
        self.currentVolume = slicer.util.loadVolume(data_path)

        # 判断是否已有记录
        if not hasattr(self, "res"):
            return None
        if self.res == dict():
            return None
        if str(sample_id) not in self.res:
            return None

        data = self.res[str(sample_id)]

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
            if u"线性影" in data[u"主要病灶"][u"病变类型"]:
                ZYBZ[5].setChecked(True)
            else:
                ZYBZ[5].setChecked(False)

            if u"中央" in data[u"主要病灶"][u"病变分布"]:
                ZYBZ[7].setChecked(True)
            else:
                ZYBZ[7].setChecked(False)
            if u"沿支气管分布" in data[u"主要病灶"][u"病变分布"]:
                ZYBZ[8].setChecked(True)
            else:
                ZYBZ[8].setChecked(False)
            if u"胸膜附近" in data[u"主要病灶"][u"病变分布"]:
                ZYBZ[9].setChecked(True)
            else:
                ZYBZ[9].setChecked(False)

            if u"<3cm结节" in data[u"主要病灶"][u"病灶大小"]:
                ZYBZ[11].setChecked(True)
            else:
                ZYBZ[11].setChecked(False)
            if u"3-10cm斑块" in data[u"主要病灶"][u"病灶大小"]:
                ZYBZ[12].setChecked(True)
            else:
                ZYBZ[12].setChecked(False)
            if u">10cm大块" in data[u"主要病灶"][u"病灶大小"]:
                ZYBZ[13].setChecked(True)
            else:
                ZYBZ[13].setChecked(False)
            if u"弥散性" in data[u"主要病灶"][u"病灶大小"]:
                ZYBZ[14].setChecked(True)
            else:
                ZYBZ[14].setChecked(False)

            if u"单发" in data[u"主要病灶"][u"病变数目"]:
                ZYBZ[16].setChecked(True)
            else:
                ZYBZ[16].setChecked(False)
            if u"2-4，多发" in data[u"主要病灶"][u"病变数目"]:
                ZYBZ[17].setChecked(True)
            else:
                ZYBZ[17].setChecked(False)
            if u"5以上，多发" in data[u"主要病灶"][u"病变数目"]:
                ZYBZ[18].setChecked(True)
            else:
                ZYBZ[18].setChecked(False)
            if u"弥散性2" in data[u"主要病灶"][u"病变数目"]:
                ZYBZ[19].setChecked(True)
            else:
                ZYBZ[19].setChecked(False)

            if u"左上" in data[u"主要病灶"][u"病变位置"]:
                ZYBZ[21].setChecked(True)
            else:
                ZYBZ[21].setChecked(False)
            if u"左下" in data[u"主要病灶"][u"病变位置"]:
                ZYBZ[22].setChecked(True)
            else:
                ZYBZ[22].setChecked(False)
            if u"右上" in data[u"主要病灶"][u"病变位置"]:
                ZYBZ[23].setChecked(True)
            else:
                ZYBZ[23].setChecked(False)
            if u"右中" in data[u"主要病灶"][u"病变位置"]:
                ZYBZ[24].setChecked(True)
            else:
                ZYBZ[24].setChecked(False)
            if u"右下" in data[u"主要病灶"][u"病变位置"]:
                ZYBZ[25].setChecked(True)
            else:
                ZYBZ[25].setChecked(False)

        # 其他征象

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
        n_QTZX = dict()
        cur_list = []
        for z in QTZX:
            if str(z.__class__) == "<class 'PythonQt.QtGui.QLabel'>":
                if DICT[z.objectName] not in n_QTZX:
                    n_QTZX[DICT[z.objectName]] = []
                cur_list = n_QTZX[DICT[z.objectName]]
            elif str(z.__class__) == "<class 'PythonQt.QtGui.QCheckBox'>" and z.checked:
                cur_list.append(DICT[z.objectName])

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

        if hasattr(self, "txt"):
            txt_path = self.fileDirSelector.currentPath + '/result.txt'
            self.txt = open(txt_path, 'w')
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

#
# CT_CharacteristicLogic
#


class CT_CharacteristicLogic(ScriptedLoadableModuleLogic):

    def hasImageData(self, volumeNode):
        """This is an example logic method that
        returns true if the passed in volume
        node has valid image data
        """
        if not volumeNode:
            logging.debug('hasImageData failed: no volume node')
            return False
        if volumeNode.GetImageData() is None:
            logging.debug('hasImageData failed: no image data in volume node')
            return False
        return True

    def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
        """Validates if the output is not the same as input
        """
        if not inputVolumeNode:
            logging.debug(
                'isValidInputOutputData failed: no input volume node defined')
            return False
        if not outputVolumeNode:
            logging.debug(
                'isValidInputOutputData failed: no output volume node defined')
            return False
        if inputVolumeNode.GetID() == outputVolumeNode.GetID():
            logging.debug(
                'isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
            return False
        return True

    def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
        """
        Run the actual algorithm
        """

        if not self.isValidInputOutputData(inputVolume, outputVolume):
            slicer.util.errorDisplay(
                'Input volume is the same as output volume. Choose a different output volume.')
            return False

        logging.info('Processing started')

        # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
        cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(
        ), 'ThresholdValue': imageThreshold, 'ThresholdType': 'Above'}
        cliNode = slicer.cli.run(
            slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

        # Capture screenshot
        if enableScreenshots:
            self.takeScreenshot(
                'CT_CharacteristicTest-Start', 'MyScreenshot', -1)

        logging.info('Processing completed')

        return True


class CT_CharacteristicTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_CT_Characteristic1()

    def test_CT_Characteristic1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import SampleData
        SampleData.downloadFromURL(
            nodeNames='FA',
            fileNames='FA.nrrd',
            uris='http://slicer.kitware.com/midas3/download?items=5767')
        self.delayDisplay('Finished with download and loading')

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = CT_CharacteristicLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay('Test passed!')
