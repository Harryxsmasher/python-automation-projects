# ============================================================
# VRED 2026.2
# Seat Motion Calibration Tool
#
# Hip Tracker:
#   Seat X / Seat Z
#
# Head Tracker:
#   Tilt Angle
#   Pitch
#   Roll
#
# Features
# ------------------------------------------------------------
# - Active Tracker Detection
# - Hip / Head Dropdown Selection
# - Horizontal Dashboard Layout
# - Reset Neutral Position
# - Rounded Values
# - 5 Second Updates
# ============================================================
 
from PySide6 import QtWidgets, QtCore
import math
import time
 
UPDATE_INTERVAL = 5000
 
POSITION_DEADBAND = 5
ANGLE_DEADBAND = 1
 
hipZero = [0, 0, 0]
headZero = [0, 0, 0]
 
neutralPitch = 0.0
neutralRoll = 0.0
 
# ============================================================
# HELPERS
# ============================================================
 
def roundValue(v):
    return int(round(v))
 
 
def applyDeadband(value, deadband):
 
    if abs(value) < deadband:
        return 0
 
    return value
 
 
def getPosition(node):
 
    pos = node.getWorldTranslation()
 
    return [
        pos.x(),
        pos.y(),
        pos.z()
    ]
 
 
# ============================================================
# ACTIVE TRACKER DETECTION
# ============================================================
 
def getAvailableTrackers():
 
    trackers = []
 
    for i in range(1, 21):
 
        try:
 
            name = "tracker-{}".format(i)
 
            tracker = vrDeviceService.getVRDevice(name)
 
            if tracker is None:
                continue
 
            node = tracker.getNode()
 
            pos = node.getWorldTranslation()
 
            if (
                abs(pos.x()) > 0.001 or
                abs(pos.y()) > 0.001 or
                abs(pos.z()) > 0.001
            ):
 
                trackers.append(name)
 
        except:
            pass
 
    return trackers
 
 
# ============================================================
# UI
# ============================================================
 
class SeatMotionTool(QtWidgets.QWidget):
 
    def __init__(self):
 
        super().__init__()
 
        self.hipTracker = None
        self.headTracker = None
 
        self.setWindowTitle(
            "Seat Motion Calibration Tool"
        )
 
        self.resize(900, 500)
 
        mainLayout = QtWidgets.QVBoxLayout(self)
 
        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------
 
        title = QtWidgets.QLabel(
            "Seat Motion Calibration Tool"
        )
 
        title.setStyleSheet(
            "font-size:14pt;"
            "font-weight:bold;"
        )
 
        mainLayout.addWidget(title)
 
        # ----------------------------------------------------
        # TRACKER SELECTION ROW
        # ----------------------------------------------------
 
        trackerLayout = QtWidgets.QHBoxLayout()
 
        self.hipCombo = QtWidgets.QComboBox()
        self.headCombo = QtWidgets.QComboBox()
 
        trackerLayout.addWidget(
            QtWidgets.QLabel("Hip Tracker")
        )
 
        trackerLayout.addWidget(
            self.hipCombo
        )
 
        trackerLayout.addSpacing(30)
 
        trackerLayout.addWidget(
            QtWidgets.QLabel("Head Tracker")
        )
 
        trackerLayout.addWidget(
            self.headCombo
        )
 
        self.refreshButton = QtWidgets.QPushButton(
            "Refresh"
        )
 
        trackerLayout.addWidget(
            self.refreshButton
        )
 
        mainLayout.addLayout(
            trackerLayout
        )
 
        # ----------------------------------------------------
        # ACTIVE TRACKERS
        # ----------------------------------------------------
 
        self.connectedLabel = QtWidgets.QLabel()
 
        mainLayout.addWidget(
            self.connectedLabel
        )
 
        # ----------------------------------------------------
        # HIP AND HEAD ROW
        # ----------------------------------------------------
 
        infoLayout = QtWidgets.QHBoxLayout()
 
        hipGroup = QtWidgets.QGroupBox(
            "HIP TRACKER"
        )
 
        headGroup = QtWidgets.QGroupBox(
            "HEAD TRACKER"
        )
 
        self.hipLabel = QtWidgets.QLabel()
        self.headLabel = QtWidgets.QLabel()
 
        hipLayout = QtWidgets.QVBoxLayout()
        hipLayout.addWidget(
            self.hipLabel
        )
 
        headLayout = QtWidgets.QVBoxLayout()
        headLayout.addWidget(
            self.headLabel
        )
 
        hipGroup.setLayout(
            hipLayout
        )
 
        headGroup.setLayout(
            headLayout
        )
 
        infoLayout.addWidget(
            hipGroup
        )
 
        infoLayout.addWidget(
            headGroup
        )
 
        mainLayout.addLayout(
            infoLayout
        )
 
        # ----------------------------------------------------
        # OUTPUT ROW
        # ----------------------------------------------------
 
        outputLayout = QtWidgets.QHBoxLayout()
 
        seatGroup = QtWidgets.QGroupBox(
            "SEAT POSITION"
        )
 
        tiltGroup = QtWidgets.QGroupBox(
            "TILT OUTPUT"
        )
 
        self.seatLabel = QtWidgets.QLabel()
 
        self.tiltLabel = QtWidgets.QLabel()
 
        seatLayout = QtWidgets.QVBoxLayout()
        seatLayout.addWidget(
            self.seatLabel
        )
 
        tiltLayout = QtWidgets.QVBoxLayout()
        tiltLayout.addWidget(
            self.tiltLabel
        )
 
        seatGroup.setLayout(
            seatLayout
        )
 
        tiltGroup.setLayout(
            tiltLayout
        )
 
        outputLayout.addWidget(
            seatGroup
        )
 
        outputLayout.addWidget(
            tiltGroup
        )
 
        mainLayout.addLayout(
            outputLayout
        )
 
        self.timeLabel = QtWidgets.QLabel()
 
        mainLayout.addWidget(
            self.timeLabel
        )
 
        self.resetButton = QtWidgets.QPushButton(
            "RESET NEUTRAL POSITION"
        )
 
        mainLayout.addWidget(
            self.resetButton
        )
 
        self.refreshButton.clicked.connect(
            self.refreshTrackers
        )
 
        self.resetButton.clicked.connect(
            self.resetReference
        )
 
        self.refreshTrackers()
 
        self.hipCombo.currentIndexChanged.connect(
            self.updateSelectedTrackers
        )
 
        self.headCombo.currentIndexChanged.connect(
            self.updateSelectedTrackers
        )
 
        self.timer = QtCore.QTimer()
 
        self.timer.timeout.connect(
            self.updateDisplay
        )
 
        self.timer.start(
            UPDATE_INTERVAL
        )
            # ========================================================
    # REFRESH TRACKERS
    # ========================================================
 
    def refreshTrackers(self):
 
        trackers = getAvailableTrackers()
 
        self.hipCombo.clear()
        self.headCombo.clear()
 
        self.hipCombo.addItems(trackers)
        self.headCombo.addItems(trackers)
 
        if len(trackers) >= 1:
            self.hipCombo.setCurrentText(trackers[0])
 
        if len(trackers) >= 2:
            self.headCombo.setCurrentText(trackers[1])
 
        self.connectedLabel.setText(
            "Active Trackers : " +
            "   ".join(
                ["● " + t for t in trackers]
            )
        )
 
        self.updateSelectedTrackers()
 
    # ========================================================
    # TRACKER SELECTION
    # ========================================================
 
    def updateSelectedTrackers(self):
 
        try:
 
            hipName = self.hipCombo.currentText()
            headName = self.headCombo.currentText()
 
            if hipName == headName:
 
                self.tiltLabel.setText(
                    "Select different trackers"
                )
 
                return
 
            self.hipTracker = vrDeviceService.getVRDevice(
                hipName
            )
 
            self.headTracker = vrDeviceService.getVRDevice(
                headName
            )
 
        except Exception as e:
 
            print(e)
 
    # ========================================================
    # RESET
    # ========================================================
 
    def resetReference(self):
 
        global hipZero
        global headZero
 
        global neutralPitch
        global neutralRoll
 
        if self.hipTracker is None:
            return
 
        if self.headTracker is None:
            return
 
        try:
 
            hipNode = self.hipTracker.getNode()
            headNode = self.headTracker.getNode()
 
            hipZero = getPosition(
                hipNode
            )
 
            headZero = getPosition(
                headNode
            )
 
            dx = (
                headZero[0] -
                hipZero[0]
            )
 
            dy = (
                headZero[1] -
                hipZero[1]
            )
 
            dz = (
                headZero[2] -
                hipZero[2]
            )
 
            neutralRoll = math.degrees(
                math.atan2(dx, dy)
            )
 
            neutralPitch = math.degrees(
                math.atan2(dz, dy)
            )
 
            print(
                "Neutral Position Saved"
            )
 
        except Exception as e:
 
            print(e)
 
    # ========================================================
    # UPDATE DISPLAY
    # ========================================================
 
    def updateDisplay(self):
 
        global neutralPitch
        global neutralRoll
 
        try:
 
            if self.hipTracker is None:
                return
 
            if self.headTracker is None:
                return
 
            hipNode = self.hipTracker.getNode()
            headNode = self.headTracker.getNode()
 
            hipPos = getPosition(
                hipNode
            )
 
            headPos = getPosition(
                headNode
            )
 
            # ------------------------------------
            # HIP VALUES
            # ------------------------------------
 
            hipX = applyDeadband(
                roundValue(
                    hipPos[0] - hipZero[0]
                ),
                POSITION_DEADBAND
            )
 
            hipY = applyDeadband(
                roundValue(
                    hipPos[1] - hipZero[1]
                ),
                POSITION_DEADBAND
            )
 
            hipZ = applyDeadband(
                roundValue(
                    hipPos[2] - hipZero[2]
                ),
                POSITION_DEADBAND
            )
 
            # ------------------------------------
            # HEAD VALUES
            # ------------------------------------
 
            headX = applyDeadband(
                roundValue(
                    headPos[0] - headZero[0]
                ),
                POSITION_DEADBAND
            )
 
            headY = applyDeadband(
                roundValue(
                    headPos[1] - headZero[1]
                ),
                POSITION_DEADBAND
            )
 
            headZ = applyDeadband(
                roundValue(
                    headPos[2] - headZero[2]
                ),
                POSITION_DEADBAND
            )
 
            # ------------------------------------
            # HIP -> HEAD VECTOR
            # ------------------------------------
 
            dx = (
                headPos[0]
                - hipPos[0]
            )
 
            dy = (
                headPos[1]
                - hipPos[1]
            )
 
            dz = (
                headPos[2]
                - hipPos[2]
            )
 
            currentRoll = math.degrees(
                math.atan2(
                    dx,
                    dy
                )
            )
 
            currentPitch = math.degrees(
                math.atan2(
                    dz,
                    dy
                )
            )
 
            roll = roundValue(
                currentRoll -
                neutralRoll
            )
 
            pitch = roundValue(
                currentPitch -
                neutralPitch
            )
 
            roll = applyDeadband(
                roll,
                ANGLE_DEADBAND
            )
 
            pitch = applyDeadband(
                pitch,
                ANGLE_DEADBAND
            )
 
            # ------------------------------------
            # OVERALL TILT ANGLE
            # ------------------------------------
 
            tiltAngle = roundValue(
                math.sqrt(
                    pitch * pitch +
                    roll * roll
                )
            )
 
            # ------------------------------------
            # DIRECTION
            # ------------------------------------
 
            vertical = ""
            horizontal = ""
 
            if pitch > 0:
                vertical = "FORWARD"
 
            elif pitch < 0:
                vertical = "BACKWARD"
 
            if roll > 0:
                horizontal = "RIGHT"
 
            elif roll < 0:
                horizontal = "LEFT"
 
            direction = "CENTER"
 
            if vertical and horizontal:
 
                direction = (
                    vertical +
                    " " +
                    horizontal
                )
 
            elif vertical:
 
                direction = vertical
 
            elif horizontal:
 
                direction = horizontal
 
            # ------------------------------------
            # HIP PANEL
            # ------------------------------------
 
            self.hipLabel.setText(
                "X : {} mm\n"
                "Y : {} mm\n"
                "Z : {} mm".format(
                    hipX,
                    hipY,
                    hipZ
                )
            )
 
            # ------------------------------------
            # HEAD PANEL
            # ------------------------------------
 
            self.headLabel.setText(
                "X : {} mm\n"
                "Y : {} mm\n"
                "Z : {} mm".format(
                    headX,
                    headY,
                    headZ
                )
            )
 
            # ------------------------------------
            # SEAT OUTPUT PANEL
            # ------------------------------------
 
            self.seatLabel.setText(
                "Seat X : {} mm\n"
                "Seat Z : {} mm".format(
                    hipX,
                    hipZ
                )
            )
 
            # ------------------------------------
            # TILT PANEL
            # ------------------------------------
 
            self.tiltLabel.setText(
                "Tilt Angle : {}°\n\n"
                "Pitch : {}°\n"
                "Roll  : {}°\n\n"
                "Direction : {}".format(
                    tiltAngle,
                    pitch,
                    roll,
                    direction
                )
            )
 
            self.timeLabel.setText(
                "Last Update : {}".format(
                    time.strftime(
                        "%H:%M:%S"
                    )
                )
            )
 
        except Exception as e:
 
            print(e)
 
 
# ============================================================
# SINGLE INSTANCE
# ============================================================
 
try:
    seatMotionTool.close()
    seatMotionTool.deleteLater()
except:
    pass
 
seatMotionTool = SeatMotionTool()
seatMotionTool.show()