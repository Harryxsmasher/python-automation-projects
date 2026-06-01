# =========================================================
# VRED Qt XR Object Move Controller
# ✅ Shows Live X / Y / Z Position Displays
# =========================================================

from PySide2 import QtWidgets, QtCore
from vrScenegraph import *

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
MAIN_GROUP_NAME = "MainGroup"

TIMER_INTERVAL = 30
SPEED_INTERVAL = 100
POSITION_REFRESH = 60  # ms

MIN_SPEED = 0.2
MAX_SPEED = 50.0
SPEED_STEP = 0.2

axisSpeed = {"X": 2.0, "Y": 2.0, "Z": 2.0}

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
        self.setMinimumWidth(420)

        layout = QtWidgets.QVBoxLayout(self)

        # --- Object List with Checkboxes ---
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.itemChanged.connect(self.onVisibilityChanged)
        self.listWidget.currentItemChanged.connect(self.onSelectionChanged)
        layout.addWidget(self.listWidget)

        # Per‑axis UI storage
        self.speedLabels = {}
        self.posLabels = {}

        self.createAxis(layout, "X")
        self.createAxis(layout, "Y")
        self.createAxis(layout, "Z")

        originBtn = QtWidgets.QPushButton("Move to Origin (0,0,0)")
        originBtn.clicked.connect(moveToOrigin)
        layout.addWidget(originBtn)

        # Position refresh timer ✅
        self.posTimer = QtCore.QTimer(self)
        self.posTimer.setInterval(POSITION_REFRESH)
        self.posTimer.timeout.connect(self.updatePositionLabels)
        self.posTimer.start()

        self.populate()

    # -----------------------------------------------------
    # Populate list
    # -----------------------------------------------------
    def populate(self):
        self.listWidget.clear()
        for node in getChildNodes():
            item = QtWidgets.QListWidgetItem(node.getName())
            item.setCheckState(QtCore.Qt.Checked)
            item.setData(QtCore.Qt.UserRole, node)
            self.listWidget.addItem(item)

        if self.listWidget.count():
            self.listWidget.setCurrentRow(0)

    # -----------------------------------------------------
    # Selection
    # -----------------------------------------------------
    def onSelectionChanged(self, current, previous):
        global targetNode
        if current:
            targetNode = current.data(QtCore.Qt.UserRole)
            self.updatePositionLabels()

    # -----------------------------------------------------
    # Visibility toggle
    # -----------------------------------------------------
    def onVisibilityChanged(self, item):
        node = item.data(QtCore.Qt.UserRole)
        node.setActive(item.checkState() == QtCore.Qt.Checked)

    # -----------------------------------------------------
    # Axis row ✅ WITH POSITION DISPLAY
    # -----------------------------------------------------
    def createAxis(self, layout, axis):
        row = QtWidgets.QHBoxLayout()

        minus = QtWidgets.QPushButton(f"-{axis}")
        plus  = QtWidgets.QPushButton(f"+{axis}")

        posLabel = QtWidgets.QLabel(f"{axis}: 0.00")
        posLabel.setMinimumWidth(90)
        self.posLabels[axis] = posLabel

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

        plus.pressed.connect(tPlus.start)
        plus.released.connect(tPlus.stop)
        minus.pressed.connect(tMinus.start)
        minus.released.connect(tMinus.stop)

        # Speed timers
        su = QtCore.QTimer(self)
        sd = QtCore.QTimer(self)
        su.setInterval(SPEED_INTERVAL)
        sd.setInterval(SPEED_INTERVAL)

        su.timeout.connect(lambda: self.adjustSpeed(axis, +SPEED_STEP))
        sd.timeout.connect(lambda: self.adjustSpeed(axis, -SPEED_STEP))

        speedUp.pressed.connect(su.start)
        speedUp.released.connect(su.stop)
        speedDown.pressed.connect(sd.start)
        speedDown.released.connect(sd.stop)

        row.addWidget(minus)
        row.addWidget(posLabel)   # ✅ POSITION DISPLAY
        row.addWidget(plus)
        row.addWidget(speedLabel)
        row.addWidget(speedUp)
        row.addWidget(speedDown)

        layout.addLayout(row)

    # -----------------------------------------------------
    # Speed helpers
    # -----------------------------------------------------
    def adjustSpeed(self, axis, delta):
        axisSpeed[axis] = max(MIN_SPEED, min(MAX_SPEED, axisSpeed[axis] + delta))
        self.updateSpeedLabel(axis)

    def updateSpeedLabel(self, axis):
        self.speedLabels[axis].setText(f"{axis} speed: {axisSpeed[axis]:.1f}")

    # -----------------------------------------------------
    # Position display updater ✅
    # -----------------------------------------------------
    def updatePositionLabels(self):
        if not targetNode:
            return

        x, y, z = targetNode.getTranslation()
        self.posLabels["X"].setText(f"X: {x:.2f}")
        self.posLabels["Y"].setText(f"Y: {y:.2f}")
        self.posLabels["Z"].setText(f"Z: {z:.2f}")

# ---------------------------------------------------------
# Init
# ---------------------------------------------------------
if resolveMainGroup():
    ui = MoveWidget()
    ui.show()
    print("✅ Controller with live position display loaded")