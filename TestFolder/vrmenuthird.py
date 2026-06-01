from PySide6 import QtWidgets, QtCore
from vrScenegraph import *

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
TARGET_NODE_NAME = "Box"

DEFAULT_SPEED = 10.0
SPEED_STEP = 5.0
MIN_SPEED = 1.0
MAX_SPEED = 100.0

MOVE_INTERVAL_MS = 30   # repeat rate while holding

# -------------------------------------------------
# XR PAGE WIDGET
# -------------------------------------------------
class XRObjectMoveWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        # Per‑axis speed (mm per tick)
        self.axisSpeed = {
            "X": DEFAULT_SPEED,
            "Y": DEFAULT_SPEED,
            "Z": DEFAULT_SPEED
        }

        # Store speed labels for live update
        self.speedLabels = {}

        self.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 16px;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 2px solid #5a5a5a;
                border-radius: 10px;
                padding: 12px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #ff9f40;
                color: #1e1e1e;
                border-color: #ff9f40;
            }
            QPushButton:pressed {
                background-color: #ff7f00;
                color: #1e1e1e;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(16)

        # Title
        title = QtWidgets.QLabel("Object Move Tool")
        title.setStyleSheet("font-size: 26px;")
        layout.addWidget(title)

        # Position display
        self.posLabel = QtWidgets.QLabel("X: 0.00   Y: 0.00   Z: 0.00")
        layout.addWidget(self.posLabel)

        # Axis controls
        self.createAxisControls(layout, "X")
        self.createAxisControls(layout, "Y")
        self.createAxisControls(layout, "Z")

        # Move to origin
        originBtn = QtWidgets.QPushButton("Move to Origin")
        originBtn.clicked.connect(self.moveToOrigin)
        layout.addWidget(originBtn)

        layout.addStretch()

        # Position refresh
        self.refreshTimer = QtCore.QTimer(self)
        self.refreshTimer.timeout.connect(self.updatePosition)
        self.refreshTimer.start(100)

    # -------------------------------------------------
    # UI helpers
    # -------------------------------------------------
    def createAxisControls(self, parent, axis):
        headerRow = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel(f"Move {axis}")
        speedLabel = QtWidgets.QLabel(f"Speed: {self.axisSpeed[axis]:.0f} mm")

        self.speedLabels[axis] = speedLabel

        headerRow.addWidget(label)
        headerRow.addStretch()
        headerRow.addWidget(speedLabel)

        parent.addLayout(headerRow)

        row = QtWidgets.QHBoxLayout()

        movePlus = QtWidgets.QPushButton(f"+{axis}")
        moveMinus = QtWidgets.QPushButton(f"-{axis}")

        speedMinus = QtWidgets.QPushButton("–")
        speedPlus = QtWidgets.QPushButton("+")

        # Timers for hold movement
        timerPlus = QtCore.QTimer(self)
        timerMinus = QtCore.QTimer(self)

        timerPlus.setInterval(MOVE_INTERVAL_MS)
        timerMinus.setInterval(MOVE_INTERVAL_MS)

        timerPlus.timeout.connect(lambda: self.move(axis, +1))
        timerMinus.timeout.connect(lambda: self.move(axis, -1))

        movePlus.pressed.connect(timerPlus.start)
        movePlus.released.connect(timerPlus.stop)

        moveMinus.pressed.connect(timerMinus.start)
        moveMinus.released.connect(timerMinus.stop)

        speedMinus.clicked.connect(lambda: self.adjustSpeed(axis, -SPEED_STEP))
        speedPlus.clicked.connect(lambda: self.adjustSpeed(axis, +SPEED_STEP))

        row.addWidget(movePlus)
        row.addWidget(moveMinus)
        row.addWidget(speedMinus)
        row.addWidget(speedPlus)

        parent.addLayout(row)

    # -------------------------------------------------
    # Logic
    # -------------------------------------------------
    def getNode(self):
        nodes = findNodes(TARGET_NODE_NAME)
        return nodes[0] if nodes else None

    def move(self, axis, direction):
        node = self.getNode()
        if not node:
            return

        x, y, z = node.getTranslation()
        delta = self.axisSpeed[axis] * direction

        if axis == "X":
            x += delta
        elif axis == "Y":
            y += delta
        elif axis == "Z":
            z += delta

        node.setTranslation(x, y, z)
        self.updatePosition()

    def adjustSpeed(self, axis, delta):
        self.axisSpeed[axis] = max(
            MIN_SPEED,
            min(MAX_SPEED, self.axisSpeed[axis] + delta)
        )
        self.speedLabels[axis].setText(
            f"Speed: {self.axisSpeed[axis]:.0f} mm"
        )

    def moveToOrigin(self):
        node = self.getNode()
        if node:
            node.setTranslation(0.0, 0.0, 0.0)
            self.updatePosition()

    def updatePosition(self):
        node = self.getNode()
        if not node:
            return

        x, y, z = node.getTranslation()
        self.posLabel.setText(
            f"X: {x:8.2f}   Y: {y:8.2f}   Z: {z:8.2f}"
        )

# -------------------------------------------------
# XR HOME TOOL
# -------------------------------------------------
tool = vrImmersiveUiService.createTool("XR_Object_Move")
tool.setText("Object Move")

widget = XRObjectMoveWidget()
tool.setViewWidget(widget)
