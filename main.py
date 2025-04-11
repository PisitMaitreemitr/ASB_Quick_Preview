from PySide6.QtWidgets import *
from PySide6.QtCore import *
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import os
import subprocess
import shutil

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QMainWindow)

class MyWindow(QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super().__init__(parent)
        self.setWindowTitle("ASB Quick Preview")
        self.setMinimumWidth(300)

        self.minframe = cmds.playbackOptions(q=True, min=True)
        self.maxframe = cmds.playbackOptions(q=True, max=True)
        self.currentPath = cmds.file(q=1,f=1,exn=1)
        self.currentDir, self.currentFileName = os.path.split(self.currentPath)
        self.currentDir = f'{self.currentDir}'

        self.camera = 'persp'
        for vp in cmds.getPanel(type="modelPanel"):
            self.camera = cmds.modelEditor(vp,q=1,av=1,cam=1)  

        self.current_fps = mel.eval('currentTimeUnitToFPS')
        self.width = cmds.getAttr("defaultResolution.width")
        self.height = cmds.getAttr("defaultResolution.height")
        self.build_ui()

    def build_ui(self):
        # layout = QtWidgets.QVBoxLayout(self)
        # label = QtWidgets.QLabel("🎉 Hello from PySide6!")
        # button = QtWidgets.QPushButton("Click Me")
        # layout.addWidget(label)
        # layout.addWidget(button)
        self.previewRange()
        self.imageSize()
        self.displayColor()
        self.location()
        self.frameRate()
        self.overlay()
        
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.previewGroup)
        mainLayout.addWidget(self.imageGroup)
        mainLayout.addWidget(self.displayGroup)
        mainLayout.addLayout(self.locationLayout)
        mainLayout.addWidget(self.framerateGroup)
        mainLayout.addWidget(self.overlayGroup)

    def previewRange(self):
        # preview range widget
        self.activeTimeSegmentRB = QRadioButton('Active Time Segment')
        self.customRangeRB = QRadioButton('Custom Range:')
        self.minRangeSB = QSpinBox()
        self.toTextLB = QLabel('to')
        self.maxRangeSB = QSpinBox()

        # preview range layout
        previewLayout = QVBoxLayout()
        customRangeLayout = QHBoxLayout()

        self.previewGroup = QGroupBox('Preview Range')

        #setting
        self.minRangeSB.setMinimum(0)
        self.minRangeSB.setMaximum(1000000)
        self.maxRangeSB.setMinimum(0)
        self.maxRangeSB.setMaximum(1000000)

        self.minRangeSB.setValue(self.minframe)
        self.maxRangeSB.setValue(self.maxframe)
        self.activeTimeSegmentRB.setChecked(True)
        self.minRangeSB.setEnabled(False)
        self.toTextLB.setEnabled(False)
        self.maxRangeSB.setEnabled(False)

        #set signal
        self.activeTimeSegmentRB.clicked.connect(self.previewOptionClick)
        self.customRangeRB.clicked.connect(self.previewOptionClick)
        
        previewLayout.addWidget(self.activeTimeSegmentRB)
        previewLayout.addWidget(self.customRangeRB)
        previewLayout.addLayout(customRangeLayout)

        customRangeLayout.addWidget(self.minRangeSB)
        customRangeLayout.addWidget(self.toTextLB)
        customRangeLayout.addWidget(self.maxRangeSB)

        self.previewGroup.setLayout(previewLayout)

    def imageSize(self):
        self.percentLB = QLabel('Percent of Output:')
        self.percentSB = QSpinBox()
        self.resolutionLB = QLabel('Resolution:')
        self.resolutionDesLB = QLabel('{}X{}'.format(self.width, self.height))

        imageLayout = QVBoxLayout()
        percentLayout = QHBoxLayout()
        resolutionLayout = QHBoxLayout()

        self.imageGroup = QGroupBox('Image Size')

        self.percentSB.setMaximum(100)
        self.percentSB.setMinimum(0)
        self.percentSB.setValue(100)

        percentLayout.addWidget(self.percentLB)
        percentLayout.addWidget(self.percentSB)

        resolutionLayout.addWidget(self.resolutionLB)
        resolutionLayout.addWidget(self.resolutionDesLB)

        imageLayout.addLayout(percentLayout)
        imageLayout.addLayout(resolutionLayout)
        self.imageGroup.setLayout(imageLayout)

    def displayColor(self):
        self.objectColorRB = QRadioButton('Object Color')
        self.materialColorRB = QRadioButton('Material Color')

        self.defaultShadingRB = QRadioButton('Default Shading')
        self.facetsRB = QRadioButton('Facets')
        self.boundingBoxRB = QRadioButton('Bounding Box')
        self.hiddenLinesRB = QRadioButton('Hidden Lines')
        self.flatColorRB = QRadioButton('Flat Color')

        displayLayout = QVBoxLayout()

        self.displayGroup = QGroupBox('Display Color')

        self.objectColorRB.clicked.connect(self.displayOptionClick)
        self.materialColorRB.clicked.connect(self.displayOptionClick)
        self.defaultShadingRB.clicked.connect(self.displayOptionClick)
        self.facetsRB.clicked.connect(self.displayOptionClick)
        self.boundingBoxRB.clicked.connect(self.displayOptionClick)
        self.hiddenLinesRB.clicked.connect(self.displayOptionClick)
        self.flatColorRB.clicked.connect(self.displayOptionClick)

        self.materialColorRB.setChecked(True)
        self.displayOptionClick()

        displayLayout.addWidget(self.objectColorRB)
        displayLayout.addWidget(self.materialColorRB)

        displayLayout.addWidget(self.defaultShadingRB)
        displayLayout.addWidget(self.facetsRB)
        displayLayout.addWidget(self.boundingBoxRB)
        displayLayout.addWidget(self.hiddenLinesRB)
        displayLayout.addWidget(self.flatColorRB)

        self.displayGroup.setLayout(displayLayout)

    def location(self):
        self.animationFolderRB = QRadioButton('Save Preview to Animation folder')
        self.customPathRB = QRadioButton('Custom Path')
        self.pathInputLE = QLineEdit()
        self.exploreBT = QPushButton('...')
        self.makePreviewBT = QPushButton('Make Preview')

        locationOptionLayout = QVBoxLayout()
        pathSelectLayout = QHBoxLayout()
        self.locationLayout = QVBoxLayout()

        self.locationGroup = QGroupBox('Location')

        self.customPathRB.setChecked(True)
        self.makePreviewBT.setFixedHeight(50)
        self.exploreBT.setFixedWidth(40)

        self.pathInputLE.setText(self.currentDir)

        self.exploreBT.clicked.connect(self.open_file_dialog)
        self.animationFolderRB.clicked.connect(self.locationOptionClick)
        self.customPathRB.clicked.connect(self.locationOptionClick)
        self.makePreviewBT.clicked.connect(self.playblast)

        locationOptionLayout.addWidget(self.animationFolderRB)
        locationOptionLayout.addWidget(self.customPathRB)
        pathSelectLayout.addWidget(self.pathInputLE)
        pathSelectLayout.addWidget(self.exploreBT)

        self.locationGroup.setLayout(locationOptionLayout)

        self.locationLayout.addWidget(self.locationGroup)
        self.locationLayout.addLayout(pathSelectLayout)
        self.locationLayout.addWidget(self.makePreviewBT)

    def frameRate(self):
        self.convertFPS_CB = QCheckBox('Convert to 12 FPS')
        framerateLayout = QVBoxLayout()
        self.framerateGroup = QGroupBox('Frame rate')

        framerateLayout.addWidget(self.convertFPS_CB)
        self.framerateGroup.setLayout(framerateLayout) 

    def overlay(self):
        self.safeFrameCB = QCheckBox('Safe Frame')
        self.frameNumbersCB = QCheckBox('Frame Number')
        self.cameraCB = QCheckBox('Camera/View Name')

        overlayLayout = QVBoxLayout()
        self.overlayGroup = QGroupBox('Overlay')

        overlayLayout.addWidget(self.safeFrameCB)
        overlayLayout.addWidget(self.frameNumbersCB)
        overlayLayout.addWidget(self.cameraCB)

        self.overlayGroup.setLayout(overlayLayout)

    def previewOptionClick(self):
        if self.activeTimeSegmentRB.isChecked():
            self.minRangeSB.setEnabled(False)
            self.maxRangeSB.setEnabled(False)
            self.toTextLB.setEnabled(False)
        else:
            self.minRangeSB.setEnabled(True)
            self.maxRangeSB.setEnabled(True)
            self.toTextLB.setEnabled(True)
        # self.isCustomRange = !self.isCustomRange

    def displayOptionClick(self):
        if self.objectColorRB.isChecked():
            cmds.modelEditor('modelPanel4', edit=True, da="smoothShaded")
            cmds.modelEditor('modelPanel4', edit=True, dtx=False)
            cmds.modelEditor('modelPanel4', edit=True, udm=False)
            cmds.modelEditor('modelPanel4', edit=True, wos=False)

        if self.materialColorRB.isChecked():
            cmds.modelEditor('modelPanel4', edit=True, da="smoothShaded")
            cmds.modelEditor('modelPanel4', edit=True, dtx=True)
            cmds.modelEditor('modelPanel4', edit=True, udm=False)
            cmds.modelEditor('modelPanel4', edit=True, wos=False)

        if self.defaultShadingRB.isChecked():
            cmds.modelEditor('modelPanel4', edit=True, da="smoothShaded")
            cmds.modelEditor('modelPanel4', edit=True, udm=True)
            cmds.modelEditor('modelPanel4', edit=True, dtx=False)
            cmds.modelEditor('modelPanel4', edit=True, wos=False)

        if self.facetsRB.isChecked():
            cmds.modelEditor('modelPanel4', edit=True, da="smoothShaded")
            cmds.modelEditor('modelPanel4', edit=True, wos=True)
            cmds.modelEditor('modelPanel4', edit=True, dtx=False)
            cmds.modelEditor('modelPanel4', edit=True, udm=False)

        if self.boundingBoxRB.isChecked():
            cmds.modelEditor('modelPanel4', edit=True, da="boundingBox")
            cmds.modelEditor('modelPanel4', edit=True, dtx=False)
            cmds.modelEditor('modelPanel4', edit=True, udm=False)
            cmds.modelEditor('modelPanel4', edit=True, wos=False)

        if self.hiddenLinesRB.isChecked():
            cmds.modelEditor('modelPanel4', edit=True, da="wireframe")
            cmds.modelEditor('modelPanel4', edit=True, dtx=False)
            cmds.modelEditor('modelPanel4', edit=True, udm=False)
            cmds.modelEditor('modelPanel4', edit=True, wos=False)

        if self.flatColorRB.isChecked():
            cmds.modelEditor('modelPanel4', edit=True ,da="flatShaded")
            cmds.modelEditor('modelPanel4', edit=True, dtx=False)
            cmds.modelEditor('modelPanel4', edit=True, udm=False)
            cmds.modelEditor('modelPanel4', edit=True, wos=False)

    def locationOptionClick(self):
        if self.animationFolderRB.isChecked():
            self.pathInputLE.setEnabled(False)
            self.exploreBT.setEnabled(False)
        else:
            self.pathInputLE.setEnabled(True)
            self.exploreBT.setEnabled(True)

    def open_file_dialog(self):
        # Open a file dialog to select a file
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.pathInputLE.setText(directory)

    def playblast(self):
        self.outputDir = ''
        minframe = 0
        maxframe = 0
        panel = cmds.getPanel(type="modelPanel")
        if self.safeFrameCB.isChecked():
            cmds.camera(self.camera, e=True, displaySafeAction=True)
            cmds.camera(self.camera, e=True, displaySafeTitle=True)
        else:
            cmds.camera(self.camera, e=True, displaySafeAction=False)
            cmds.camera(self.camera, e=True, displaySafeTitle=False)
            
        if self.animationFolderRB.isChecked():
            self.outputDir = self.currentDir
        else:
            self.outputDir = self.pathInputLE.text()

        if self.convertFPS_CB.isChecked():
            self.framerate = 12
        else:
            self.framerate = self.current_fps

        if self.customRangeRB.isChecked():
            minframe = self.minRangeSB.value()
            maxframe = self.maxRangeSB.value()
        else:
            minframe = self.minframe
            maxframe = self.maxframe

        if self.framerate == 0.0:
            self.framerate = 24

        cmds.playblast(
            startTime=minframe, 
            endTime=maxframe, 
            format="image", 
            filename= '{}/{}/'.format(self.outputDir,self.currentFileName.replace('.ma','_playblast')) + self.currentFileName.replace('.ma','_frame'), 
            viewer=False, 
            compression="png", 
            widthHeight=(self.width, self.height),  # Set resolution
            percent=self.percentSB.value(),
            clearCache=True, 
            forceOverwrite=True,
            showOrnaments=True
        )

        filename = self.currentFileName.replace('.ma','')
        image_sequence_path = "%s/%s_playblast/%s"%(self.outputDir,filename,filename)
        drawtext_filters = []
        if self.frameNumbersCB.isChecked():
            drawtext_filters.append(f"drawtext=text='Frame\\: %{{n}}':x=20:y=40:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.5")
        
        if self.cameraCB.isChecked():
            drawtext_filters.append(f"drawtext=text='Camera\\: {self.camera}':x=20:y=80:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5")
        filters = ",".join(drawtext_filters)

        i = 1
        videoOutput = "%s/%s_v%04d.mp4"%(self.outputDir,filename,i)
        while os.path.exists(videoOutput):
            videoOutput = "%s/%s_v%04d.mp4"%(self.outputDir,filename,i)
            i+=1

        if not filters is "":
            ffmpeg_command = [
                "ffmpeg", 
                "-framerate", str(self.framerate), 
                "-start_number", "1",
                "-i", image_sequence_path + "_frame.%04d.png",
                "-vf", filters,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                videoOutput
            ]
        else:
            ffmpeg_command = [
                "ffmpeg", 
                "-framerate", str(self.framerate), 
                "-start_number", "1",
                "-i", image_sequence_path + "_frame.%04d.png",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                videoOutput
            ]

        # Run the FFmpeg command
        process = subprocess.Popen(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr with stdout
            universal_newlines=True,   # Text output (instead of bytes)
            bufsize=1                  # Line-buffered
        )
        for line in process.stdout:
            print(line.strip())

        process.stdout.close()
        process.wait()

        shutil.rmtree('{}/{}/'.format(self.outputDir,self.currentFileName.replace('.ma','_playblast')))
        os.startfile(videoOutput)
def show_ui():
    global my_ui
    try:
        my_ui.close()
        my_ui.deleteLater()
    except:
        pass
    my_ui = MyWindow()
    my_ui.show()
