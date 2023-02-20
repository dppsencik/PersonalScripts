from maya import cmds
import os
from PySide2 import QtWidgets, QtCore, QtGui


class SubImporter:

    def createMayaMaterial(self, path, attrs):
        createdFileNodes = {
            'baseColor': '',
            'metalness': '',
            'roughness': '',
            'emissive': '',
            'bump': '',
            'opacity': '',
        }
        folderName = path.split('/')[-1]
        mat = cmds.shadingNode('blinn', asShader=True, name='%s_SHD' % folderName)
        # Creates all needed file nodes for given images
        for a in attrs:
            if not attrs[a]:
                continue
            else:
                if type(attrs[a]) == str:
                    createdFileNodes[a] = self.createFileTexture(path, attrs[a])
                else:
                    pass
            """**Use this section to add specific settings or reroute connections**"""
        # baseColor
        if createdFileNodes['baseColor']:
            cmds.connectAttr('%s.outColor' % createdFileNodes['baseColor'], '%s.color' % mat)

        # metalness
        if createdFileNodes['metalness']:
            cmds.connectAttr('%s.outColor.outColorR' % createdFileNodes['metalness'], '%s.reflectivity' % mat)
        # roughness
        if createdFileNodes['roughness']:
            cmds.connectAttr('%s.outColor.outColorR' % createdFileNodes['roughness'], '%s.specularRollOff' % mat)
        # emissive
        if createdFileNodes['emissive']:
            cmds.connectAttr('%s.outColor' % createdFileNodes['emissive'], '%s.incandescence' % mat)
        # bump
        if createdFileNodes['bump']:
            bumpNode = cmds.shadingNode('bump2d', asUtility=True, name='%s_BMP' % attrs['bump'].split('.')[0])
            cmds.setAttr('%s.alphaIsLuminance' % createdFileNodes['bump'], True)
            if attrs['isHeightNormal']:
                cmds.setAttr('%s.bumpInterp' % bumpNode, 1)
            cmds.connectAttr('%s.outAlpha' % createdFileNodes['bump'], '%s.bumpValue' % bumpNode)
            cmds.connectAttr('%s.outNormal' % bumpNode, '%s.normalCamera' % mat)
        # opacity
        if createdFileNodes['opacity']:
            cmds.connectAttr('%s.outColor' % createdFileNodes['opacity'], '%s.transparency' % mat)

        print("inserted!")

    def createFileTexture(self, path, entry):
        #  Function for creating the File [texture] node as maya does
        filename = entry.split('.')[0]
        fileNode = cmds.shadingNode('file', asTexture=True, isColorManaged=True, name='%s_tx' % filename)
        texNode = cmds.shadingNode('place2dTexture', asUtility=True, name='%s_p2d' % filename)
        cmds.connectAttr('%s.coverage' % texNode, '%s.coverage' % fileNode, force=True)
        cmds.connectAttr('%s.rotateFrame' % texNode, '%s.rotateFrame' % fileNode, force=True)
        cmds.connectAttr('%s.mirrorU' % texNode, '%s.mirrorU' % fileNode, force=True)
        cmds.connectAttr('%s.mirrorV' % texNode, '%s.mirrorV' % fileNode, force=True)
        cmds.connectAttr('%s.stagger' % texNode, '%s.stagger' % fileNode, force=True)
        cmds.connectAttr('%s.wrapU' % texNode, '%s.wrapU' % fileNode, force=True)
        cmds.connectAttr('%s.wrapV' % texNode, '%s.wrapV' % fileNode, force=True)
        cmds.connectAttr('%s.repeatUV' % texNode, '%s.repeatUV' % fileNode, force=True)
        cmds.connectAttr('%s.offset' % texNode, '%s.offset' % fileNode, force=True)
        cmds.connectAttr('%s.rotateUV' % texNode, '%s.rotateUV' % fileNode, force=True)
        cmds.connectAttr('%s.noiseUV' % texNode, '%s.noiseUV' % fileNode, force=True)
        cmds.connectAttr('%s.vertexUvOne' % texNode, '%s.vertexUvOne' % fileNode, force=True)
        cmds.connectAttr('%s.vertexUvTwo' % texNode, '%s.vertexUvTwo' % fileNode, force=True)
        cmds.connectAttr('%s.vertexUvThree' % texNode, '%s.vertexUvThree' % fileNode, force=True)
        cmds.connectAttr('%s.vertexCameraOne' % texNode, '%s.vertexCameraOne' % fileNode, force=True)
        cmds.connectAttr('%s.outUV' % texNode, '%s.uv' % fileNode, force=True)
        cmds.connectAttr('%s.outUvFilterSize' % texNode, '%s.uvFilterSize' % fileNode, force=True)
        cmds.setAttr('%s.fileTextureName' % fileNode,  os.path.join(path, entry), type="string")
        return fileNode

    def createAiImage(self, path, entry):
        filename = entry.split('.')[0]
        fileNode = cmds.shadingNode('aiImage', asTexture=True, isColorManaged=True, name='%s_aiImage' % filename)
        cmds.setAttr('%s.filename' % fileNode, os.path.join(path, entry), type="string")
        return fileNode

    def createArnoldMaterial(self, path, attrs):
        createdFileNodes = {
            'baseColor': '',
            'metalness': '',
            'roughness': '',
            'emissive': '',
            'bump': '',
            'opacity': '',
        }
        folderName = path.split('/')[-1]
        mat = cmds.shadingNode('aiStandardSurface', asShader=True, name='%s_SHD' % folderName)
        # Creates all needed file nodes for given images
        for a in attrs:
            if not attrs[a]:
                continue
            else:
                if type(attrs[a]) == str:
                    createdFileNodes[a] = self.createAiImage(path, attrs[a])
                else:
                    pass


        """**Use this section to add specific settings or reroute connections**"""
        # baseColor
        if createdFileNodes['baseColor']:
            cmds.connectAttr('%s.outColor' % createdFileNodes['baseColor'], '%s.baseColor' % mat)

        # metalness
        if createdFileNodes['metalness']:
            cmds.connectAttr('%s.outColor.outColorR' % createdFileNodes['metalness'], '%s.metalness' % mat)
        # roughness
        if createdFileNodes['roughness']:
            cmds.connectAttr('%s.outColor.outColorR' % createdFileNodes['roughness'], '%s.diffuseRoughness' % mat)
        # emissive
        if createdFileNodes['emissive']:
            cmds.connectAttr('%s.outColor' % createdFileNodes['emissive'], '%s.emissionColor' % mat)
            cmds.connectAttr('%s.outColor.outColorR' % createdFileNodes['emissive'], '%s.emission' % mat)
        # bump
        if attrs['isHeightNormal']:
            normalNode = cmds.shadingNode('aiNormalMap', asUtility=True, name='%s_NRM' % attrs['bump'].split('.')[0])
            cmds.connectAttr('%s.outColor' % createdFileNodes['bump'], '%s.input' % normalNode)
            cmds.connectAttr('%s.outValue' % normalNode, '%s.normalCamera' % mat)
        else:
            if createdFileNodes['bump']:
                bumpNode = cmds.shadingNode('aiBump2d', asUtility=True)
                cmds.connectAttr('%s.outAlpha' % createdFileNodes['bump'], '%s.bumpMap' % bumpNode)
                cmds.connectAttr('%s.outValue' % bumpNode, '%s.normalCamera' % mat)
        # opacity
        if createdFileNodes['opacity']:
            cmds.connectAttr('%s.outColor.outColorR' % createdFileNodes['opacity'], '%s.transmission' % mat)

        print("inserted!")


class SubImportUI(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):

        self.attrs = {
            'baseColor': '',
            'metalness': '',
            'roughness': '',
            'emissive': '',
            'bump': '',
            'opacity': '',
        }
        self.path = None
        self.importer = SubImporter()
        super().__init__()
        # TODO:Window Title isn't being set properly
        self.buildUI()

    def buildUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Creating the bottom buttons
        importBtn = QtWidgets.QPushButton('Load Images')
        importBtn.clicked.connect(self.populateImages)
        layout.addWidget(importBtn)

        # Creating the scroll area for image selection
        scrollWidget = QtWidgets.QWidget()
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        scrollLayout = QtWidgets.QGridLayout(scrollWidget)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)
        layout.addWidget(scrollArea)

        # Creating the combo boxes and adding to scroll area
        self.baseColorCB = QtWidgets.QComboBox()
        self.baseColorCB.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        scrollLayout.addWidget(self.baseColorCB, 0, 1)
        self.metalnessCB = QtWidgets.QComboBox()
        scrollLayout.addWidget(self.metalnessCB, 1, 1)
        self.roughnessCB = QtWidgets.QComboBox()
        scrollLayout.addWidget(self.roughnessCB, 2, 1)
        self.emissiveCB = QtWidgets.QComboBox()
        scrollLayout.addWidget(self.emissiveCB, 3, 1)
        self.bumpCB = QtWidgets.QComboBox()
        scrollLayout.addWidget(self.bumpCB, 4, 1)
        self.opacityCB = QtWidgets.QComboBox()
        scrollLayout.addWidget(self.opacityCB, 5, 1)

        # Creating the text labels for the Combo Boxes
        baseColorTxt = QtWidgets.QLabel('Color:')
        scrollLayout.addWidget(baseColorTxt, 0, 0)
        metalnessTxt = QtWidgets.QLabel('Metalness:')
        scrollLayout.addWidget(metalnessTxt, 1, 0)
        roughnessTxt = QtWidgets.QLabel('Roughness:')
        scrollLayout.addWidget(roughnessTxt, 2, 0)
        emissiveTxt = QtWidgets.QLabel('Emissive:')
        scrollLayout.addWidget(emissiveTxt, 3, 0)
        heightTxt = QtWidgets.QLabel('Height:')
        scrollLayout.addWidget(heightTxt, 4, 0)
        opacityTxt = QtWidgets.QLabel('Opacity:')
        scrollLayout.addWidget(opacityTxt, 5, 0)

        self.arnoldCheck = QtWidgets.QCheckBox('Create Arnold Shader?')
        self.arnoldCheck.setChecked(True)
        layout.addWidget(self.arnoldCheck)

        self.heightCheck = QtWidgets.QCheckBox('Is Height A Normal Map?')
        layout.addWidget(self.heightCheck)

        applyBtn = QtWidgets.QPushButton("Create Material")
        applyBtn.clicked.connect(self.createConnections)
        layout.addWidget(applyBtn)

    def populateImages(self):
        # Gets current Maya project directory and asks user for folder in which to import images.
        mayaProjPath = cmds.workspace(expandName='sourceimages')
        self.path = QtWidgets.QFileDialog.getExistingDirectory(caption="Select Folder to Import",
                                                               options=QtWidgets.QFileDialog.Option.DontUseNativeDialog,
                                                               dir=mayaProjPath)
        # Ensures no error when user closes file dialog box
        if self.path:
            # Clears previous items as user selects new directory
            self.baseColorCB.clear()
            self.roughnessCB.clear()
            self.metalnessCB.clear()
            self.emissiveCB.clear()
            self.bumpCB.clear()
            self.opacityCB.clear()

            self.opacityCB.addItem(None)
            self.bumpCB.addItem(None)
            self.emissiveCB.addItem(None)
            self.roughnessCB.addItem(None)
            self.metalnessCB.addItem(None)
            self.baseColorCB.addItem(None)
            # Scan user-defined directory and add all image files to CB for user selection
            with os.scandir(self.path) as it:
                for entry in it:
                    if entry.name.endswith(('.jpg', '.png', '.tiff')) and not entry.name.startswith('.'):
                        self.baseColorCB.addItem(entry.name)
                        self.metalnessCB.addItem(entry.name)
                        self.roughnessCB.addItem(entry.name)
                        self.emissiveCB.addItem(entry.name)
                        self.bumpCB.addItem(entry.name)
                        self.opacityCB.addItem(entry.name)

                        # for convenience of user, checks file names and populates CBs
                        if "basecolor" in entry.name:
                            self.baseColorCB.setCurrentText(entry.name)
                        if "metalness" in entry.name:
                            self.metalnessCB.setCurrentText(entry.name)
                        if "roughness" in entry.name:
                            self.roughnessCB.setCurrentText(entry.name)
                        if "emissive" in entry.name:
                            self.emissiveCB.setCurrentText(entry.name)
                        if "bump" in entry.name:
                            self.bumpCB.setCurrentText(entry.name)
                        if "opacity" in entry.name:
                            self.opacityCB.setCurrentText(entry.name)

    def createConnections(self):
        # Get all CB texts and pass them to a dict
        if not self.path:
            cmds.warning("Please select a folder to import by clicking the load images button.")
        else:
            attrs = {
                'isHeightNormal': self.heightCheck.isChecked(),
                'baseColor': self.baseColorCB.currentText(),
                'metalness': self.metalnessCB.currentText(),
                'roughness': self.roughnessCB.currentText(),
                'emissive': self.emissiveCB.currentText(),
                'bump': self.bumpCB.currentText(),
                'opacity': self.opacityCB.currentText()
                }
            if self.arnoldCheck.isChecked():
                self.importer.createArnoldMaterial(self.path, attrs)
            else:
                self.importer.createMayaMaterial(self.path, attrs)

            self.close()
