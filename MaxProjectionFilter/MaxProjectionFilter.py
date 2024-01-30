import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
#
# MaxProjectionFilter
#

class MaxProjectionFilter(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "MaxProjectionFilter" # TODO make this more human readable by adding spaces
    self.parent.categories = ["FHKTools"]
    self.parent.dependencies = []
    self.parent.contributors = ["C. Menard"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
Version 0.5.0:\nThis module claculates the maximum intensity projection for a given volume. All 3 axis can be 
used for he projection with a given kernel size
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """

""" # replace with organization, grant and thanks.

#
# MaxProjectionFilterWidget
#

class MaxProjectionFilterWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

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
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input volume." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.renameEnabled = True    
    self.outputSelector.noneEnabled = False
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    # kernel size of projection
    #
    self.kernelSize = qt.QWidget()
    self.kernelSizeLayout = qt.QGridLayout(self.kernelSize)
    self.kernelSize = qt.QSpinBox()
    self.kernelSize.maximum = 25
    self.kernelSize.value = 8
    self.kernelSize.setAlignment(qt.Qt.AlignLeft)   
    self.kernelSize.setToolTip( "choose the kernel size for the filter along the axis" )
    #self.kernelSizeLayout.addWidget(self.kernelSize, 0, 0)
    parametersFormLayout.addRow("Kernel Size ", self.kernelSize)
    
    # axis used count
    #
    self.axis = qt.QWidget()
    self.axisLayout = qt.QGridLayout(self.axis)
    self.axis = qt.QSpinBox()
    self.axis.maximum = 2
    self.axis.value = 1  # axial
    self.axis.setToolTip( "0 = axial\n1 = coronal\n2 = sagital " )
    self.axis.setAlignment(qt.Qt.AlignLeft)   
    #self.axisLayout.addWidget(self.axis, 0, 0)
    parametersFormLayout.addRow("Axis  ", self.axis)
    
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = MaxProjectionFilterLogic()
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), 
        self.outputSelector.currentNode(), 
        self.kernelSize.value, 
        self.axis.value)

#
# MaxProjectionFilterLogic
#

class MaxProjectionFilterLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
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
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def run(self, inputVolume, outputVolume, kernelSize, mode):
    """
    Run the actual algorithm
    """
        
    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    outputVolume.SetOrigin( inputVolume.GetOrigin())
    outputVolume.SetSpacing( inputVolume.GetSpacing());
    ijkToRAS = vtk.vtkMatrix4x4() 
    inputVolume.GetIJKToRASMatrix(ijkToRAS) 
    outputVolume.SetIJKToRASMatrix(ijkToRAS) 
   
    #get numpy arrayFromVolume
    nparray = slicer.util.arrayFromVolume(inputVolume).copy()
    dim = nparray.shape

    kernelStep = int(kernelSize/2)
    newData = np.empty((dim[0],dim[1],dim[2]), dtype=nparray.dtype)

    if mode == 0:
        # sagital
        for x in range(kernelStep, dim[0] - kernelStep):
            newData[x,:,:] = nparray[x-kernelStep:x+kernelStep,:,:].max(0)
            
    elif mode == 1:
        # axial
        for y in range(kernelStep, dim[1] - kernelStep):
            newData[:,y,:] = nparray[:,y-kernelStep:y+kernelStep,:].max(1)       
    else:
        #coronal
        for z in range(kernelStep, dim[2] - kernelStep):
            newData[:,:,z] = nparray[:,:,z-kernelStep:z+kernelStep].max(2)

    nparray[:] = newData[:]
    #outputVolume.Modified()
    slicer.util.updateVolumeFromArray(outputVolume,nparray)
    
    slicer.util.setSliceViewerLayers(background=outputVolume)
    
    logging.info('Processing completed')

    return True


class MaxProjectionFilterTest(ScriptedLoadableModuleTest):
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
    self.test_MaxProjectionFilter1()

  def test_MaxProjectionFilter1(self):
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
    logic = MaxProjectionFilterLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
