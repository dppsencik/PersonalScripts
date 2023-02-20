from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds
import os
import json
import pprint
"""
Features to implement:
    If a controller is put in the dir externally, there will be no screenshot. Point to a default image.
    When loaded, controllers simply go to origin. Implement a constrain to move the controllers then del constraint
    If you save a controller with existing name, it overwrites. Confirm box, warning or something.
"""


DIRECTORY = os.path.join(cmds.internalVar(userAppDir=True), "controllerLibrary")


def createDirectory(directory=DIRECTORY):
    """
    Creates given directory if it doesn't exist already.
    Args:
        directory (str) The directory to create if it doesn't exist

    """
    if not os.path.exists(directory):
        os.mkdir(directory)


class ControllerLibrary(dict):

    def save(self, name, directory=DIRECTORY, screenshot=True, **info):

        createDirectory(directory)

        path = os.path.join(directory, '%s.ma' % name)
        infoFile = os.path.join(directory, '%s.json' % name)

        info['name'] = name
        info['path'] = path

        cmds.file(rename=path)
        if cmds.ls(selection=True):
            cmds.file(force=True, type='mayaAscii', exportSelected=True)
        else:
            cmds.file(save=True, type='mayaAscii', force=True)
        if screenshot:
            info['screenshot'] = self.saveScreenshot(name, directory=directory)

        with open(infoFile, 'w') as f:
            json.dump(info, f, indent=4)

        self[name] = info

    def find(self, directory=DIRECTORY):
        self.clear()
        if not os.path.exists(directory):
            print('No Library found, please ensure it is in the correct place')
            return
        files = os.listdir(directory)
        mayaFiles = [f for f in files if f.endswith('.ma')]

        for ma in mayaFiles:
            name, ext = os.path.splitext(ma)
            path = os.path.join(directory, ma)

            infoFile = '%s.json' % name
            if infoFile in files:
                infoFile = os.path.join(directory, infoFile)
                with open(infoFile, 'r') as f:
                    info = json.load(f)
                    pprint.pprint(info)
            else:
                print("No Info found for %s" % name)
                info = {}
            info['name'] = name
            info['path'] = path
            self[name] = info

            screenshot = '%s.jpg' % name
            if screenshot in files:
                info['screenshot'] = os.path.join(directory, screenshot)

    def load(self, name):
        path = self[name]['path']
        cmds.file(path, i=True, usingNamespaces=False)

    def saveScreenshot(self, name, directory=DIRECTORY):
        path = os.path.join(directory, '%s.jpg' % name)
        cmds.viewFit()
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.playblast(completeFilename=path, forceOverwrite=True, format='image', width=200, height=200,
                       showOrnaments=False, startTime=1, endTime=1, viewer=False)
        return path


class ControllerLibraryUI(QtWidgets.QDialog):
    """
    The ControllerLibraryUI is a dialog that allows us to save and import controllers
    """
    def __init__(self):
        super(ControllerLibraryUI, self).__init__()
        self.setWindowTitle('Controller Library UI')
        # The library variable points to an instance of our controller library
        self.library = ControllerLibrary()

        # Every time instance is created, the UI is built and populated
        self.buildUI()
        self.populate()

    def buildUI(self):
        """
       This method builds out the UI
        """
        # Master Layout
        layout = QtWidgets.QVBoxLayout(self)

        # First row in the master
        saveWidget = QtWidgets.QWidget()
        saveLayout = QtWidgets.QHBoxLayout(saveWidget)
        layout.addWidget(saveWidget)

        self.saveNameField = QtWidgets.QLineEdit()
        saveLayout.addWidget(self.saveNameField)

        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.save)
        saveLayout.addWidget(saveBtn)

        # Thumbnail size parameters
        size = 64
        buffer = 12

        # This creates a visual grid of all controllers, displaying name and thumbnail
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.listWidget.setIconSize(QtCore.QSize(size, size))
        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.listWidget.setGridSize(QtCore.QSize(size+buffer, size + buffer))
        layout.addWidget(self.listWidget)

        # Bottom child widget handling bottom buttons
        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        layout.addWidget(btnWidget)

        importBtn = QtWidgets.QPushButton('Import!')
        importBtn.clicked.connect(self.load)
        btnLayout.addWidget(importBtn)

        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.populate)
        btnLayout.addWidget(refreshBtn)

        closeBtn = QtWidgets.QPushButton('Close')
        closeBtn.clicked.connect(self.close)
        btnLayout.addWidget(closeBtn)

    def populate(self):
        """This clears the list widget and repopulates based on existing disk"""
        self.listWidget.clear()
        self.library.find()

        for name, info in self.library.items():
            item = QtWidgets.QListWidgetItem(name)
            self.listWidget.addItem(item)

            screenshot = info.get('screenshot')
            if screenshot:
                icon = QtGui.QIcon(screenshot)
                item.setIcon(icon)
            item.setToolTip(pprint.pformat(info))

    def load(self):
        """Loads currently selected controller"""
        currentItem = self.listWidget.currentItem()
        if not currentItem:
            return
        name = currentItem.text()
        self.library.load(name)

    def save(self):
        """Save selected controller with given file name"""
        name = self.saveNameField.text()
        if not name.strip():
            cmds.warning("Please enter a name to save")
            return
        self.library.save(name)
        self.populate()
        self.saveNameField.setText('')


def showUI():
    """
    This shows and returns a handle of the ui
    Returns:
        QDialog

    """
    ui = ControllerLibraryUI()
    ui.show()
    return ui
