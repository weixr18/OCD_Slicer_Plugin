import os
import unittest
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import logging

from slicer.util import VTKObservationMixin, arrayFromVolume

#
# CT_Annotate
#

# TODO: Hide segment showing in other views (bug)
# TODO: Add view selector
# TODO: Zooming synchronization


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
        """UI setup"""
        ScriptedLoadableModuleWidget.setup(self)

        #
        # Draw the settings layout
        #
        self.setSettingsLayOut()

        #
        # Draw segment editor widget
        #
        import qSlicerSegmentationsModuleWidgetsPythonQt
        self.editor = qSlicerSegmentationsModuleWidgetsPythonQt.qMRMLSegmentEditorWidget()
        self.editor.setMaximumNumberOfUndoStates(10)
        # Set parameter node first so that the automatic selections made when the scene is set are saved
        self.selectParameterNode()
        self.editor.setMRMLScene(slicer.mrmlScene)
        # set selectors invisible
        self.editor.setAutoShowMasterVolumeNode(False)
        self.editor.setMasterVolumeNodeSelectorVisible(False)
        self.editor.setSegmentationNodeSelectorVisible(False)
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

        #
        # Connections
        #
        self.inputSelectorV1.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.refreshLayOut)
        self.inputSelectorV2.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.refreshLayOut)
        self.inputSelectorV3.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.refreshLayOut)

        self.sliderAxial.connect("valueChanged(double)", self.sideBarMoveAxial)
        self.sliderCoronal.connect(
            "valueChanged(double)", self.sideBarMoveCoronal)
        self.sliderSagittal.connect(
            "valueChanged(double)", self.sideBarMoveSagittal)

        self.masterVolumeSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.masterVolumeChange)

        self.viewSelector.connect(
            "currentTextChanged(QString)", self.viewChange)

        #
        # Other Initials
        #

        # Set display layout
        layout = slicer.qMRMLLayoutWidget()
        layout.setMRMLScene(slicer.mrmlScene)
        layout.setLayout(
            slicer.vtkMRMLLayoutNode.SlicerLayoutThreeByThreeSliceView)
        self.refreshLayOut()

        # Select the master volume node
        self.masterVolumeChange(
            self.masterVolumeSelector.currentNode()
        )

        # debug part
        # print(self.editor.mouseTracking)
        # print(dir(slicer.app.layoutManager().sliceWidget('Red')))

    def setSettingsLayOut(self):
        """settings layout setup"""
        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Settings"
        self.layout.addWidget(parametersCollapsibleButton)
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

        # Input select & segment select
        if True:
            self.inputSelectorV1Lay = qt.QHBoxLayout()
            self.inputSelectorV1 = slicer.qMRMLNodeComboBox()
            self.inputSelectorV1.nodeTypes = ["vtkMRMLScalarVolumeNode"]
            self.inputSelectorV1.selectNodeUponCreation = True
            self.inputSelectorV1.addEnabled = False
            self.inputSelectorV1.removeEnabled = False
            self.inputSelectorV1.noneEnabled = False
            self.inputSelectorV1.showHidden = False
            self.inputSelectorV1.showChildNodeTypes = False
            self.inputSelectorV1.setMRMLScene(slicer.mrmlScene)
            self.inputSelectorV1.setToolTip("First period.")
            self.inputLableV1 = qt.QLabel()
            self.inputLableV1.setText("Input Volume 1:")
            self.inputSelectorV1Lay.addWidget(self.inputLableV1)
            self.inputSelectorV1Lay.addWidget(self.inputSelectorV1)

            self.inputSelectorS1 = slicer.qMRMLNodeComboBox()
            self.inputSelectorS1.nodeTypes = ["vtkMRMLSegmentationNode"]
            self.inputSelectorS1.selectNodeUponCreation = True
            self.inputSelectorS1.addEnabled = True
            self.inputSelectorS1.removeEnabled = True
            self.inputSelectorS1.noneEnabled = False
            self.inputSelectorS1.showHidden = False
            self.inputSelectorS1.showChildNodeTypes = False
            self.inputSelectorS1.setMRMLScene(slicer.mrmlScene)
            self.inputSelectorS1.setToolTip("Segmentation for period 1.")
            self.inputLableS1 = qt.QLabel()
            self.inputLableS1.setText("Input Segment 1:")
            self.inputSelectorV1Lay.addWidget(self.inputLableS1)
            self.inputSelectorV1Lay.addWidget(self.inputSelectorS1)
            parametersFormLayout.addRow(self.inputSelectorV1Lay)

            self.inputSelectorV2Lay = qt.QHBoxLayout()
            self.inputSelectorV2 = slicer.qMRMLNodeComboBox()
            self.inputSelectorV2.nodeTypes = ["vtkMRMLScalarVolumeNode"]
            self.inputSelectorV2.selectNodeUponCreation = True
            self.inputSelectorV2.addEnabled = False
            self.inputSelectorV2.removeEnabled = False
            self.inputSelectorV2.noneEnabled = False
            self.inputSelectorV2.showHidden = False
            self.inputSelectorV2.showChildNodeTypes = False
            self.inputSelectorV2.setMRMLScene(slicer.mrmlScene)
            self.inputSelectorV2.setToolTip("Second period.")
            self.inputLableV2 = qt.QLabel()
            self.inputLableV2.setText("Input Volume 2:")
            self.inputSelectorV2Lay.addWidget(self.inputLableV2)
            self.inputSelectorV2Lay.addWidget(self.inputSelectorV2)

            self.inputSelectorS2 = slicer.qMRMLNodeComboBox()
            self.inputSelectorS2.nodeTypes = ["vtkMRMLSegmentationNode"]
            self.inputSelectorS2.selectNodeUponCreation = True
            self.inputSelectorS2.addEnabled = True
            self.inputSelectorS2.removeEnabled = True
            self.inputSelectorS2.noneEnabled = False
            self.inputSelectorS2.showHidden = False
            self.inputSelectorS2.showChildNodeTypes = False
            self.inputSelectorS2.setMRMLScene(slicer.mrmlScene)
            self.inputSelectorS2.setToolTip("Pick the input to the algorithm.")
            self.inputLableS2 = qt.QLabel()
            self.inputLableS2.setText("Input Segment 2:")
            self.inputSelectorV2Lay.addWidget(self.inputLableS2)
            self.inputSelectorV2Lay.addWidget(self.inputSelectorS2)
            parametersFormLayout.addRow(self.inputSelectorV2Lay)

            self.inputSelectorV3Lay = qt.QHBoxLayout()
            self.inputSelectorV3 = slicer.qMRMLNodeComboBox()
            self.inputSelectorV3.nodeTypes = ["vtkMRMLScalarVolumeNode"]
            self.inputSelectorV3.selectNodeUponCreation = True
            self.inputSelectorV3.addEnabled = False
            self.inputSelectorV3.removeEnabled = False
            self.inputSelectorV3.noneEnabled = False
            self.inputSelectorV3.showHidden = False
            self.inputSelectorV3.showChildNodeTypes = False
            self.inputSelectorV3.setMRMLScene(slicer.mrmlScene)
            self.inputSelectorV3.setToolTip("Third period.")
            self.inputLableV3 = qt.QLabel()
            self.inputLableV3.setText("Input Volume 3:")
            self.inputSelectorV3Lay.addWidget(self.inputLableV3)
            self.inputSelectorV3Lay.addWidget(self.inputSelectorV3)

            self.inputSelectorS3 = slicer.qMRMLNodeComboBox()
            self.inputSelectorS3.nodeTypes = ["vtkMRMLSegmentationNode"]
            self.inputSelectorS3.selectNodeUponCreation = True
            self.inputSelectorS3.addEnabled = True
            self.inputSelectorS3.removeEnabled = True
            self.inputSelectorS3.noneEnabled = False
            self.inputSelectorS3.showHidden = False
            self.inputSelectorS3.showChildNodeTypes = False
            self.inputSelectorS3.setMRMLScene(slicer.mrmlScene)
            self.inputSelectorS3.setToolTip("Pick the input to the algorithm.")
            self.inputLableS3 = qt.QLabel()
            self.inputLableS3.setText("Input Segment 3:")
            self.inputSelectorV3Lay.addWidget(self.inputLableS3)
            self.inputSelectorV3Lay.addWidget(self.inputSelectorS3)
            parametersFormLayout.addRow(self.inputSelectorV3Lay)

        # Sliders

        self.sliderAxial = slicer.qMRMLSliderWidget()
        self.LableAxial = qt.QLabel()
        self.LableAxial.setText("Axial:")
        self.sliderLay1 = qt.QHBoxLayout()
        self.sliderLay1.addWidget(self.LableAxial)
        self.sliderLay1.addWidget(self.sliderAxial)
        parametersFormLayout.addRow(self.sliderLay1)

        self.sliderCoronal = slicer.qMRMLSliderWidget()
        self.LableCoronal = qt.QLabel()
        self.LableCoronal.setText("Coronal:")
        self.sliderLay3 = qt.QHBoxLayout()
        self.sliderLay3.addWidget(self.LableCoronal)
        self.sliderLay3.addWidget(self.sliderCoronal)
        parametersFormLayout.addRow(self.sliderLay3)

        self.sliderSagittal = slicer.qMRMLSliderWidget()
        self.LableSagittal = qt.QLabel()
        self.LableSagittal.setText("Sagittal:")
        self.sliderLay2 = qt.QHBoxLayout()
        self.sliderLay2.addWidget(self.LableSagittal)
        self.sliderLay2.addWidget(self.sliderSagittal)
        parametersFormLayout.addRow(self.sliderLay2)

        # Master Volume Select
        self.operationLay = qt.QHBoxLayout()
        self.masterVolumeSelector = slicer.qMRMLNodeComboBox()
        self.masterVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.masterVolumeSelector.selectNodeUponCreation = True
        self.masterVolumeSelector.addEnabled = False
        self.masterVolumeSelector.removeEnabled = False
        self.masterVolumeSelector.noneEnabled = False
        self.masterVolumeSelector.showHidden = False
        self.masterVolumeSelector.showChildNodeTypes = False
        self.masterVolumeSelector.setMRMLScene(slicer.mrmlScene)
        self.masterVolumeSelector.setToolTip("Select Master Volume Node")

        self.masterVolumeLabel = qt.QLabel()
        self.masterVolumeLabel.setText("Master Volume:")
        self.operationLay.addWidget(self.masterVolumeLabel)
        self.operationLay.addWidget(self.masterVolumeSelector)
        parametersFormLayout.addRow(self.operationLay)

        # view selector
        self.viewLay = qt.QHBoxLayout()
        self.viewSelector = ctk.ctkComboBox()
        self.viewSelector.addItem("Compare")
        self.viewSelector.addItem("Single")

        self.viewSelLabel = qt.QLabel()
        self.viewSelLabel.setText("Choose view:")
        self.viewLay.addWidget(self.viewSelLabel)
        self.viewLay.addWidget(self.viewSelector)
        parametersFormLayout.addRow(self.viewLay)

        pass

    def refreshLayOut(self):
        """Layout refresh"""

        inputV1 = self.inputSelectorV1.currentNode()
        inputV2 = self.inputSelectorV2.currentNode()
        inputV3 = self.inputSelectorV3.currentNode()

        inputS1 = self.inputSelectorS1.currentNode()
        inputS2 = self.inputSelectorS2.currentNode()
        inputS3 = self.inputSelectorS3.currentNode()

        # bind logic to volumes
        lm = slicer.app.layoutManager()
        redLogic = lm.sliceWidget('Red').sliceLogic()
        yellowLogic = lm.sliceWidget('Yellow').sliceLogic()
        greenLogic = lm.sliceWidget('Green').sliceLogic()

        slice4Logic = lm.sliceWidget('Slice4').sliceLogic()
        slice5Logic = lm.sliceWidget('Slice5').sliceLogic()
        slice6Logic = lm.sliceWidget('Slice6').sliceLogic()

        slice7Logic = lm.sliceWidget('Slice7').sliceLogic()
        slice8Logic = lm.sliceWidget('Slice8').sliceLogic()
        slice9Logic = lm.sliceWidget('Slice9').sliceLogic()

        # V1
        if (inputV1 != None and inputV1.GetID()):
            redLogic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV1.GetID()
            )
            yellowLogic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV1.GetID()
            )
            greenLogic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV1.GetID()
            )

        # V2
        if (inputV2 != None and inputV2.GetID()):
            slice4Logic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV2.GetID()
            )
            slice4Logic.GetSliceNode().SetOrientationToAxial()
            slice5Logic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV2.GetID()
            )
            slice5Logic.GetSliceNode().SetOrientationToCoronal()
            slice6Logic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV2.GetID()
            )
            slice6Logic.GetSliceNode().SetOrientationToSagittal()

        # V3
        if (inputV3 != None and inputV3.GetID()):
            slice7Logic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV3.GetID()
            )
            slice7Logic.GetSliceNode().SetOrientationToAxial()
            slice8Logic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV3.GetID()
            )
            slice8Logic.GetSliceNode().SetOrientationToCoronal()
            slice9Logic.GetSliceCompositeNode().SetBackgroundVolumeID(
                inputV3.GetID()
            )
            slice9Logic.GetSliceNode().SetOrientationToSagittal()

        # S1
        if (inputS1 != None and inputS1.GetID()):
            redLogic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS1.GetID()
            )
            yellowLogic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS1.GetID()
            )
            greenLogic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS1.GetID()
            )

        # S2
        if (inputS2 != None and inputS2.GetID()):
            slice4Logic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS2.GetID()
            )
            slice5Logic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS2.GetID()
            )
            slice6Logic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS2.GetID()
            )

        # S3
        if (inputS3 != None and inputS3.GetID()):
            slice7Logic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS3.GetID()
            )
            slice8Logic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS3.GetID()
            )
            slice9Logic.GetSliceCompositeNode().SetForegroundVolumeID(
                inputS3.GetID()
            )

        slicer.util.resetSliceViews()

        if inputV1 and inputV2 and inputV3 and inputV1.GetID() and inputV2.GetID() and inputV3.GetID():

            # Assuming Aligned
            arr1 = arrayFromVolume(inputV1)
            origin = inputV1.GetOrigin()
            spacing = inputV1.GetSpacing()

            self.sliderAxial.minimum = 0 * spacing[2] + origin[2]
            self.sliderCoronal.minimum = - \
                arr1.shape[1] * spacing[1] + origin[1]
            self.sliderSagittal.minimum = -arr1.shape[2] * \
                spacing[0] + origin[0]

            self.sliderAxial.maximum = arr1.shape[0] * \
                spacing[2] + origin[2]
            self.sliderCoronal.maximum = 0 * spacing[1] + origin[1]
            self.sliderSagittal.maximum = 0 * spacing[0] + origin[0]

        else:
            pass

        pass

    def viewChange(self, option):
        """change the view to 3*3 or only one"""
        option = str(option)
        layout = slicer.qMRMLLayoutWidget()
        layout.setMRMLScene(slicer.mrmlScene)

        if (option == "Compare"):
            layout.setLayout(
                slicer.vtkMRMLLayoutNode.SlicerLayoutThreeByThreeSliceView
            )
            self.refreshLayOut()
        else:
            layout.setLayout(
                slicer.vtkMRMLLayoutNode.SlicerLayoutTabbedSliceView
            )
            self.refreshLayOut()

    def masterVolumeChange(self, currentNode):
        """set the master volume for segmentation"""

        self.editor.setMasterVolumeNode(currentNode)

        nodeID = currentNode.GetID()
        if self.inputSelectorV1.currentNodeID == nodeID:

            self.editor.setSegmentationNode(
                self.inputSelectorS1.currentNode()
            )
        elif self.inputSelectorV2.currentNodeID == nodeID:
            self.editor.setSegmentationNode(
                self.inputSelectorS2.currentNode()
            )
        elif self.inputSelectorV3.currentNodeID == nodeID:
            self.editor.setSegmentationNode(
                self.inputSelectorS3.currentNode()
            )
        pass

    def sideBarMoveAxial(self, index):
        """Axial move"""
        lm = slicer.app.layoutManager()
        redLogic = lm.sliceWidget('Red').sliceLogic()
        slice4Logic = lm.sliceWidget('Slice4').sliceLogic()
        slice7Logic = lm.sliceWidget('Slice7').sliceLogic()

        redLogic.SetSliceOffset(index)
        slice4Logic.SetSliceOffset(index)
        slice7Logic.SetSliceOffset(index)
        pass

    def sideBarMoveCoronal(self, index):
        """Coronal move"""
        lm = slicer.app.layoutManager()
        greenLogic = lm.sliceWidget('Green').sliceLogic()
        slice5Logic = lm.sliceWidget('Slice5').sliceLogic()
        slice8Logic = lm.sliceWidget('Slice8').sliceLogic()

        greenLogic.SetSliceOffset(index)
        slice5Logic.SetSliceOffset(index)
        slice8Logic.SetSliceOffset(index)
        pass

    def sideBarMoveSagittal(self, index):
        """Sagittal move"""
        lm = slicer.app.layoutManager()
        yellowLogic = lm.sliceWidget('Yellow').sliceLogic()
        slice6Logic = lm.sliceWidget('Slice6').sliceLogic()
        slice9Logic = lm.sliceWidget('Slice9').sliceLogic()

        yellowLogic.SetSliceOffset(index)
        slice6Logic.SetSliceOffset(index)
        slice9Logic.SetSliceOffset(index)
        pass

    """
    DON'T EDIT CODE BELOW !!
    """

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
        """
        layoutManager = slicer.app.layoutManager()
        # Use first background volume node in any of the displayed layouts
        for layoutName in layoutManager.sliceViewNames():
            compositeNode = self.getCompositeNode(layoutName)
            if compositeNode.GetBackgroundVolumeID():
                return compositeNode.GetBackgroundVolumeID()
        """
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
