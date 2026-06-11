from PySide6 import QtWidgets, QtCore
from vrScenegraph import *

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
MAIN_GROUP_NAME = "MainGroup"

DEFAULT_SPEED = 10.0
SPEED_STEP = 5.0
MIN_SPEED = 1.0
MAX_SPEED = 100.0
MOVE_INTERVAL_MS = 30

# -------------------------------------------------
class XRObjectMoveWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.currentNode = None
        self.axisSpeed = {"X": 10.0, "Y": 10.0, "Z": 10.0}
        self.speedLabels = {}

        # ✅ Narrow XR panel
        self.setMaximumWidth(700)

        self.setStyleSheet("""
            QLabel { color: #e6e6e6; font-size: 14px; }
            QPushButton {
                background-color: #3a3a3a;
                border: 2px solid #5a5a5a;
                border-radius: 6px;
                padding: 7px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #ff9f40;
                color: #1e1e1e;
            }
            QListWidget {
                background-color: #262626;
                border: 2px solid #5a5a5a;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #ff9f40;
                color: #1e1e1e;
            }
            QCheckBox { font-size: 12px; }
        """)

        # ---------------- Layout ----------------
        root = QtWidgets.QHBoxLayout(self)
        root.setSpacing(8)

        self.left = QtWidgets.QVBoxLayout()
        self.rightWidget = QtWidgets.QWidget()
        self.right = QtWidgets.QVBoxLayout(self.rightWidget)

        root.addLayout(self.left, 4)
        root.addWidget(self.rightWidget, 1)

        # ---------------- LEFT ----------------
        title = QtWidgets.QLabel("Object Move Tool")
        title.setStyleSheet("font-size: 18px;")
        self.left.addWidget(title)

        self.posLabel = QtWidgets.QLabel("X: 0.00   Y: 0.00   Z: 0.00")
        self.left.addWidget(self.posLabel)

        self.createAxis("X")
        self.createAxis("Y")
        self.createAxis("Z")

        originBtn = QtWidgets.QPushButton("Move to Origin")
        originBtn.clicked.connect(self.moveToOrigin)
        self.left.addWidget(originBtn)

        toggleBtn = QtWidgets.QPushButton("📂 Objects")
        toggleBtn.clicked.connect(self.toggleObjectPanel)
        self.left.addWidget(toggleBtn)

        self.left.addStretch()

        # ---------------- RIGHT ----------------
        self.right.addWidget(QtWidgets.QLabel("Objects"))

        self.visibilityLayout = QtWidgets.QVBoxLayout()
        self.right.addLayout(self.visibilityLayout)

        self.nodeList = QtWidgets.QListWidget()
        self.nodeList.itemSelectionChanged.connect(self.onNodeSelected)
        self.right.addWidget(self.nodeList)

        self.populateNodes()

        # Position refresh
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.updatePosition)
        timer.start(100)

    # -------------------------------------------------
    def createAxis(self, axis):
        header = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(f"Move {axis}")
        speedLabel = QtWidgets.QLabel(f"Speed: {self.axisSpeed[axis]:.0f} mm")
        self.speedLabels[axis] = speedLabel

        header.addWidget(label)
        header.addStretch()
        header.addWidget(speedLabel)
        self.left.addLayout(header)

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
        self.left.addLayout(row)

    # -------------------------------------------------
    def populateNodes(self):
        self.nodeList.clear()
        while self.visibilityLayout.count():
            w = self.visibilityLayout.takeAt(0).widget()
            if w:
                w.deleteLater()

        groups = findNodes(MAIN_GROUP_NAME)
        if not groups:
            return

        group = groups[0]

        for i in range(group.getNChildren()):
            node = group.getChild(i)

            cb = QtWidgets.QCheckBox(node.getName())
            cb.setChecked(node.getActive())
            cb.stateChanged.connect(
                lambda state, n=node: self.onVisibilityToggled(n, state)
            )
            self.visibilityLayout.addWidget(cb)

            item = QtWidgets.QListWidgetItem(node.getName())
            item.setData(QtCore.Qt.UserRole, node)
            self.nodeList.addItem(item)

        if self.nodeList.count():
            self.nodeList.setCurrentRow(0)

    # -------------------------------------------------
    # ✅ FINAL VISIBILITY LOGIC (WORKS IN YOUR VRED)
    def onVisibilityToggled(self, node, state):
        if state == QtCore.Qt.Checked:
            self.showNodeFully(node)
        else:
            self.setActiveTree(node, False)

    def setActiveTree(self, node, state):
        node.setActive(state)
        for i in range(node.getNChildren()):
            self.setActiveTree(node.getChild(i), state)

    def showNodeFully(self, node):
        # Ensure parent chain is active
        p = node
        while p:
            p.setActive(True)
            p = p.getParent()

        # Ensure full subtree is active
        self.setActiveTree(node, True)

    # -------------------------------------------------
    def toggleObjectPanel(self):
        self.rightWidget.setVisible(not self.rightWidget.isVisible())

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
        delta = self.axisSpeed[axis] * direction

        if axis == "X": x += delta
        if axis == "Y": y += delta
        if axis == "Z": z += delta

        self.currentNode.setTranslation(x, y, z)

    def adjustSpeed(self, axis, delta):
        self.axisSpeed[axis] = max(
            MIN_SPEED, min(MAX_SPEED, self.axisSpeed[axis] + delta)
        )
        self.speedLabels[axis].setText(
            f"Speed: {self.axisSpeed[axis]:.0f} mm"
        )

    def moveToOrigin(self):
        if self.currentNode:
            self.currentNode.setTranslation(0, 0, 0)
            self.updatePosition()

    def updatePosition(self):
        if not self.currentNode:
            return

        x, y, z = self.currentNode.getTranslation()
        self.posLabel.setText(
            f"X: {x:.2f}   Y: {y:.2f}   Z: {z:.2f}"
        )

# -------------------------------------------------
# XR HOME TOOL
# -------------------------------------------------
tool = vrImmersiveUiService.createTool("XR_Object_Move")
tool.setText("Object Move")
tool.setViewWidget(XRObjectMoveWidget())