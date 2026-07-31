# ============================================================
# VRED 2026.2
# Seat Motion Calibration Tool
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
# ACTIVE TRACKERS
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
 
        # 3840x2160 / 4
        self.resize(960, 540)
 
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
        # TRACKER ROW
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
 
        trackerLayout.addSpacing(20)
 
        trackerLayout.addWidget(
            QtWidgets.QLabel("Head Tracker")
        )
 
        trackerLayout.addWidget(
            self.headCombo
        )
 
        trackerLayout.addStretch()
 
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
        # OPTIONS
        # ----------------------------------------------------
 
        optionsLayout = QtWidgets.QHBoxLayout()
 
        self.showXYZCheck = QtWidgets.QCheckBox(
            "Show XYZ"
        )
 
        self.showXYZCheck.setChecked(True)
 
        self.showPitchRollCheck = QtWidgets.QCheckBox(
            "Show Pitch / Roll"
        )
 
        self.showPitchRollCheck.setChecked(True)
 
        optionsLayout.addWidget(
            self.showXYZCheck
        )
 
        optionsLayout.addSpacing(20)
 
        optionsLayout.addWidget(
            self.showPitchRollCheck
        )
 
        optionsLayout.addStretch()
 
        mainLayout.addLayout(
            optionsLayout
        )
 
        # ----------------------------------------------------
        # ACTIVE TRACKERS
        # ----------------------------------------------------
 
        self.connectedLabel = QtWidgets.QLabel()
 
        self.connectedLabel.setStyleSheet(
            "font-weight:bold;"
        )
 
        mainLayout.addWidget(
            self.connectedLabel
        )
 
        # ----------------------------------------------------
        # COMPACT XYZ SECTION
        # ----------------------------------------------------
 
        xyzGroup = QtWidgets.QGroupBox(
            "TRACKER POSITIONS"
        )
 
        xyzLayout = QtWidgets.QVBoxLayout()
 
        self.hipLabel = QtWidgets.QLabel()
        self.headLabel = QtWidgets.QLabel()
 
        self.hipLabel.setStyleSheet(
            "font-size:11pt;"
        )
 
        self.headLabel.setStyleSheet(
            "font-size:11pt;"
        )
 
        xyzLayout.addWidget(
            self.hipLabel
        )
 
        xyzLayout.addWidget(
            self.headLabel
        )
 
        xyzGroup.setLayout(
            xyzLayout
        )
 
        mainLayout.addWidget(
            xyzGroup
        )
 
        # ----------------------------------------------------
        # OUTPUTS
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
 
        seatGroup.setLayout(
            seatLayout
        )
 
        tiltLayout = QtWidgets.QVBoxLayout()
        tiltLayout.addWidget(
            self.tiltLabel
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
 
        # ----------------------------------------------------
        # RESET BUTTONS
        # ----------------------------------------------------
 
        resetLayout = QtWidgets.QHBoxLayout()
 
        self.resetHipButton = QtWidgets.QPushButton(
            "Reset Hip Position"
        )
 
        self.resetHeadButton = QtWidgets.QPushButton(
            "Reset Head Position"
        )
 
        resetLayout.addWidget(
            self.resetHipButton
        )
 
        resetLayout.addWidget(
            self.resetHeadButton
        )
 
        mainLayout.addLayout(
            resetLayout
        )
        
                # ----------------------------------------------------
        # SIGNALS
        # ----------------------------------------------------
 
        self.refreshButton.clicked.connect(
            self.refreshTrackers
        )
 
        self.resetHipButton.clicked.connect(
            self.resetHip
        )
 
        self.resetHeadButton.clicked.connect(
            self.resetHead
        )
 
        self.hipCombo.currentIndexChanged.connect(
            self.updateSelectedTrackers
        )
 
        self.headCombo.currentIndexChanged.connect(
            self.updateSelectedTrackers
        )
 
        self.refreshTrackers()
 
        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------
 
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
            self.hipCombo.setCurrentIndex(0)
 
        if len(trackers) >= 2:
            self.headCombo.setCurrentIndex(1)
 
        self.connectedLabel.setText(
            "Active : " +
            "   ".join(
                ["● " + t for t in trackers]
            )
        )
 
        self.updateSelectedTrackers()
 
    # ========================================================
    # UPDATE TRACKERS
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
 
            self.hipTracker = \
                vrDeviceService.getVRDevice(
                    hipName
                )
 
            self.headTracker = \
                vrDeviceService.getVRDevice(
                    headName
                )
 
        except Exception as e:
 
            print(e)
 
    # ========================================================
    # RESET HIP
    # ========================================================
 
    def resetHip(self):
 
        global hipZero
 
        try:
 
            if self.hipTracker is None:
                return
 
            hipNode = self.hipTracker.getNode()
 
            hipZero = getPosition(
                hipNode
            )
 
            print(
                "Hip position reset"
            )
 
        except Exception as e:
 
            print(e)
 
    # ========================================================
    # RESET HEAD
    # ========================================================
 
    def resetHead(self):
 
        global headZero
        global neutralPitch
        global neutralRoll
 
        try:
 
            if self.headTracker is None:
                return
 
            if self.hipTracker is None:
                return
 
            hipNode = self.hipTracker.getNode()
            headNode = self.headTracker.getNode()
 
            headZero = getPosition(
                headNode
            )
 
            hipPos = getPosition(
                hipNode
            )
 
            headPos = getPosition(
                headNode
            )
 
            dx = headPos[0] - hipPos[0]
            dy = headPos[1] - hipPos[1]
            dz = headPos[2] - hipPos[2]
 
            neutralRoll = math.degrees(
                math.atan2(
                    dx,
                    dy
                )
            )
 
            neutralPitch = math.degrees(
                math.atan2(
                    dz,
                    dy
                )
            )
 
            print(
                "Head position reset"
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
 
            # ------------------------------------------------
            # HIP
            # ------------------------------------------------
 
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
 
            # ------------------------------------------------
            # HEAD
            # ------------------------------------------------
 
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
 
            # ------------------------------------------------
            # TILT CALCULATION
            # ------------------------------------------------
 
            dx = (
                headPos[0] -
                hipPos[0]
            )
 
            dy = (
                headPos[1] -
                hipPos[1]
            )
 
            dz = (
                headPos[2] -
                hipPos[2]
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
 
            # ------------------------------------------------
            # OVERALL TILT
            # ------------------------------------------------
 
            tiltAngle = roundValue(
                math.sqrt(
                    pitch * pitch +
                    roll * roll
                )
            )
 
            # ------------------------------------------------
            # DIRECTION
            # ------------------------------------------------
 
            direction = "CENTER"
 
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
 
            # ------------------------------------------------
            # HIDE / SHOW XYZ
            # ------------------------------------------------
 
            if self.showXYZCheck.isChecked():
 
                self.hipLabel.show()
                self.headLabel.show()
 
                self.hipLabel.setText(
                    "HIP  :   X {} mm    Y {} mm    Z {} mm".format(
                        hipX,
                        hipY,
                        hipZ
                    )
                )
 
                self.headLabel.setText(
                    "HEAD :   X {} mm    Y {} mm    Z {} mm".format(
                        headX,
                        headY,
                        headZ
                    )
                )
 
            else:
 
                self.hipLabel.hide()
                self.headLabel.hide()
 
            # ------------------------------------------------
            # SEAT OUTPUT
            # ------------------------------------------------
 
            self.seatLabel.setText(
                "Seat X : {} mm\n"
                "Seat Z : {} mm".format(
                    hipX,
                    hipZ
                )
            )
 
            # ------------------------------------------------
            # TILT OUTPUT
            # ------------------------------------------------
 
            if self.showPitchRollCheck.isChecked():
 
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
 
            else:
 
                self.tiltLabel.setText(
                    "Tilt Angle : {}°\n\n"
                    "Direction : {}".format(
                        tiltAngle,
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