# python 2.7
# Contributors: Xinran Wei, Bolun Liu, Kaiwen Men
import os
import sys
import time

import unittest
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import *
import logging

import numpy as np
import subprocess
import socket
import sys
import pickle

#
# CT_Detect
#


class CT_Detect(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "CT_Detect"
        self.parent.categories = ["COVID Detect"]
        self.parent.dependencies = []
        self.parent.contributors = ["XinRan Wei, Kaiwen Men, PeiYi Han, BoLun Liu, \
                                    WeiXiang Chen, (Tsinghua Univ.)"]
        self.parent.helpText = ""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        # replace with organization, grant and thanks.
        self.parent.acknowledgementText = ""

#
# CT_DetectWidget
#


USE_CUDA = False


class Client():
    """Subprocess and communication"""

    def __init__(self):

        # Set up a subprocess

        # Clear the python paths
        if 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']
        if 'PYTHONHOME' in os.environ:
            del os.environ['PYTHONHOME']
        if 'PYTHONNOUSERSITE' in os.environ:
            del os.environ['PYTHONNOUSERSITE']

        tmp_interpreterPath = r'E:\Anaconda3\envs\COVID\python.exe'
        # TODO: pack a python3.6 interpreter with site-packages
        # in the release version

        scriptPath = "./server_py3.py"
        dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])
        absScriptPath = dirPath + '/' + scriptPath
        cmd_work_path = r'D:\Codes\_Projects\Covid\OCD_Slicer_Plugin'

        self.proc = subprocess.Popen(
            [tmp_interpreterPath, absScriptPath,
             "--use_cuda", str(USE_CUDA)],
            cwd=cmd_work_path,
            bufsize=1,
            shell=False,
        )
        logging.info(self.proc.pid)

        # open the socket
        time.sleep(10)

        self.serverAddress = ('127.0.0.1', 31500)
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.connect(self.serverAddress)

    def __del__(self):
        self.serverSocket.close()
        self.proc.terminate()

    def solve(self, inputData, inputInfo):
        # send data
        pack = {
            "data": inputData,
            "info": inputInfo,
        }
        self.serverSocket.send(pickle.dumps(pack, protocol=2))
        logging.info("Processing...")

        # receive data
        returnData = pickle.loads(self.serverSocket.recv(200000000))

        return returnData

    pass


class CT_DetectWidget(ScriptedLoadableModuleWidget):

    def __init__(self, parent):
        """Components initialize."""
        # father widget initialize
        ScriptedLoadableModuleWidget.__init__(self, parent)

        # client setup
        self.client = Client()
        print("Subprocess launched.")

        # logic setup
        self.logic = CT_DetectLogic()

        # state flag
        self.resultGet = False
        self.resData = False
        pass

    def setup(self):
        """Layouts initialize"""

        # Father content setup
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer)
        uiWidget = slicer.util.loadUI(
            self.resourcePath('UI/CT_Detect.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)
        self.ui.inputw.inputSelector.setMRMLScene(slicer.mrmlScene)
        self.ui.outputw.outputSelector.setMRMLScene(slicer.mrmlScene)

        # connect slots
        self.ui.gbxAction.applyButton.connect(
            'clicked(bool)',
            self.onApplyButton
        )
        self.ui.gbxAction.divideButton.connect(
            'clicked(bool)',
            self.onDivideButton
        )
        self.ui.inputw.inputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)",
            self.buttonStateChange
        )
        self.ui.outputw.outputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)",
            self.buttonStateChange
        )
        self.ui.gbxDisplay.f1.showSliderWidget.connect(
            "valueChanged(double)",
            self.showSlices
        )

        # Add vertical spacer
        self.layout.addStretch(1)

        # Refresh components states
        self.buttonStateChange()
        self.rangeInitial()

        pass

    def cleanup(self):
        self.client.__del__()
        pass

    def buttonStateChange(self):
        """reset the button accesses"""
        self.ui.applyButton.enabled = self.ui.inputw.inputSelector.currentNode(
        ) and self.ui.outputw.outputSelector.currentNode()
        self.ui.divideButton.enabled = self.resultGet
        self.ui.gbxDisplay.enabled = self.resultGet
        self.rangeInitial()

        pass

    def rangeInitial(self):
        sliceRange = self.ui.slicing.sliceRange
        sliceRange.minimum = 0
        sliceRange.maximum = arrayFromVolume(
            self.ui.inputw.inputSelector.currentNode()
        ).shape[0]

        sliceRange.minimumValue = sliceRange.minimum
        sliceRange.maximumValue = sliceRange.maximum

        spacing = self.ui.slicing.spacing.spacingBox
        spacing.minimum = 1
        spacing.maximum = 20
        spacing.value = 5

        pass

    def onApplyButton(self):
        """on apply button clicked"""

        # slicing info
        start_pos = int(self.ui.slicing.sliceRange.minimumValue)
        end_pos = int(self.ui.slicing.sliceRange.maximumValue)
        spacing = self.ui.slicing.spacing.spacingBox.value
        padding = (end_pos - start_pos) // spacing
        inputInfo = {'start_pos': start_pos,
                     'end_pos': end_pos,
                     'spacing': spacing,
                     'padding': padding,
                     }

        # run the algorithm
        self.resData = self.logic.run(self.ui.inputw.inputSelector.currentNode(),
                                      self.ui.outputw.outputSelector.currentNode(),
                                      self.client,
                                      inputInfo)
        self.resultGet = True
        self.buttonStateChange()

        # set the volume
        outputVolume = self.ui.outputw.outputSelector.currentNode()
        outputVolume.CreateDefaultDisplayNodes()
        updateVolumeFromArray(outputVolume, self.resData["slices"])

        # set the scene
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_cn = red_logic.GetSliceCompositeNode()
        red_logic.GetSliceCompositeNode().SetBackgroundVolumeID(
            outputVolume.GetID()
        )

        show = self.ui.gbxDisplay.f1.showSliderWidget
        show.maximum = self.resData["slices"].shape[0]

        # TODO: display the interpolated segmentation in the yellow/green scene.

        pass

    def onDivideButton(self):
        """we may need this."""
        pass

    def showSlices(self):
        """show the slices on the screen."""

        layer = self.ui.gbxDisplay.f1.showSliderWidget.value
        self.ui.scorelineEdit.setText(self.getScore(int(layer)))

        lm = slicer.app.layoutManager()
        redLogic = lm.sliceWidget('Red').sliceLogic()
        yellowLogic = lm.sliceWidget('Yellow').sliceLogic()
        greenLogic = lm.sliceWidget('Green').sliceLogic()
        redLogic.SetSliceOffset(layer)

        pass

    def getScore(self, layer):
        """get score from layer index"""
        if not self.resultGet:
            return 0

        if layer >= len(self.resData["slice_scores"]):
            return 0

        return self.resData["slice_scores"][layer]

    pass  # end class


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

    def run(self, inputVolume, outputVolume, client, inputInfo):

        if not self.isValidInputOutputData(inputVolume, outputVolume):
            slicer.util.errorDisplay(
                'Input volume is the same as output volume. Choose a different output volume.'
            )
            return False

        logging.info('Calculation started')
        tic = time.time()

        # get input data
        npInputData = arrayFromVolume(inputVolume)

        # send, calc and reveive output data
        npOutputData = client.solve(npInputData, inputInfo)
        toc = time.time()
        logging.info('Calculation completed. Total time:' + str(toc - tic))

        # split the segs and slices
        outShape = npOutputData["ret_slices"].shape
        npOutputData["slices"] = npOutputData["ret_slices"][:, 1, :, :]
        npOutputData["slices"].reshape([outShape[0], outShape[2], outShape[3]])
        npOutputData["segs"] = npOutputData["ret_slices"][:, 0, :, :]
        npOutputData["segs"].reshape([outShape[0], outShape[2], outShape[3]])
        del npOutputData["ret_slices"]

        # data post-processing
        npOutputData["slices"] *= 255
        npOutputData["segs"] *= 255
        npOutputData["segs"] = self.segmentInterpolation(npOutputData["segs"])

        return npOutputData

    def segmentInterpolation(self, npSeg):
        """Interpolation of the segmentation result"""
        return npSeg


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
