import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import SampleData
import numpy as np
import SimpleITK as sitk
import sitkUtils

#
# HistogramLabel
#

class HistogramLabel(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "HistogramLabel" # TODO make this more human readable by adding spaces
    self.parent.categories = ["FHKTools"]
    self.parent.dependencies = []
    self.parent.contributors = ["C.Menard"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This module generates a histogram based on a given labelmap fiiting to the input scalar volume
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This module generates a histogram based on a given labelmap fiiting to the input scalar volume
""" # replace with organization, grant and thanks.

#
# HistogramLabelWidget
#

class HistogramLabelWidget(ScriptedLoadableModuleWidget):
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
    self.inputSelector.selectNodeUponCreation = False
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Scalar Volume: ", self.inputSelector)
	
	#
    # input labelvolume  selector
    #
    self.inputSelector2 = slicer.qMRMLNodeComboBox()
    self.inputSelector2.nodeTypes =["vtkMRMLLabelMapVolumeNode"]
    #self.inputSelector2.addAttribute( "vtkMRMLLabelMapVolumeNode", "LabelMap", 0 )
    self.inputSelector2.selectNodeUponCreation = False
    self.inputSelector2.addEnabled = False
    self.inputSelector2.removeEnabled = True
    self.inputSelector2.noneEnabled = True
    self.inputSelector2.showHidden = False
    self.inputSelector2.showChildNodeTypes = False
    self.inputSelector2.setMRMLScene( slicer.mrmlScene )
    self.inputSelector2.setToolTip( "Pick the label map to the algorithm." )
    parametersFormLayout.addRow("Input Label Map:", self.inputSelector2)
    
    #
    # output plotchart selector
    #
    self.plotSelector = slicer.qMRMLNodeComboBox()
    self.plotSelector.nodeTypes = ["vtkMRMLPlotChartNode"]
    self.plotSelector.selectNodeUponCreation = True
    self.plotSelector.addEnabled = True
    self.plotSelector.removeEnabled = True
    self.plotSelector.renameEnabled = True    
    self.plotSelector.noneEnabled = False
    self.plotSelector.showHidden = False
    self.plotSelector.showChildNodeTypes = False
    self.plotSelector.setMRMLScene( slicer.mrmlScene )
    self.plotSelector.setToolTip( "Plot" )
    parametersFormLayout.addRow("Plot: ", self.plotSelector)
   
    #
    # output plotseries selector
    #
    self.seriesSelector = slicer.qMRMLNodeComboBox()
    self.seriesSelector.nodeTypes = ["vtkMRMLPlotSeriesNode"]
    self.seriesSelector.selectNodeUponCreation = True
    self.seriesSelector.addEnabled = True
    self.seriesSelector.removeEnabled = True
    self.seriesSelector.renameEnabled = True    
    self.seriesSelector.noneEnabled = False
    self.seriesSelector.showHidden = False
    self.seriesSelector.showChildNodeTypes = False
    self.seriesSelector.setMRMLScene( slicer.mrmlScene )
    self.seriesSelector.setToolTip( "Series" )
    parametersFormLayout.addRow("Timeseries: ", self.seriesSelector)      

    #
    # output maskedvolume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.renameEnabled = True    
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Masked Volume: ", self.outputSelector)
           
    # input density plot
    self.densityTab = qt.QWidget()
    self.densityLayout = qt.QGridLayout(self.densityTab)    
    self.density = qt.QCheckBox() 
    self.density.toolTip = "When checked, create density map histogram" 
    self.density.checked = False 
    self.densityLayout.addWidget(self.density, 0, 0)
    parametersFormLayout.addRow("Density Histogram: ", self.density)
    
    # input cumulative plot
    self.cumulativeHist = qt.QWidget()
    #self.densityLayout = qt.QGridLayout(self.densityTab)    
    self.cumulativeHist = qt.QCheckBox() 
    self.cumulativeHist.toolTip = "When checked, create dcumulative histogram" 
    self.cumulativeHist.checked = False 
    #self.densityLayout.addWidget(self.density, 0, 0)
    parametersFormLayout.addRow("Cumulative Histogram: ", self.cumulativeHist)
    
    # bin count
    #
    self.BinTab = qt.QWidget()
    self.BinCountLayout = qt.QGridLayout(self.BinTab)
    self.BinCount = qt.QSpinBox()
    self.BinCount.maximum = 500
    self.BinCount.value = 255
    self.BinCount.setAlignment(qt.Qt.AlignLeft)   
    self.BinCountLayout.addWidget(self.BinCount, 0, 0)
    parametersFormLayout.addRow("Bins: ", self.BinCount)
    
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
    self.applyButton.enabled =  self.inputSelector.currentNode() and self.plotSelector.currentNode() and self.seriesSelector.currentNode()

  def onApplyButton(self):
    logic = HistogramLabelLogic()
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(),
        self.inputSelector2.currentNode(), 
        self.BinCount.value,
        self.density.checked,
        self.cumulativeHist.checked,
        self.outputSelector.currentNode(),
        self.plotSelector.currentNode(),
        self.seriesSelector.currentNode())

#
# HistogramLabelLogic
#

class HistogramLabelLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  mskVolumeLabel=1
   
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

  def isValidInputOutputData(self, inputVolumeNode,inputVolumeNode2, seriesNode,plotNode,outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    #if not inputVolumeNode2:
    #    logging.debug('isValidInputOutputData failed: no input volume node 2 defined')
    #    return False
    if not seriesNode:
        logging.debug('isValidInputOutputData failed: no series as output defined')
        return False
    if not plotNode:
        logging.debug('isValidInputOutputData failed: no plot as output defined')
        return False
    
    #if not outputVolumeNode:
    #    logging.debug('isValidInputOutputData failed: no output volume node defined')
    #    return False
    
    #logging.info('ids'+inputVolumeNode.GetID()+" "+outputVolumeNode.GetID())
    
    #if inputVolumeNode.GetID() == outputVolumeNode.GetID():
    #  logging.debug('isValidInputOutputData failed: input and masked output volume is the same. Create a new volume for output to avoid this error.')
    #  return False
      
    return True

  def createMaskedVolume(self,inputVolume, inputVolume2, maskedValue, outputVolume):
    mif = sitk.MaskImageFilter()			
    mif.SetOutsideValue(maskedValue)

    roiSITK  = sitkUtils.PullVolumeFromSlicer(inputVolume)
    maskSITK = sitkUtils.PullVolumeFromSlicer(inputVolume2)

    final = mif.Execute(roiSITK,maskSITK)
    sitkUtils.PushVolumeToSlicer(final,outputVolume)
    
  def calcHistogram(self, inputVolume, inputVolume2, binCount, useDensity, useCumulative):
    # Compute histogram values
    #
    volume = slicer.util.arrayFromVolume(inputVolume)
    
    if (inputVolume2):
        label = slicer.util.arrayFromVolume(inputVolume2)
        points  = np.where( label == self.mskVolumeLabel )  # or use another label number depending on what you segmented
        values  = volume[points] 						    # this will be a list of the label values
        histogram = np.histogram(values,bins=binCount,density=useDensity) # easier way works also without the masked volume
    else:
        histogram = np.histogram(volume, bins=binCount, density=useDensity)
     
    if useCumulative:
        cumhist = np.cumsum(histogram[0]*np.diff(histogram[1])),histogram[1]
        return cumhist
    else:
        return histogram
  
  def createPlot(self,histogram,plotChart,seriesNode):
    # Save results to a new table node in order to have the possibiolity to save the data
    tableName = seriesNode.GetName()+"_table"
   
    try:
        tableNode = slicer.util.getNode(tableName)
        print("table not found")
    except slicer.util.MRMLNodeNotFoundException:
        targetNode = None
        tableNode=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", tableName)
        
    slicer.util.updateTableFromArray(tableNode, histogram)
    tableNode.GetTable().GetColumn(0).SetName("Count")
    tableNode.GetTable().GetColumn(1).SetName("Intensity")

    # Create plot
    #plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "test")
    plotSeriesNode = seriesNode
    plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
    plotSeriesNode.SetXColumnName("Intensity")
    plotSeriesNode.SetYColumnName("Count")
    plotSeriesNode.SetLineWidth(2)
    plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
    plotSeriesNode.SetMarkerStyle(plotSeriesNode.MarkerStyleNone)
    plotSeriesNode.SetColor(0.2,0.2,0.8)
   
    # Create chart and add plot
    #plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
    plotChartNode = plotChart
    #plotChartNode.SetYAxisLogScale(True)
    plotChartNode.SetLegendVisibility(False)
    
 
    plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
    plotChartNode.XAxisRangeAutoOn()
    plotChartNode.YAxisRangeAutoOn()
    #plotChartNode.SetXAxisRange(-100.0,400.0)
    #plotChartNode.SetYAxisRange(0,2.0)
    plotChartNode.SetGridVisibility(True)
    #plotChartNode.XAxisLogScaleOn()
    # Show plot in layout
    slicer.modules.plots.logic().ShowChartInLayout(plotChartNode)    
    #slicer.util.resetSliceViews()
    
  def run(self, inputVolume, inputVolume2, binCount, useDensity, useCumulative,outputVolume, plotChart, series):
    """
    Run the actual algorithm
    """
    
    mskVolumeLabel = 1
    if not self.isValidInputOutputData(inputVolume,inputVolume2,series, plotChart,outputVolume):
      slicer.util.errorDisplay('Check the input')
      return False

    logging.info('Trying to calc Histogram')
       
    # Switch to a layout with plot automatically
    layoutManager = slicer.app.layoutManager()
    layoutWithPlot = slicer.modules.plots.logic().GetLayoutWithPlot(layoutManager.layout)
    layoutManager.setLayout(layoutWithPlot)
    
    # create maskedvolume
    #
    if (outputVolume):
        self.createMaskedVolume(inputVolume, inputVolume2, 0, outputVolume)
       
    # Compute histogram values
    #
    histogram = self.calcHistogram(inputVolume, inputVolume2, binCount, useDensity, useCumulative)    
    
    # Create plot
    #
    self.createPlot(histogram,plotChart, series)
    logging.info(series.GetPlotType())
    logging.info('Processing completed')

    return True


class HistogramLabelTest(ScriptedLoadableModuleTest):
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
    self.test_HistogramLabel1()

  def test_HistogramLabel1(self):
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
    logic = HistogramLabelLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
