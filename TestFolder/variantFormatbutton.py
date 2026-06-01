from PySide6 import QtWidgets
from vrScenegraph import *

# -----------------------------
# XR PAGE CONTENT (Qt Widget)
# -----------------------------
class ObjectMoveWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("XR Object Move Tool")
        title.setStyleSheet("font-size: 18px;")

        btnPlusX = QtWidgets.QPushButton("Move +X")
        btnMinusX = QtWidgets.QPushButton("Move -X")

        layout.addWidget(title)
        layout.addWidget(btnPlusX)
        layout.addWidget(btnMinusX)

        btnPlusX.clicked.connect(lambda: self.move(10))
        btnMinusX.clicked.connect(lambda: self.move(-10))

    def move(self, delta):
        nodes = findNodes("Box")
        if not nodes:
            print("No Box found")
            return

        node = nodes[0]
        x, y, z = node.getTranslation()
        node.setTranslation(x + delta, y, z)

# -----------------------------
# XR HOME TOOL
# -----------------------------
tool = vrImmersiveUiService.createTool("XR_Object_Move")

tool.setText("Object Move")
tool.setCheckable(True)

widget = ObjectMoveWidget()
tool.setViewWidget(widget)