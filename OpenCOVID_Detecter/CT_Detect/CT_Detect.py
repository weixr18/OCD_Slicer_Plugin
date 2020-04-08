# python 2.7
import os
import sys
import time

import unittest
import vtk
import qt
import ctk
import slicer
import numpy as np
from slicer.ScriptedLoadableModule import *
from slicer.util import *
import logging
import subprocess

#
# CT_Detect
#


class CT_Detect(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        # TODO make this more human readable by adding spaces
        self.parent.title = "CT_Detect"
        self.parent.categories = ["Examples"]
        self.parent.dependencies = []
        # replace with "Firstname Lastname (Organization)"
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]
        self.parent.helpText = ""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        # replace with organization, grant and thanks.
        self.parent.acknowledgementText = ""

#
# CT_DetectWidget
#


class CT_DetectWidget(ScriptedLoadableModuleWidget):

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...

        #
        # Parameters Area
        #
        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters"
        self.layout.addWidget(parametersCollapsibleButton)

        # Layout within the dummy collapsible button
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

        #
        # input volume selector
        #
        self.inputSelector = slicer.qMRMLNodeComboBox()
        self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.inputSelector.selectNodeUponCreation = True
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.noneEnabled = False
        self.inputSelector.showHidden = False
        self.inputSelector.showChildNodeTypes = False
        self.inputSelector.setMRMLScene(slicer.mrmlScene)
        self.inputSelector.setToolTip("Pick the input to the algorithm.")
        parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

        #
        # output volume selector
        #
        self.outputSelector = slicer.qMRMLNodeComboBox()
        self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.outputSelector.selectNodeUponCreation = True
        self.outputSelector.addEnabled = True
        self.outputSelector.removeEnabled = True
        self.outputSelector.noneEnabled = True
        self.outputSelector.showHidden = False
        self.outputSelector.showChildNodeTypes = False
        self.outputSelector.setMRMLScene(slicer.mrmlScene)
        self.outputSelector.setToolTip("Pick the output to the algorithm.")
        parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

        #
        # threshold value
        #
        self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
        self.imageThresholdSliderWidget.singleStep = 0.1
        self.imageThresholdSliderWidget.minimum = -100
        self.imageThresholdSliderWidget.maximum = 100
        self.imageThresholdSliderWidget.value = 0.5
        self.imageThresholdSliderWidget.setToolTip(
            "Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
        parametersFormLayout.addRow(
            "Image threshold", self.imageThresholdSliderWidget)

        #
        # check box to trigger taking screen shots for later use in tutorials
        #
        self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
        self.enableScreenshotsFlagCheckBox.checked = 0
        self.enableScreenshotsFlagCheckBox.setToolTip(
            "If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
        parametersFormLayout.addRow(
            "Enable Screenshots", self.enableScreenshotsFlagCheckBox)

        #
        # Apply Button
        #
        self.applyButton = qt.QPushButton("Apply")
        self.applyButton.toolTip = "Run the algorithm."
        self.applyButton.enabled = False
        parametersFormLayout.addRow(self.applyButton)

        # connections
        self.applyButton.connect('clicked(bool)', self.onApplyButton)
        self.inputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.outputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onSelect)

        # Add vertical spacer
        self.layout.addStretch(1)

        # Refresh Apply button state
        self.onSelect()

    def cleanup(self):
        pass

    def onSelect(self):
        self.applyButton.enabled = self.inputSelector.currentNode(
        ) and self.outputSelector.currentNode()

    def onApplyButton(self):
        logic = CT_DetectLogic()
        enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
        imageThreshold = self.imageThresholdSliderWidget.value
        logic.run(self.inputSelector.currentNode(
        ), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

#
# CT_DetectLogic
#


class CT_DetectLogic(ScriptedLoadableModuleLogic):

    def hasImageData(self, volumeNode):
        """
        Returns true if the passed in volume
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
        tic = time.time()

        npInputData = arrayFromVolume(inputVolume)
        npOutputData = self.process(npInputData)

        outputVolume.CreateDefaultDisplayNodes()
        updateVolumeFromArray(outputVolume, npOutputData)

        toc = time.time()
        logging.info('Processing completed')

        return True

    def process(self, npInputData):
        """
        Use a subprocess to cauculate the result
        """

        # Prepare the environment
        if 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']
        if 'PYTHONHOME' in os.environ:
            del os.environ['PYTHONHOME']
        if 'PYTHONNOUSERSITE' in os.environ:
            del os.environ['PYTHONNOUSERSITE']

        # TODO: pack a python environment and set the interpreter path to it
        tmp_interpreterPath = r'E:\Anaconda3\envs\COVID\python.exe'
        scriptPath = "./detect_py3.py"
        imagePath = '../__cache/__cache_input.npy'
        maskPath = ''
        workPath = r'D:\Codes\_Projects\Covid\OCD_Slicer_Plugin\OpenCOVID_Detecter\CT_Detect'

        dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])
        absScriptPath = dirPath + '/' + scriptPath
        currentEncoding = 'utf-8'
        absImagePath = dirPath + '/' + imagePath

        # TODO: add the maskpath while segment network is ready
        # and don't forget to prepare the mask before diagnose
        if isinstance(npInputData, np.ndarray):
            np.save(absImagePath, npInputData)
        else:
            return False

        # Start calculate
        proc = subprocess.Popen(
            [tmp_interpreterPath, absScriptPath,
             '--image_path', absImagePath],        # TODO: add mask path.
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            shell=True,
        )

        while proc.poll() is None:
            r = proc.stdout.readline().decode(currentEncoding)
            logging.info(r)

        if proc.poll() != 0:
            err = proc.stderr.read().decode(currentEncoding)
            logging.error(err)

        # Load output data
        outputPath = '../__cache/__cache_CAM.npy'
        absOutputPath = dirPath + '/' + outputPath
        return np.load(absOutputPath)


class CT_DetectTest(ScriptedLoadableModuleTest):
    # TODO : write a test class
    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_CT_Detect1()

    def test_CT_Detect1(self):
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
        logic = CT_DetectLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay('Test passed!')
