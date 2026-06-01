from PySide6 import QtWidgets, QtCore
from vrScenegraph import *

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
MAIN_GROUP_NAME = "MainGroup"
MAX_NODE_COUNT = 10

DEFAULT_SPEED = 10.0
SPEED_STEP = 5.0
MIN_SPEED = 1.0
MAX_SPEED = 100.0

MOVE_INTERVAL_MS = 30

# -------------------------------------------------
# XR PAGE WIDGET
# -------------------------------------------------
class XRObjectMoveWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.currentNode = None

        self.axisSpeed = {"X": 10.0, "Y": 10.0, "Z": 10.0}
        self.speedLabels = {}

        self.setStyleSheet("""
            QLabel { color: #e6e6e6; font-size: 16px; }
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
            }
            QListWidget {
                background-color: #262626;
                border: 2px solid #5a5a5a;
                border-radius: 8px;
                font-size: 16px;
            }
            QListWidget::item:selected {
                background-color: #ff9f40;
                color: #1e1e1e;
            }
        """)

        root = QtWidgets.QHBoxLayout(self)
        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()

        root.addLayout(left, 3)
        root.addLayout(right, 1)

        # ---------- LEFT ----------
        title = QtWidgets.QLabel("Object Move Tool")
        title.setStyleSheet("font-size: 26px;")
        left.addWidget(title)

        self.posLabel = QtWidgets.QLabel("X: 0.00   Y: 0.00   Z: 0.00")
        left.addWidget(self.posLabel)

        self.createAxis(left, "X")
        self.createAxis(left, "Y")
        self.createAxis(left, "Z")

        origin = QtWidgets.QPushButton("Move to Origin")
        origin.clicked.connect(self.moveToOrigin)
        left.addWidget(origin)

        left.addStretch()

        # ---------- RIGHT ----------
        rightTitle = QtWidgets.QLabel("Objects")
        rightTitle.setStyleSheet("font-size: 20px;")
        right.addWidget(rightTitle)

        self.nodeList = QtWidgets.QListWidget()
        self.nodeList.itemSelectionChanged.connect(self.onNodeSelected)
        right.addWidget(self.nodeList)

        self.populateNodeList()

        # ---------- REFRESH ----------
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updatePosition)
        self.timer.start(100)

    # -------------------------------------------------
    def createAxis(self, parent, axis):
        header = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(f"Move {axis}")
        speed = QtWidgets.QLabel(f"Speed: {self.axisSpeed[axis]:.0f} mm")

        self.speedLabels[axis] = speed

        header.addWidget(label)
        header.addStretch()
        header.addWidget(speed)
        parent.addLayout(header)

        row = QtWidgets.QHBoxLayout()

        plus = QtWidgets.QPushButton(f"+{axis}")
        minus = QtWidgets.QPushButton(f"-{axis}")
        sMinus = QtWidgets.QPushButton("–")
        sPlus = QtWidgets.QPushButton("+")

        tPlus = QtCore.QTimer(self)
        tMinus = QtCore.QTimer(self)

        tPlus.setInterval(MOVE_INTERVAL_MS)
        tMinus.setInterval(MOVE_INTERVAL_MS)

        tPlus.timeout.connect(lambda: self.move(axis, +1))
        tMinus.timeout.connect(lambda: self.move(axis, -1))

        plus.pressed.connect(tPlus.start)
        plus.released.connect(tPlus.stop)
        minus.pressed.connect(tMinus.start)
        minus.released.connect(tMinus.stop)

        sMinus.clicked.connect(lambda: self.adjustSpeed(axis, -SPEED_STEP))
        sPlus.clicked.connect(lambda: self.adjustSpeed(axis, +SPEED_STEP))

        row.addWidget(plus)
        row.addWidget(minus)
        row.addWidget(sMinus)
        row.addWidget(sPlus)

        parent.addLayout(row)

    # -------------------------------------------------
    def populateNodeList(self):
        self.nodeList.clear()
        groups = findNodes(MAIN_GROUP_NAME)
        if not groups:
            return

        g = groups[0]
        for i in range(min(g.getNChildren(), MAX_NODE_COUNT)):
            child = g.getChild(i)
            item = QtWidgets.QListWidgetItem(child.getName())
            item.setData(QtCore.Qt.UserRole, child)
            self.nodeList.addItem(item)

        if self.nodeList.count():
            self.nodeList.setCurrentRow(0)

    def onNodeSelected(self):
        items = self.nodeList.selectedItems()
        if items:
            self.currentNode = items[0].data(QtCore.Qt.UserRole)
            self.updatePosition()

    # -------------------------------------------------
    def move(self, axis, direction):
        if not self.currentNode:
            return

        x, y, z = self.currentNode.getTranslation()
        d = self.axisSpeed[axis] * direction

        if axis == "X": x += d
        if axis == "Y": y += d
        if axis == "Z": z += d

        self.currentNode.setTranslation(x, y, z)

    def adjustSpeed(self, axis, delta):
        self.axisSpeed[axis] = max(
            MIN_SPEED, min(MAX_SPEED, self.axisSpeed[axis] + delta)
        )
        self.speedLabels[axis].setText(f"Speed: {self.axisSpeed[axis]:.0f} mm")

    def moveToOrigin(self):
        if self.currentNode:
            self.currentNode.setTranslation(0, 0, 0)
            self.updatePosition()

    def updatePosition(self):
        if not self.currentNode:
            return

        x, y, z = self.currentNode.getTranslation()
        self.posLabel.setText(
            f"X: {x:8.2f}   Y: {y:8.2f}   Z: {z:8.2f}"
        )

# -------------------------------------------------
# XR HOME TOOL
# -------------------------------------------------
tool = vrImmersiveUiService.createTool("XR_Object_Move")
tool.setText("Object Move")
tool.setViewWidget(XRObjectMoveWidget())