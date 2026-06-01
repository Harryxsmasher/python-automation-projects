# =========================================================
# VRED Qt XR Object Move Controller
# With Numeric Keypad for Manual Entry (FIXED)
# =========================================================

from PySide2 import QtWidgets, QtCore
from vrScenegraph import *

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
MAIN_GROUP_NAME = "MainGroup"

TIMER_INTERVAL = 30
SPEED_INTERVAL = 100
POSITION_REFRESH = 60

MIN_SPEED = 0.2
MAX_SPEED = 50.0
SPEED_STEP = 0.2

axisSpeed = {"X": 2.0, "Y": 2.0, "Z": 2.0}

mainGroup = None
targetNode = None
activeAxis = "X"

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

def setAxisValue(axis, value):
    if not targetNode:
        return
    x, y, z = targetNode.getTranslation()
    if axis == "X":
        x = value
    elif axis == "Y":
        y = value
    elif axis == "Z":
        z = value
    targetNode.setTranslation(x, y, z)

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
        self.setMinimumWidth(460)

        mainLayout = QtWidgets.QVBoxLayout(self)

        # ---------- Object list ----------
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.itemChanged.connect(self.onVisibilityChanged)
        self.listWidget.currentItemChanged.connect(self.onSelectionChanged)
        mainLayout.addWidget(self.listWidget)

        # ---------- Axis rows ----------
        self.posLabels = {}
        self.speedLabels = {}

        self.createAxis(mainLayout, "X")
        self.createAxis(mainLayout, "Y")
        self.createAxis(mainLayout, "Z")

        # ---------- Keypad ----------
        self.createKeypad(mainLayout)

        # ---------- Origin ----------
        originBtn = QtWidgets.QPushButton("Move to Origin (0,0,0)")
        originBtn.clicked.connect(moveToOrigin)
        mainLayout.addWidget(originBtn)

        # ---------- Position refresh ----------
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
    # Selection & visibility
    # -----------------------------------------------------
    def onSelectionChanged(self, current, previous):
        global targetNode
        if current:
            targetNode = current.data(QtCore.Qt.UserRole)
            self.updatePositionLabels()

    def onVisibilityChanged(self, item):
        node = item.data(QtCore.Qt.UserRole)
        node.setActive(item.checkState() == QtCore.Qt.Checked)

    # -----------------------------------------------------
    # Axis rows
    # -----------------------------------------------------
    def createAxis(self, layout, axis):
        row = QtWidgets.QHBoxLayout()

        minus = QtWidgets.QPushButton(f"-{axis}")
        plus  = QtWidgets.QPushButton(f"+{axis}")

        posLabel = QtWidgets.QLabel(f"{axis}: 0.00")
        posLabel.setFixedWidth(90)
        posLabel.mousePressEvent = lambda e, a=axis: self.setActiveAxis(a)
        self.posLabels[axis] = posLabel

        self.speedLabels[axis] = QtWidgets.QLabel()
        self.updateSpeedLabel(axis)

        speedUp = QtWidgets.QPushButton("Speed +")
        speedDown = QtWidgets.QPushButton("Speed -")

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

        su = QtCore.QTimer(self)
        sd = QtCore.QTimer(self)
        su.setInterval(SPEED_INTERVAL)
        sd.setInterval(SPEED_INTERVAL)

        su.timeout.connect(lambda a=axis: self.adjustSpeed(a, +SPEED_STEP))
        sd.timeout.connect(lambda a=axis: self.adjustSpeed(a, -SPEED_STEP))

        speedUp.pressed.connect(su.start)
        speedUp.released.connect(su.stop)
        speedDown.pressed.connect(sd.start)
        speedDown.released.connect(sd.stop)

        row.addWidget(minus)
        row.addWidget(posLabel)
        row.addWidget(plus)
        row.addWidget(self.speedLabels[axis])
        row.addWidget(speedUp)
        row.addWidget(speedDown)

        layout.addLayout(row)

    def setActiveAxis(self, axis):
        global activeAxis
        activeAxis = axis
        self.axisDisplay.setText(f"Editing: {axis}")

    # -----------------------------------------------------
    # Keypad ✅ FIXED
    # -----------------------------------------------------
    def createKeypad(self, layout):
        box = QtWidgets.QGroupBox("Numeric Entry")
        v = QtWidgets.QVBoxLayout(box)

        self.axisDisplay = QtWidgets.QLabel("Editing: X")
        self.inputField = QtWidgets.QLineEdit()
        self.inputField.setReadOnly(True)

        v.addWidget(self.axisDisplay)
        v.addWidget(self.inputField)

        grid = QtWidgets.QGridLayout()
        buttons = [
            "7","8","9",
            "4","5","6",
            "1","2","3",
            "0",".","-"
        ]

        for i, t in enumerate(buttons):
            b = QtWidgets.QPushButton(t)
            # ✅ FIX: accept Qt signal args safely
            b.clicked.connect(lambda *args, x=t: self.inputField.insert(x))
            grid.addWidget(b, i // 3, i % 3)

        clearBtn = QtWidgets.QPushButton("Clear")
        enterBtn = QtWidgets.QPushButton("ENTER")

        clearBtn.clicked.connect(self.inputField.clear)
        enterBtn.clicked.connect(self.applyKeypadValue)

        v.addLayout(grid)
        v.addWidget(clearBtn)
        v.addWidget(enterBtn)

        layout.addWidget(box)

    def applyKeypadValue(self):
        try:
            value = float(self.inputField.text())
            setAxisValue(activeAxis, value)
            self.inputField.clear()
        except ValueError:
            pass

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------
    def adjustSpeed(self, axis, delta):
        axisSpeed[axis] = max(MIN_SPEED, min(MAX_SPEED, axisSpeed[axis] + delta))
        self.updateSpeedLabel(axis)

    def updateSpeedLabel(self, axis):
        self.speedLabels[axis].setText(f"{axis} speed: {axisSpeed[axis]:.1f}")

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
    print("✅ Controller with numeric keypad loaded successfully")