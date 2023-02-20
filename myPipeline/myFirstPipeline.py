import pymel.core as pm
import os
from myPipeline import importFromPipeline
from myPipeline import substanceImporter
from myPipeline import sceneCheck
from maya import cmds


class PipelineTools:
    def __init__(self):
        # finding master pipeline
        self.DIRECTORY = os.path.join(pm.internalVar(userAppDir=True), "pipeline")
        self.PROPS = []
        if os.path.exists(self.DIRECTORY):
            print('Master Pipeline Found!')
        else:
            raise IOError("No Master Pipeline Found. Contact Support")
        self.buildMenu()
        self.importUi = importFromPipeline.ImportUI()
        self.subUi = substanceImporter.SubImportUI()
        self.sceneCheck = sceneCheck.SceneCheckUI()

    def commitToMaster(self, *args):
        currentScene = cmds.file(q=True, sn=True)
        propFile = currentScene.split('/')[-1]
        prop = propFile.split('_')[0]
        key = propFile.split('_')[1]
        if self.sceneCheck.testAll():
            # creates new scene under master pipeline
            masterDir = os.path.join(self.DIRECTORY, 'Master', prop, '%s_%s' % (prop, key))
            if not os.path.exists(masterDir):
                os.mkdir(masterDir)
            cmds.file(rename=os.path.join(masterDir, "%s.ma" % prop))
            cmds.file(save=True, type='mayaAscii')
            cmds.file(currentScene, open=True)
            print("successfully committed %s to master %s pipeline" % (prop, key))
        else:
            cmds.warning("Scene Check Failed, can not commit to master.")

    def incrementScene(self, is_master=False, *args):
        changesToSave = cmds.file(q=True, modified=True)
        sceneDir = cmds.file(q=True, exn=True)
        sceneDir = os.path.split(sceneDir)[0]
        print(sceneDir)
        if changesToSave:
            if is_master:
                # Todo: make this useful
                print("I can't increment master files yet.")
            else:
                currentScene = cmds.file(q=True, sn=True)
                currentFile = currentScene.split('/')[-1]
                if len(currentFile.split('_')) < 3:
                    cmds.file(rename='%s_000.ma' % currentFile.split('.')[0])
                    cmds.file(save=True, type='mayaAscii')
                else:
                    version = currentFile.split('_')[-1]  # 001.ma
                    version = version.split('.')[0]  # 001
                    version = version.strip('0')  # 1
                    if not version:
                        newVersion = 1
                    else:
                        newVersion = int(version) + 1
                    newVersion = '{:03d}'.format(newVersion)
                    filename = currentFile.split('_')[0] + '_' + currentFile.split('_')[1]
                    cmds.file(rename='%s_%s.%s' % (os.path.join(sceneDir, filename), newVersion, 'ma'))
                    cmds.file(save=True, type='mayaAscii')
                    print("successfully incremented %s to version %s" % (filename, newVersion))
        else:
            cmds.warning("No Changes to Save.")

    def buildMenu(self):
        # Declaring names and finding parents
        mainWindow = pm.language.melGlobals['gMainWindow']
        menuObj = 'PipelineToolsMenu'
        menuLbl = 'Pipeline'
        # if Menu already exists, delete
        if pm.menu(menuObj, label=menuLbl, exists=True, parent=mainWindow):
            pm.deleteUI(pm.menu(menuObj, e=True, deleteAllItems=True))
        # Create menu items
        PipelineToolsMenu = pm.menu(menuObj, label=menuLbl, parent=mainWindow, tearOff=True)
        pm.menuItem(label='Tools', subMenu=True, parent=PipelineToolsMenu, tearOff=True)
        pm.menuItem(label='Material Importer', command=lambda *args, **kwargs: self.subUi.show())
        pm.menuItem(label='Increment Scene', command=self.incrementScene)
        pm.menuItem(label='Scene Checker', command=lambda *args, **kwargs: self.sceneCheck.show())
        pm.menuItem(label="Import From Master", parent=PipelineToolsMenu,
                    command=lambda *args, **kwargs: self.importUi.show())
        pm.menuItem(label='Commit To Master', parent=PipelineToolsMenu, command=self.commitToMaster)
