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

        self.saveButton = self.ui.Save
        self.fileDirSelector = self.ui.FileSelect.children()[1].PathLineEdit

        # connections
        self.saveButton.connect('clicked(bool)', self.onSaveButton)
        self.fileDirSelector.connect(
            'currentPathChanged(QString)', self.onDirSelected)
        """
        self.inputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.outputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        """

        # enables
        self.saveButton.setEnabled(self.fileDirSelector.currentPath == "\n")

    def cleanup(self):
        pass

    def onDirSelected(self, file_dir):
        """文件夹选择后"""

        if file_dir is not '\n':
            self.saveButton.setEnabled(True)
            txt_path = file_dir + "/result.txt"

            if os.path.exists(txt_path):
                self.txt = open(txt_path, mode='r')
                sample_json = self.txt.read()
                self.txt.close()
                self.res = json.loads(sample_json.decode("gb2312"))
            else:
                self.txt = open(txt_path, mode='w')
                self.txt.close()
                self.res = dict()

            file_list = os.listdir(file_dir)

            n_file_list = []
            for f in file_list:
                if f[-3:] is "nii":
                    n_file_list.append(f)
            file_list = n_file_list

            print file_list
        pass

    def onSaveButton(self):
        """点击保存按钮"""

        # id
        fs = self.ui.FileSelect.children()
        file_dir = fs[1].PathLineEdit.currentPath
        sample_id = fs[2].idSpinBox.value

        # ZhuYaoBingZao
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

        # QiTaZhengXiang
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

        # ZhenDuanHeBaWo
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

        self.res[sample_id] = {
            u"主要病灶": n_ZYBZ,
            u"其他征象": n_QTZX,
            u"阅片诊断": n_YPZD,
            u"诊断把握": n_ZDBW,
        }

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
