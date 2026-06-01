# =====================================================
# VRED Qt X/Y/Z Object Move Controller (VR Compatible)
# =====================================================

from PySide2 import QtWidgets
from vrScenegraph import *

MOVE_STEP = 10.0  # mm per click

# -----------------------------------------------------
# Helper: get selected node
# -----------------------------------------------------
def getSelectedNode():
    nodes = getSelectedNodes()
    if not nodes:
        return None
    return nodes[0]

# -----------------------------------------------------
# Move helper
# -----------------------------------------------------
def moveNode(dx, dy, dz):
    node = getSelectedNode()
    if not node:
        print("No node selected")
        return

    pos = node.getTranslation()
    node.setTranslation([
        pos[0] + dx,
        pos[1] + dy,
        pos[2] + dz
    ])

# -----------------------------------------------------
# Qt Window
# -----------------------------------------------------
class MoveWidget(QtWidgets.QWidget):

    def __init__(self):
        super(MoveWidget, self).__init__()
        self.setWindowTitle("XR Object Move Controller")
        self.setMinimumWidth(220)

        layout = QtWidgets.QGridLayout(self)

        # X axis
        btnXp = QtWidgets.QPushButton("+X")
        btnXm = QtWidgets.QPushButton("-X")
        btnXp.clicked.connect(lambda: moveNode( MOVE_STEP, 0, 0))
        btnXm.clicked.connect(lambda: moveNode(-MOVE_STEP, 0, 0))

        # Y axis
        btnYp = QtWidgets.QPushButton("+Y")
        btnYm = QtWidgets.QPushButton("-Y")
        btnYp.clicked.connect(lambda: moveNode(0,  MOVE_STEP, 0))
        btnYm.clicked.connect(lambda: moveNode(0, -MOVE_STEP, 0))

        # Z axis
        btnZp = QtWidgets.QPushButton("+Z")
        btnZm = QtWidgets.QPushButton("-Z")
        btnZp.clicked.connect(lambda: moveNode(0, 0,  MOVE_STEP))
        btnZm.clicked.connect(lambda: moveNode(0, 0, -MOVE_STEP))

        # Layout
        layout.addWidget(btnXp, 0, 0)
        layout.addWidget(btnXm, 0, 1)

        layout.addWidget(btnYp, 1, 0)
        layout.addWidget(btnYm, 1, 1)

        layout.addWidget(btnZp, 2, 0)
        layout.addWidget(btnZm, 2, 1)

# -----------------------------------------------------
# Show widget
# -----------------------------------------------------
moveWidget = MoveWidget()
moveWidget.show()

print("✅ Qt XR Object Move Controller loaded")

