import os
import unittest
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import logging

from slicer.util import VTKObservationMixin

#
# CT_Annotate
#


class CT_Annotate(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "CT_Annotate"
        self.parent.categories = ["COVID Research Tools"]
        self.parent.dependencies = []
        self.parent.contributors = ["XinRan Wei, Kaiwen Men, PeiYi Han, BoLun Liu, \
                                    WeiXiang Chen, (Tsinghua Univ.)"]
        self.parent.helpText = ""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        # replace with organization, grant and thanks.
        self.parent.acknowledgementText = ""

#
# CT_AnnotateWidget
#


class CT_AnnotateWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)

        # Members
        self.parameterSetNode = None
        self.editor = None

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Add margin to the sides
        self.layout.setContentsMargins(4, 0, 4, 0)

        #
        # Segment editor widget
        #
        import qSlicerSegmentationsModuleWidgetsPythonQt
        self.editor = qSlicerSegmentationsModuleWidgetsPythonQt.qMRMLSegmentEditorWidget()
        self.editor.setMaximumNumberOfUndoStates(10)
        # Set parameter node first so that the automatic selections made when the scene is set are saved
        self.selectParameterNode()
        self.editor.setMRMLScene(slicer.mrmlScene)
        self.layout.addWidget(self.editor)

        # Observe editor effect registrations to make sure that any effects that are registered
        # later will show up in the segment editor widget. For example, if Segment Editor is set
        # as startup module, additional effects are registered after the segment editor widget is created.
        import qSlicerSegmentationsEditorEffectsPythonQt
        # TODO: For some reason the instance() function cannot be called as a class function although it's static
        factory = qSlicerSegmentationsEditorEffectsPythonQt.qSlicerSegmentEditorEffectFactory()
        self.effectFactorySingleton = factory.instance()
        self.effectFactorySingleton.connect(
            'effectRegistered(QString)', self.editorEffectRegistered)

        # Connect observers to scene events
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene,
                         slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.EndImportEvent, self.onSceneEndImport)

    def editorEffectRegistered(self):
        self.editor.updateEffectList()

    def selectParameterNode(self):
        # Select parameter set node if one is found in the scene, and create one otherwise
        segmentEditorSingletonTag = "SegmentEditor"
        segmentEditorNode = slicer.mrmlScene.GetSingletonNode(
            segmentEditorSingletonTag, "vtkMRMLSegmentEditorNode")
        if segmentEditorNode is None:
            segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
            segmentEditorNode.SetSingletonTag(segmentEditorSingletonTag)
            segmentEditorNode = slicer.mrmlScene.AddNode(segmentEditorNode)
        if self.parameterSetNode == segmentEditorNode:
            # nothing changed
            return
        self.parameterSetNode = segmentEditorNode
        self.editor.setMRMLSegmentEditorNode(self.parameterSetNode)

    def getCompositeNode(self, layoutName):
        """ use the Red slice composite node to define the active volumes """
        count = slicer.mrmlScene.GetNumberOfNodesByClass(
            'vtkMRMLSliceCompositeNode')
        for n in range(count):
            compNode = slicer.mrmlScene.GetNthNodeByClass(
                n, 'vtkMRMLSliceCompositeNode')
            if layoutName and compNode.GetLayoutName() != layoutName:
                continue
            return compNode

    def getDefaultMasterVolumeNodeID(self):
        layoutManager = slicer.app.layoutManager()
        # Use first background volume node in any of the displayed layouts
        for layoutName in layoutManager.sliceViewNames():
            compositeNode = self.getCompositeNode(layoutName)
            if compositeNode.GetBackgroundVolumeID():
                return compositeNode.GetBackgroundVolumeID()
        # Use first background volume node in any of the displayed layouts
        for layoutName in layoutManager.sliceViewNames():
            compositeNode = self.getCompositeNode(layoutName)
            if compositeNode.GetForegroundVolumeID():
                return compositeNode.GetForegroundVolumeID()
        # Not found anything
        return None

    def enter(self):
        """Runs whenever the module is reopened
        """
        if self.editor.turnOffLightboxes():
            slicer.util.warningDisplay('Segment Editor is not compatible with slice viewers in light box mode.'
                                       'Views are being reset.', windowTitle='Segment Editor')

        # Allow switching between effects and selected segment using keyboard shortcuts
        self.editor.installKeyboardShortcuts()

        # Set parameter set node if absent
        self.selectParameterNode()
        self.editor.updateWidgetFromMRML()

        # If no segmentation node exists then create one so that the user does not have to create one manually
        if not self.editor.segmentationNodeID():
            segmentationNode = slicer.mrmlScene.GetFirstNode(
                None, "vtkMRMLSegmentationNode")
            if not segmentationNode:
                segmentationNode = slicer.mrmlScene.AddNewNodeByClass(
                    'vtkMRMLSegmentationNode')
            self.editor.setSegmentationNode(segmentationNode)
            if not self.editor.masterVolumeNodeID():
                masterVolumeNodeID = self.getDefaultMasterVolumeNodeID()
                self.editor.setMasterVolumeNodeID(masterVolumeNodeID)

    def exit(self):
        self.editor.setActiveEffect(None)
        self.editor.uninstallKeyboardShortcuts()
        self.editor.removeViewObservations()

    def onSceneStartClose(self, caller, event):
        self.parameterSetNode = None
        self.editor.setSegmentationNode(None)
        self.editor.removeViewObservations()

    def onSceneEndClose(self, caller, event):
        if self.parent.isEntered:
            self.selectParameterNode()
            self.editor.updateWidgetFromMRML()

    def onSceneEndImport(self, caller, event):
        if self.parent.isEntered:
            self.selectParameterNode()
            self.editor.updateWidgetFromMRML()

    def cleanup(self):
        self.removeObservers()
        self.effectFactorySingleton.disconnect(
            'effectRegistered(QString)', self.editorEffectRegistered)

#
# CT_AnnotateLogic
#


"""
class SegmentEditorWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    def __init__(self, parent):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)

        # Members
        self.parameterSetNode = None
        self.editor = None

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Add margin to the sides
        self.layout.setContentsMargins(4, 0, 4, 0)

        #
        # Segment editor widget
        #
        import qSlicerSegmentationsModuleWidgetsPythonQt
        self.editor = qSlicerSegmentationsModuleWidgetsPythonQt.qMRMLSegmentEditorWidget()
        self.editor.setMaximumNumberOfUndoStates(10)
        # Set parameter node first so that the automatic selections made when the scene is set are saved
        self.selectParameterNode()
        self.editor.setMRMLScene(slicer.mrmlScene)
        self.layout.addWidget(self.editor)

        # Observe editor effect registrations to make sure that any effects that are registered
        # later will show up in the segment editor widget. For example, if Segment Editor is set
        # as startup module, additional effects are registered after the segment editor widget is created.
        import qSlicerSegmentationsEditorEffectsPythonQt
        # TODO: For some reason the instance() function cannot be called as a class function although it's static
        factory = qSlicerSegmentationsEditorEffectsPythonQt.qSlicerSegmentEditorEffectFactory()
        self.effectFactorySingleton = factory.instance()
        self.effectFactorySingleton.connect(
            'effectRegistered(QString)', self.editorEffectRegistered)

        # Connect observers to scene events
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene,
                         slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.EndImportEvent, self.onSceneEndImport)

    def editorEffectRegistered(self):
        self.editor.updateEffectList()

    def selectParameterNode(self):
        # Select parameter set node if one is found in the scene, and create one otherwise
        segmentEditorSingletonTag = "SegmentEditor"
        segmentEditorNode = slicer.mrmlScene.GetSingletonNode(
            segmentEditorSingletonTag, "vtkMRMLSegmentEditorNode")
        if segmentEditorNode is None:
            segmentEditorNode = slicer.vtkMRMLSegmentEditorNode()
            segmentEditorNode.SetSingletonTag(segmentEditorSingletonTag)
            segmentEditorNode = slicer.mrmlScene.AddNode(segmentEditorNode)
        if self.parameterSetNode == segmentEditorNode:
            # nothing changed
            return
        self.parameterSetNode = segmentEditorNode
        self.editor.setMRMLSegmentEditorNode(self.parameterSetNode)

    def getCompositeNode(self, layoutName):
        #  use the Red slice composite node to define the active volumes 
        count = slicer.mrmlScene.GetNumberOfNodesByClass(
            'vtkMRMLSliceCompositeNode')
        for n in range(count):
            compNode = slicer.mrmlScene.GetNthNodeByClass(
                n, 'vtkMRMLSliceCompositeNode')
            if layoutName and compNode.GetLayoutName() != layoutName:
                continue
            return compNode

    def getDefaultMasterVolumeNodeID(self):
        layoutManager = slicer.app.layoutManager()
        # Use first background volume node in any of the displayed layouts
        for layoutName in layoutManager.sliceViewNames():
            compositeNode = self.getCompositeNode(layoutName)
            if compositeNode.GetBackgroundVolumeID():
                return compositeNode.GetBackgroundVolumeID()
        # Use first background volume node in any of the displayed layouts
        for layoutName in layoutManager.sliceViewNames():
            compositeNode = self.getCompositeNode(layoutName)
            if compositeNode.GetForegroundVolumeID():
                return compositeNode.GetForegroundVolumeID()
        # Not found anything
        return None

    def enter(self):
        # Runs whenever the module is reopened
    if self.editor.turnOffLightboxes():
        slicer.util.warningDisplay('Segment Editor is not compatible with slice viewers in light box mode.'
                                   'Views are being reset.', windowTitle='Segment Editor')

    # Allow switching between effects and selected segment using keyboard shortcuts
    self.editor.installKeyboardShortcuts()

    # Set parameter set node if absent
    self.selectParameterNode()
    self.editor.updateWidgetFromMRML()

    # If no segmentation node exists then create one so that the user does not have to create one manually
    if not self.editor.segmentationNodeID():
        segmentationNode = slicer.mrmlScene.GetFirstNode(
            None, "vtkMRMLSegmentationNode")
        if not segmentationNode:
            segmentationNode = slicer.mrmlScene.AddNewNodeByClass(
                'vtkMRMLSegmentationNode')
        self.editor.setSegmentationNode(segmentationNode)
        if not self.editor.masterVolumeNodeID():
            masterVolumeNodeID = self.getDefaultMasterVolumeNodeID()
            self.editor.setMasterVolumeNodeID(masterVolumeNodeID)

def exit(self):
    self.editor.setActiveEffect(None)
    self.editor.uninstallKeyboardShortcuts()
    self.editor.removeViewObservations()

def onSceneStartClose(self, caller, event):
    self.parameterSetNode = None
    self.editor.setSegmentationNode(None)
    self.editor.removeViewObservations()

def onSceneEndClose(self, caller, event):
    if self.parent.isEntered:
        self.selectParameterNode()
        self.editor.updateWidgetFromMRML()

def onSceneEndImport(self, caller, event):
    if self.parent.isEntered:
        self.selectParameterNode()
        self.editor.updateWidgetFromMRML()

def cleanup(self):
    self.removeObservers()
    self.effectFactorySingleton.disconnect(
        'effectRegistered(QString)', self.editorEffectRegistered)
"""


class CT_AnnotateLogic(ScriptedLoadableModuleLogic):
    """
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

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
            self.takeScreenshot('CT_AnnotateTest-Start', 'MyScreenshot', -1)

        logging.info('Processing completed')

        return True


class CT_AnnotateTest(ScriptedLoadableModuleTest):
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
        self.test_CT_Annotate1()

    def test_CT_Annotate1(self):

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
        logic = CT_AnnotateLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay('Test passed!')
