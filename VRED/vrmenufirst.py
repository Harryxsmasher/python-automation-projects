from PySide6 import QtWidgets, QtCore
from vrScenegraph import *

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
TARGET_NODE_NAME = "Box"
MOVE_STEP = 10.0  # mm per click

# -------------------------------------------------
# XR PAGE WIDGET
# -------------------------------------------------
class XRObjectMoveWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 16px;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 2px solid #5a5a5a;
                border-radius: 10px;
                padding: 14px;
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

        title = QtWidgets.QLabel("Object Move Tool")
        title.setStyleSheet("font-size: 26px;")
        layout.addWidget(title)

        # --- Position display ---
        self.posLabel = QtWidgets.QLabel("X: 0.00   Y: 0.00   Z: 0.00")
        layout.addWidget(self.posLabel)

        # --- Axis controls ---
        self.createAxisControls(layout, "X")
        self.createAxisControls(layout, "Y")
        self.createAxisControls(layout, "Z")

        # --- Origin ---
        originBtn = QtWidgets.QPushButton("Move to Origin")
        originBtn.clicked.connect(self.moveToOrigin)
        layout.addWidget(originBtn)

        layout.addStretch()

        # Update position continuously
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updatePosition)
        self.timer.start(100)

    # -------------------------------------------------
    # UI Helpers
    # -------------------------------------------------
    def createAxisControls(self, parent, axis):
        label = QtWidgets.QLabel(f"Move {axis}")
        parent.addWidget(label)

        row = QtWidgets.QHBoxLayout()

        btnPlus = QtWidgets.QPushButton(f"+{axis}")
        btnMinus = QtWidgets.QPushButton(f"-{axis}")

        btnPlus.clicked.connect(lambda: self.move(axis, +MOVE_STEP))
        btnMinus.clicked.connect(lambda: self.move(axis, -MOVE_STEP))

        row.addWidget(btnPlus)
        row.addWidget(btnMinus)

        parent.addLayout(row)

    # -------------------------------------------------
    # Logic
    # -------------------------------------------------
    def getNode(self):
        nodes = findNodes(TARGET_NODE_NAME)
        return nodes[0] if nodes else None

    def move(self, axis, delta):
        node = self.getNode()
        if not node:
            return

        x, y, z = node.getTranslation()

        if axis == "X":
            x += delta
        elif axis == "Y":
            y += delta
        elif axis == "Z":
            z += delta

        node.setTranslation(x, y, z)
        self.updatePosition()

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
# XR HOME TOOL REGISTRATION
# -------------------------------------------------
tool = vrImmersiveUiService.createTool("XR_Object_Move")
tool.setText("Object Move")

widget = XRObjectMoveWidget()
tool.setViewWidget(widget)