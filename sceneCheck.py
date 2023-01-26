from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import pprint


# List of things to check scene for:
# Make sure all objects in outliner have correct suffix
# all transforms are zero'd
# no image planes, no history

SUFFIXES = {
    "mesh": "GEO",
    "joint": "JNT",
    "camera": None,
    "nurbsCurve": "CV",
    "ambientLight": "LGT",
    "directionalLight": "LGT"
}
DEFAULT_SUFFIX = "GRP"


class SceneCheck:

    def suffixTest(self):

        # Checks scene DAG objects and their suffixes

        transforms = cmds.ls(dag=True, et=('transform', 'joint'))
        failed = []
        for obj in transforms:

            children = cmds.listRelatives(obj, children=True, fullPath=True) or []

            if len(children) == 1:
                child = children[0]
                objType = cmds.objectType(child)
            else:
                objType = cmds.objectType(obj)

            suffix = SUFFIXES.get(objType, DEFAULT_SUFFIX)
            # filtering objects that pass the test
            if not suffix or obj.endswith('_' + suffix) or obj.endswith("Shape"):
                continue
            else:
                failed.append(obj)
        if not failed:
            # Scene has passed Suffix Test!
            return True
        else:
            cmds.warning("The following objects have the incorrect suffix:")
            pprint.pprint(failed, indent=4)
            return False

    def transformTest(self):

        # Checks if the objects have frozen transforms

        transforms = cmds.ls(dag=True, et='transform')
        failed = []
        for obj in transforms:
            objType = cmds.listRelatives(obj, children=True)
            if not objType:
                continue
            objType = objType[-1]
            if cmds.objectType(objType) == 'camera':
                continue
            if cmds.objectType(objType) == 'joint' or obj.endswith('_LGT'):
                if not cmds.getAttr(obj + '.rotate') == [(0.0, 0.0, 0.0)] and \
                        cmds.getAttr(obj + '.scale') == [(1.0, 1.0, 1.0)]:
                    failed.append(obj)
            else:
                if not cmds.getAttr(obj + '.translate') == [(0.0, 0.0, 0.0)] and\
                        cmds.getAttr(obj + '.rotate') == [(0.0, 0.0, 0.0)] and\
                        cmds.getAttr(obj + '.scale') == [(1.0, 1.0, 1.0)]:
                    failed.append(obj)

        if not failed:
            # Scene has passed Transform Test!
            return True
        else:
            cmds.warning("The following objects need transforms frozen:")
            pprint.pprint(failed, indent=4)
            return False

    def tidyTest(self):

        # checking for existing reference planes

        existingPlanes = cmds.ls(et='imagePlane')
        if existingPlanes:
            cmds.warning("Please remove all image planes:")
            pprint.pprint(existingPlanes, indent=4, )
            planeCheck = False
        else:
            # No image planes found!
            planeCheck = True

        # checking for history on existing geo

        existingGeo = cmds.ls(g=True)
        failed = []
        for geo in existingGeo:
            history = cmds.listHistory(geo, pdo=True)
            if history:
                failed.append(geo)
        if not failed:
            # print("Scene has no outstanding history!")
            histCheck = True
        else:
            cmds.warning("The following objects have existing history:")
            pprint.pprint(failed, indent=4)
            histCheck = False
        if planeCheck and histCheck:
            return True
        else:
            return False


class SceneCheckUI(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scene Check Tool")
        self.setMinimumSize(165, 155)
        self.sceneCheck = SceneCheck()
        self.buildUI()

    def buildUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.suffixBtn = QtWidgets.QPushButton("Suffix Test")
        self.suffixBtn.clicked.connect(self.suffixTest)
        layout.addWidget(self.suffixBtn)

        self.transformBtn = QtWidgets.QPushButton("Transform Test")
        self.transformBtn.clicked.connect(self.transformTest)
        layout.addWidget(self.transformBtn)

        self.tidyBtn = QtWidgets.QPushButton("Tidy Test")
        self.tidyBtn.clicked.connect(self.tidyTest)
        layout.addWidget(self.tidyBtn)

        self.checkAllBtn = QtWidgets.QPushButton("Check All")
        self.checkAllBtn.clicked.connect(self.testAll)
        layout.addWidget(self.checkAllBtn)

# Each button initiates check and changes color of itself based of pass/fail

    def suffixTest(self, status=None):
        passed = self.sceneCheck.suffixTest()
        if passed:
            self.suffixBtn.setStyleSheet("background-color: green")
        else:
            self.suffixBtn.setStyleSheet("background-color: red")
        return passed

    def transformTest(self):
        passed = self.sceneCheck.transformTest()
        if passed:
            self.transformBtn.setStyleSheet("background-color: green")
        else:
            self.transformBtn.setStyleSheet("background-color: red")
        return passed

    def tidyTest(self):
        passed = self.sceneCheck.tidyTest()
        if passed:
            self.tidyBtn.setStyleSheet("background-color: green")
        else:
            self.tidyBtn.setStyleSheet("background-color: red")
        return passed

    # Essentially hits all the buttons at the same time and compares them
    def testAll(self):

        tests = [self.suffixTest(),
                 self.transformTest(),
                 self.tidyTest()]
        if all(tests):
            self.checkAllBtn.setStyleSheet("background-color: green")
            print("Passed Scene Check!")
            return True
        else:
            self.checkAllBtn.setStyleSheet("background-color: red")
            cmds.warning("Failed scene check. Check console for more details ->")



