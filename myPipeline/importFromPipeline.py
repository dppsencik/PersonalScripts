from PySide2 import QtWidgets, QtCore, QtGui
import os
import pymel.core as pm
import maya.cmds as cmds
import shutil

DIRECTORY = os.path.join(pm.internalVar(userAppDir=True), "pipeline")
PROPS = []
for item in os.scandir(os.path.join(DIRECTORY, "Props")):
    PROPS.append(item)


class ImportFromPipeline:

    def Import(self, key, prop):
        importPath = os.path.join(DIRECTORY, 'Props', prop, '%s_%s' % (prop, key))
        if os.path.exists(importPath):
            # import workspace and open current file
            cmds.workspace(importPath, openWorkspace=True)
            importFiles = os.listdir(importPath)
            # Filter out non-maya files and get most recent save
            filteredFiles = filter(lambda file: file.endswith('.ma'), importFiles)
            filteredFiles = list(filteredFiles)
            filteredFiles.sort(reverse=True)
            cmds.file(filteredFiles[0], open=True)
            print('importing %s' % filteredFiles[0])
        else:
            self.createNewFile(key, prop)

    def createNewFile(self, key, prop):
        importKey = {
            'modeling': None,
            'texturing': 'modeling',
            'rigging': 'texturing',
            'lighting': 'rigging'
        }
        # TODO: when workspace is created, create organized files (scenes folder)
        # new workspace is created
        propName = '%s_%s' % (prop, key)
        propPath = os.path.join(DIRECTORY, 'Props', prop, propName)
        cmds.workspace(create=propPath)
        cmds.workspace(propName, newWorkspace=True)
        cmds.workspace(propPath, openWorkspace=True)

        # if not modeling department, take most recent file from master and create dept workspace
        if importKey[key]:
            masterPipeline = os.path.join(DIRECTORY, 'Master', prop, '%s_%s' % (prop, importKey[key]))
            importFiles = os.listdir(masterPipeline)
            shutil.copy2(os.path.join(masterPipeline, importFiles[0]), os.path.join(propPath, propName + '.ma'))
            print('copied from %s to %s' % (os.path.join(masterPipeline, importFiles[0]),
                                            os.path.join(propPath, propName + '.ma')))
            cmds.file(os.path.join(propPath, propName + '.ma'), open=True)
        else:
            # if modeling department, create blank scene
            cmds.file(newFile=True, f=True)
            cmds.file(rename="%s.ma" % propName)
            cmds.file(save=True, type='mayaAscii')
            print('Creating blank maya file for model.')


class ImportUI(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Model To Import")
        self.setMinimumSize(225, 185)
        self.pipeline = ImportFromPipeline()
        self.buildUI()

    def buildUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.selectPropCB = QtWidgets.QComboBox()
        for prop in PROPS:
            self.selectPropCB.addItem(prop.name)
        layout.addSpacing(15)
        layout.addWidget(self.selectPropCB)

        layout.addSpacing(25)

        modelingBtn = QtWidgets.QPushButton('Model')
        modelingBtn.clicked.connect(self.importModel)
        layout.addWidget(modelingBtn)

        textureBtn = QtWidgets.QPushButton('Texture')
        textureBtn.clicked.connect(self.importTexture)
        layout.addWidget(textureBtn)

        riggingBtn = QtWidgets.QPushButton('Rigging')
        riggingBtn.clicked.connect(self.importRigging)
        layout.addWidget(riggingBtn)

        lightBtn = QtWidgets.QPushButton('Lighting')
        lightBtn.clicked.connect(self.importLighting)
        layout.addWidget(lightBtn)

    def importModel(self):
        prop = self.selectPropCB.currentText()
        print('importModel for %s Called' % prop)
        self.pipeline.Import('modeling', prop)

    def importTexture(self):
        prop = self.selectPropCB.currentText()
        print('importTexture for %s Called' % prop)
        self.pipeline.Import('texturing', prop)

    def importRigging(self):
        prop = self.selectPropCB.currentText()
        print('importRigging for %s Called' % prop)
        self.pipeline.Import('rigging', prop)

    def importLighting(self):
        prop = self.selectPropCB.currentText()
        print('importLighting for %s Called' % prop)
        self.pipeline.Import('lighting', prop)


