# =====================================================
# VRED Qt XR Object Move Controller (with Origin Button)
# =====================================================

from PySide2 import QtWidgets
from vrScenegraph import *

MOVE_STEP = 10.0  # millimeters per click
TARGET_NODE_NAME = "Box"

targetNode = None

# -----------------------------------------------------
# Resolve node
# -----------------------------------------------------
def resolveTargetNode():
    global targetNode
    nodes = findNodes(TARGET_NODE_NAME)
    if not nodes:
        print("❌ Node not found:", TARGET_NODE_NAME)
        return
    targetNode = nodes[0]
    print("✅ Target node resolved:", targetNode.getName())

# -----------------------------------------------------
# Move helper
# -----------------------------------------------------
def moveNode(dx, dy, dz):
    if not targetNode:
        return

    pos = targetNode.getTranslation()
    targetNode.setTranslation(
        pos[0] + dx,
        pos[1] + dy,
        pos[2] + dz
    )

# -----------------------------------------------------
# Move to origin ✅ NEW
# -----------------------------------------------------
def moveToOrigin():
    if not targetNode:
        return

    targetNode.setTranslation(0.0, 0.0, 0.0)
    print("✅ Node moved to origin (0, 0, 0)")

# -----------------------------------------------------
# Qt UI
# -----------------------------------------------------
class MoveWidget(QtWidgets.QWidget):

    def __init__(self):
        super(MoveWidget, self).__init__()
        self.setWindowTitle("XR Object Move Controller – Box")
        self.setMinimumWidth(240)

        mainLayout = QtWidgets.QVBoxLayout(self)
        grid = QtWidgets.QGridLayout()

        buttons = [
            ("+X", lambda: moveNode( MOVE_STEP, 0, 0), 0, 0),
            ("-X", lambda: moveNode(-MOVE_STEP, 0, 0), 0, 1),
            ("+Y", lambda: moveNode(0,  MOVE_STEP, 0), 1, 0),
            ("-Y", lambda: moveNode(0, -MOVE_STEP, 0), 1, 1),
            ("+Z", lambda: moveNode(0, 0,  MOVE_STEP), 2, 0),
            ("-Z", lambda: moveNode(0, 0, -MOVE_STEP), 2, 1),
        ]

        for text, func, r, c in buttons:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(func)
            grid.addWidget(btn, r, c)

        mainLayout.addLayout(grid)

        # --- Origin button ✅ ---
        originBtn = QtWidgets.QPushButton("Move to Origin (0,0,0)")
        originBtn.clicked.connect(moveToOrigin)
        mainLayout.addWidget(originBtn)

# -----------------------------------------------------
# Init
# -----------------------------------------------------
resolveTargetNode()
widget = MoveWidget()
widget.show()

print("✅ Qt XR Object Move Controller loaded (with Origin button)")