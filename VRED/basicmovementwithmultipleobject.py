# =========================================================
# VRED Qt XR Object Move Controller
# Continuous Move + Continuous Speed Control (FIXED)
# =========================================================

from PySide2 import QtWidgets, QtCore
from vrScenegraph import *

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
MAIN_GROUP_NAME = "MainGroup"

TIMER_INTERVAL = 30      # ms for movement
SPEED_INTERVAL = 100     # ms for speed change

MIN_SPEED = 0.2
MAX_SPEED = 50.0
SPEED_STEP = 0.2

axisSpeed = {
    "X": 2.0,
    "Y": 2.0,
    "Z": 2.0
}

mainGroup = None
targetNode = None

# ---------------------------------------------------------
# Scene helpers
# ---------------------------------------------------------
def resolveMainGroup():
    global mainGroup
    nodes = findNodes(MAIN_GROUP_NAME)
    if not nodes:
        print("❌ Main group not found:", MAIN_GROUP_NAME)
        return False
    mainGroup = nodes[0]
    return True

def getChildNodes():
    return [mainGroup.getChild(i) for i in range(mainGroup.getNChildren())]

def setTargetNodeByName(name):
    global targetNode
    for n in getChildNodes():
        if n.getName() == name:
            targetNode = n
            print("✅ Target node:", name)
            return

def moveNode(dx, dy, dz):
    if not targetNode:
        return
    x, y, z = targetNode.getTranslation()
    targetNode.setTranslation(x + dx, y + dy, z + dz)

def moveToOrigin():
    if targetNode:
        targetNode.setTranslation(0.0, 0.0, 0.0)

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
class MoveWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("XR Object Move Controller")
        self.setMinimumWidth(360)

        layout = QtWidgets.QVBoxLayout(self)

        # Dropdown
        self.combo = QtWidgets.QComboBox()
        self.combo.currentTextChanged.connect(setTargetNodeByName)
        layout.addWidget(self.combo)

        # Axis controls
        self.speedLabels = {}

        self.createAxis(layout, "X")
        self.createAxis(layout, "Y")
        self.createAxis(layout, "Z")

        originBtn = QtWidgets.QPushButton("Move to Origin (0,0,0)")
        originBtn.clicked.connect(moveToOrigin)
        layout.addWidget(originBtn)

        self.populate()

    # -----------------------------------------------------
    # Axis row
    # -----------------------------------------------------
    def createAxis(self, layout, axis):
        row = QtWidgets.QHBoxLayout()

        minusBtn = QtWidgets.QPushButton(f"-{axis}")
        plusBtn  = QtWidgets.QPushButton(f"+{axis}")

        speedLabel = QtWidgets.QLabel()
        self.speedLabels[axis] = speedLabel
        self.updateSpeedLabel(axis)

        speedUp = QtWidgets.QPushButton("Speed +")
        speedDown = QtWidgets.QPushButton("Speed -")

        # Movement timers
        tPlus = QtCore.QTimer(self)
        tMinus = QtCore.QTimer(self)
        tPlus.setInterval(TIMER_INTERVAL)
        tMinus.setInterval(TIMER_INTERVAL)

        if axis == "X":
            tPlus.timeout.connect(lambda: moveNode(axisSpeed["X"], 0, 0))
            tMinus.timeout.connect(lambda: moveNode(-axisSpeed["X"], 0, 0))
        elif axis == "Y":
            tPlus.timeout.connect(lambda: moveNode(0, axisSpeed["Y"], 0))
            tMinus.timeout.connect(lambda: moveNode(0, -axisSpeed["Y"], 0))
        else:
            tPlus.timeout.connect(lambda: moveNode(0, 0, axisSpeed["Z"]))
            tMinus.timeout.connect(lambda: moveNode(0, 0, -axisSpeed["Z"]))

        plusBtn.pressed.connect(tPlus.start)
        plusBtn.released.connect(tPlus.stop)
        minusBtn.pressed.connect(tMinus.start)
        minusBtn.released.connect(tMinus.stop)

        # Speed timers ✅ HOLD TO CHANGE SPEED
        speedUpTimer = QtCore.QTimer(self)
        speedDownTimer = QtCore.QTimer(self)
        speedUpTimer.setInterval(SPEED_INTERVAL)
        speedDownTimer.setInterval(SPEED_INTERVAL)

        speedUpTimer.timeout.connect(lambda: self.adjustSpeed(axis, +SPEED_STEP))
        speedDownTimer.timeout.connect(lambda: self.adjustSpeed(axis, -SPEED_STEP))

        speedUp.pressed.connect(speedUpTimer.start)
        speedUp.released.connect(speedUpTimer.stop)
        speedDown.pressed.connect(speedDownTimer.start)
        speedDown.released.connect(speedDownTimer.stop)

        row.addWidget(minusBtn)
        row.addWidget(plusBtn)
        row.addWidget(speedLabel)
        row.addWidget(speedUp)
        row.addWidget(speedDown)

        layout.addLayout(row)

    # -----------------------------------------------------
    # Speed logic
    # -----------------------------------------------------
    def adjustSpeed(self, axis, delta):
        axisSpeed[axis] = max(MIN_SPEED, min(MAX_SPEED, axisSpeed[axis] + delta))
        self.updateSpeedLabel(axis)

    def updateSpeedLabel(self, axis):
        self.speedLabels[axis].setText(f"{axis} speed: {axisSpeed[axis]:.1f} mm")

    # -----------------------------------------------------
    # Populate dropdown
    # -----------------------------------------------------
    def populate(self):
        self.combo.clear()
        nodes = getChildNodes()
        for n in nodes:
            self.combo.addItem(n.getName())
        if nodes:
            setTargetNodeByName(nodes[0].getName())

# ---------------------------------------------------------
# Init
# ---------------------------------------------------------
if resolveMainGroup():
    ui = MoveWidget()
    ui.show()
    print("✅ Controller loaded (continuous move + continuous speed)")