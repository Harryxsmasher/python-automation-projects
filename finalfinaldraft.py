# ============================================================
# VRED 2026.2
# SEAT MOTION CALIBRATION TOOL
#
# HIP TRACKER
#
# 1. Press Calibrate Hip Movement.
# 2. Move and hold the seat FORWARD for 5 seconds.
# 3. Move and hold the seat BACKWARD for 5 seconds.
# 4. Return the seat to neutral.
# 5. Press Reset Hip Position.
#
# HEAD TRACKER / SEAT TILT
#
# 1. Press Calibrate Seat Tilt.
# 2. Tilt and hold the seat FORWARD for 5 seconds.
# 3. Tilt and hold the seat BACKWARD for 5 seconds.
# 4. Return the seat to neutral.
# 5. Press Reset Tilt Position.
#
# OUTPUT
#
# Seat X:
#   Positive = Forward
#   Negative = Backward
#
# Seat Y:
#   Positive = Up
#   Negative = Down
#
# Seat Z:
#   Positive = Right
#   Negative = Left
#
# Tilt:
#   Neutral = 0 degrees
#   Forward tilt = 0 degrees
#   Backward tilt = Positive angle from 0 degrees
#
# Tracker mounting orientation does not determine the calibrated
# forward/backward directions.
#
# Tracker data is sampled every 50 milliseconds.
# Position and tilt outputs use a 5-second rolling average.
# Display values update every 5 seconds.
# ============================================================

from PySide6 import QtWidgets, QtCore, QtGui
from collections import deque
import math
import time


# ============================================================
# SETTINGS
# ============================================================

TRACKING_INTERVAL = 50
DISPLAY_INTERVAL = 5000
AVERAGING_WINDOW_SECONDS = 5.0

HIP_PHASE_SECONDS = 5.0
TILT_PHASE_SECONDS = 5.0

CALIBRATION_HOLD_FRACTION = 0.40

MINIMUM_HIP_CALIBRATION_DISTANCE = 40.0
MINIMUM_TILT_CALIBRATION_DISTANCE = 20.0

POSITION_DEADBAND = 5.0
VERTICAL_DEADBAND = 10.0
ANGLE_DEADBAND = 1.0

ENABLE_SEAT_VERTICAL_OUTPUT = False


# ============================================================
# GLOBAL CALIBRATION VALUES
# ============================================================

hipZero = [
    0.0,
    0.0,
    0.0
]

headZero = [
    0.0,
    0.0,
    0.0
]

hipCalibrationValid = False
hipPositionResetValid = False

tiltCalibrationValid = False
tiltPositionResetValid = False

seatForwardWorld = None
seatUpWorld = None
seatRightWorld = None

tiltForwardWorld = None
tiltUpWorld = None
tiltRightWorld = None

neutralTiltPitch = 0.0
neutralTiltRoll = 0.0


# ============================================================
# BASIC HELPERS
# ============================================================

def roundValue(value):
    return int(
        round(value)
    )


def applyDeadband(value, deadband):
    if abs(value) < deadband:
        return 0.0

    return value


def normalizeAngle180(angle):
    """
    Normalizes an angle to -180 through +180 degrees.

    This prevents a small movement from appearing as
    approximately 359 or 360 degrees.
    """

    while angle > 180.0:
        angle -= 360.0

    while angle < -180.0:
        angle += 360.0

    return angle


def getPosition(node):
    position = node.getWorldTranslation()

    return [
        position.x(),
        position.y(),
        position.z()
    ]


def positionToVector(position):
    return QtGui.QVector3D(
        position[0],
        position[1],
        position[2]
    )


def normalizeVector(vector):
    result = QtGui.QVector3D(
        vector.x(),
        vector.y(),
        vector.z()
    )

    if result.lengthSquared() <= 0.0000001:
        raise RuntimeError(
            "Cannot normalize a zero-length vector."
        )

    result.normalize()

    return result


def getHorizontalVector(vector):
    """
    VRED/OpenVR normally uses world Y as vertical.
    """

    return QtGui.QVector3D(
        vector.x(),
        0.0,
        vector.z()
    )


def getAverage(values):
    if not values:
        return 0.0

    return sum(values) / float(
        len(values)
    )


def averagePositions(positions):
    if not positions:
        raise RuntimeError(
            "No calibration samples were recorded."
        )

    xValues = []
    yValues = []
    zValues = []

    for position in positions:
        xValues.append(
            position[0]
        )

        yValues.append(
            position[1]
        )

        zValues.append(
            position[2]
        )

    return [
        getAverage(xValues),
        getAverage(yValues),
        getAverage(zValues)
    ]


def getStableSamples(samples):
    """
    Uses the final part of each phase.

    The operator should be holding the requested position
    during this period.
    """

    if not samples:
        return []

    stableCount = max(
        1,
        int(
            len(samples) *
            CALIBRATION_HOLD_FRACTION
        )
    )

    return samples[-stableCount:]


def getRelativeHeadPosition(
    hipNode,
    headNode
):
    """
    Returns head position relative to the hip tracker.

    Using the relative position reduces the effect of the
    entire seat translating while tilt is measured.
    """

    hipPosition = getPosition(
        hipNode
    )

    headPosition = getPosition(
        headNode
    )

    return [
        headPosition[0] - hipPosition[0],
        headPosition[1] - hipPosition[1],
        headPosition[2] - hipPosition[2]
    ]


def formatVector(vector):
    if vector is None:
        return "None"

    return (
        "X {:.4f}, Y {:.4f}, Z {:.4f}"
    ).format(
        vector.x(),
        vector.y(),
        vector.z()
    )


# ============================================================
# COORDINATE FRAME CREATION
# ============================================================

def createCoordinateFrame(
    forwardPosition,
    backwardPosition,
    minimumDistance,
    calibrationName
):
    """
    Creates a coordinate frame from the physically identified
    forward and backward positions.

    The forward axis points from backward toward forward.
    """

    forwardVector = positionToVector(
        forwardPosition
    )

    backwardVector = positionToVector(
        backwardPosition
    )

    forwardDifference = (
        forwardVector -
        backwardVector
    )

    horizontalDifference = getHorizontalVector(
        forwardDifference
    )

    detectedDistance = horizontalDifference.length()

    if detectedDistance < minimumDistance:
        raise RuntimeError(
            "{} forward and backward positions were too "
            "close. Detected distance: {:.1f} mm."
            .format(
                calibrationName,
                detectedDistance
            )
        )

    calibratedForward = normalizeVector(
        horizontalDifference
    )

    calibratedUp = QtGui.QVector3D(
        0.0,
        1.0,
        0.0
    )

    calibratedRight = QtGui.QVector3D.crossProduct(
        calibratedForward,
        calibratedUp
    )

    calibratedRight = normalizeVector(
        calibratedRight
    )

    # Recalculate forward to guarantee perpendicular axes.
    calibratedForward = QtGui.QVector3D.crossProduct(
        calibratedUp,
        calibratedRight
    )

    calibratedForward = normalizeVector(
        calibratedForward
    )

    return (
        calibratedRight,
        calibratedUp,
        calibratedForward,
        detectedDistance
    )


# ============================================================
# HIP MOVEMENT CALCULATION
# ============================================================

def transformHipMovement(
    currentPosition,
    zeroPosition
):
    if not hipCalibrationValid:
        return 0.0, 0.0, 0.0

    if not hipPositionResetValid:
        return 0.0, 0.0, 0.0

    if seatForwardWorld is None:
        return 0.0, 0.0, 0.0

    if seatUpWorld is None:
        return 0.0, 0.0, 0.0

    if seatRightWorld is None:
        return 0.0, 0.0, 0.0

    worldDelta = QtGui.QVector3D(
        currentPosition[0] - zeroPosition[0],
        currentPosition[1] - zeroPosition[1],
        currentPosition[2] - zeroPosition[2]
    )

    seatX = QtGui.QVector3D.dotProduct(
        worldDelta,
        seatForwardWorld
    )

    seatY = QtGui.QVector3D.dotProduct(
        worldDelta,
        seatUpWorld
    )

    seatZ = QtGui.QVector3D.dotProduct(
        worldDelta,
        seatRightWorld
    )

    if not ENABLE_SEAT_VERTICAL_OUTPUT:
        seatY = 0.0

    return seatX, seatY, seatZ


# ============================================================
# TILT CALCULATION
# ============================================================

def calculateTiltAngles(
    hipPosition,
    headPosition
):
    """
    Calculates tilt in the calibrated coordinate frame.

    Positive pitch points toward calibrated forward.
    Negative pitch points toward calibrated backward.
    """

    if not tiltCalibrationValid:
        return 0.0, 0.0

    if tiltForwardWorld is None:
        return 0.0, 0.0

    if tiltUpWorld is None:
        return 0.0, 0.0

    if tiltRightWorld is None:
        return 0.0, 0.0

    relativeVector = QtGui.QVector3D(
        headPosition[0] - hipPosition[0],
        headPosition[1] - hipPosition[1],
        headPosition[2] - hipPosition[2]
    )

    forwardComponent = QtGui.QVector3D.dotProduct(
        relativeVector,
        tiltForwardWorld
    )

    upComponent = QtGui.QVector3D.dotProduct(
        relativeVector,
        tiltUpWorld
    )

    rightComponent = QtGui.QVector3D.dotProduct(
        relativeVector,
        tiltRightWorld
    )

    if abs(upComponent) < 0.000001:
        if upComponent < 0.0:
            upComponent = -0.000001
        else:
            upComponent = 0.000001

    pitch = math.degrees(
        math.atan2(
            forwardComponent,
            upComponent
        )
    )

    roll = math.degrees(
        math.atan2(
            rightComponent,
            upComponent
        )
    )

    return pitch, roll


def calculateBackwardOnlyTilt(
    currentPitch,
    zeroPitch
):
    """
    Backward-only output.

    Neutral = 0 degrees
    Forward = 0 degrees
    Backward = Positive angle beginning at 0 degrees
    """

    signedPitchDifference = normalizeAngle180(
        currentPitch -
        zeroPitch
    )

    # Calibrated backward movement produces a negative
    # signed pitch difference. Convert it to positive output.
    backwardAngle = max(
        0.0,
        -signedPitchDifference
    )

    if backwardAngle < ANGLE_DEADBAND:
        backwardAngle = 0.0

    return backwardAngle


# ============================================================
# TRACKER DETECTION
# ============================================================

def getAvailableTrackers():
    trackers = []

    for index in range(1, 21):
        try:
            trackerName = "tracker-{}".format(
                index
            )

            tracker = vrDeviceService.getVRDevice(
                trackerName
            )

            if tracker is None:
                continue

            node = tracker.getNode()

            if node is None:
                continue

            position = node.getWorldTranslation()

            if (
                abs(position.x()) > 0.001 or
                abs(position.y()) > 0.001 or
                abs(position.z()) > 0.001
            ):
                trackers.append(
                    trackerName
                )

        except Exception as error:
            print(
                "Tracker detection error for "
                "tracker-{}: {}".format(
                    index,
                    error
                )
            )

    return trackers


# ============================================================
# USER INTERFACE
# ============================================================

class SeatMotionTool(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.hipTracker = None
        self.headTracker = None

        # Hip calibration state.
        self.hipCalibrationPhase = None
        self.hipCalibrationStartTime = 0.0
        self.hipForwardSamples = []
        self.hipBackwardSamples = []

        # Tilt calibration state.
        self.tiltCalibrationPhase = None
        self.tiltCalibrationStartTime = 0.0
        self.tiltForwardSamples = []
        self.tiltBackwardSamples = []

        # Rolling output samples.
        self.seatSamples = deque()
        self.tiltSamples = deque()

        self.averagedSeatX = 0
        self.averagedSeatY = 0
        self.averagedSeatZ = 0
        self.averagedBackwardTilt = 0

        self.setWindowTitle(
            "Seat Motion Calibration Tool"
        )

        self.resize(
            1050,
            760
        )

        mainLayout = QtWidgets.QVBoxLayout(
            self
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        titleLabel = QtWidgets.QLabel(
            "Seat Motion Calibration Tool"
        )

        titleLabel.setStyleSheet(
            "font-size: 14pt;"
            "font-weight: bold;"
        )

        mainLayout.addWidget(
            titleLabel
        )

        informationLabel = QtWidgets.QLabel(
            "Seat X = Forward / Backward | "
            "Seat Y = Up / Down | "
            "Seat Z = Left / Right | "
            "Tilt = Backward only | "
            "Neutral tilt = 0°"
        )

        informationLabel.setWordWrap(
            True
        )

        informationLabel.setStyleSheet(
            "color: #606060;"
        )

        mainLayout.addWidget(
            informationLabel
        )

        # ----------------------------------------------------
        # TRACKER SELECTION
        # ----------------------------------------------------

        trackerLayout = QtWidgets.QHBoxLayout()

        trackerLayout.addWidget(
            QtWidgets.QLabel(
                "Hip Tracker"
            )
        )

        self.hipCombo = QtWidgets.QComboBox()

        trackerLayout.addWidget(
            self.hipCombo
        )

        trackerLayout.addSpacing(
            20
        )

        trackerLayout.addWidget(
            QtWidgets.QLabel(
                "Head Tracker"
            )
        )

        self.headCombo = QtWidgets.QComboBox()

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

        self.showXYZCheck.setChecked(
            True
        )

        self.showDiagnosticsCheck = QtWidgets.QCheckBox(
            "Show Tilt Diagnostics"
        )

        self.showDiagnosticsCheck.setChecked(
            True
        )

        optionsLayout.addWidget(
            self.showXYZCheck
        )

        optionsLayout.addSpacing(
            20
        )

        optionsLayout.addWidget(
            self.showDiagnosticsCheck
        )

        optionsLayout.addStretch()

        mainLayout.addLayout(
            optionsLayout
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.connectedLabel = QtWidgets.QLabel(
            "Active: Detecting trackers"
        )

        self.connectedLabel.setStyleSheet(
            "font-weight: bold;"
        )

        mainLayout.addWidget(
            self.connectedLabel
        )

        self.hipCalibrationLabel = QtWidgets.QLabel(
            "Hip calibration: Not calibrated"
        )

        self.hipCalibrationLabel.setWordWrap(
            True
        )

        self.hipCalibrationLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        mainLayout.addWidget(
            self.hipCalibrationLabel
        )

        self.hipResetLabel = QtWidgets.QLabel(
            "Hip position: Not reset"
        )

        self.hipResetLabel.setWordWrap(
            True
        )

        self.hipResetLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        mainLayout.addWidget(
            self.hipResetLabel
        )

        self.tiltCalibrationLabel = QtWidgets.QLabel(
            "Tilt calibration: Not calibrated"
        )

        self.tiltCalibrationLabel.setWordWrap(
            True
        )

        self.tiltCalibrationLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        mainLayout.addWidget(
            self.tiltCalibrationLabel
        )

        self.tiltResetLabel = QtWidgets.QLabel(
            "Tilt position: Not reset"
        )

        self.tiltResetLabel.setWordWrap(
            True
        )

        self.tiltResetLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        mainLayout.addWidget(
            self.tiltResetLabel
        )

        self.axisLabel = QtWidgets.QLabel(
            "Calibrated axes: None"
        )

        self.axisLabel.setWordWrap(
            True
        )

        self.axisLabel.setStyleSheet(
            "color: #707070;"
        )

        mainLayout.addWidget(
            self.axisLabel
        )

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        self.calibrationProgress = QtWidgets.QProgressBar()

        self.calibrationProgress.setRange(
            0,
            100
        )

        self.calibrationProgress.setValue(
            0
        )

        self.calibrationProgress.hide()

        mainLayout.addWidget(
            self.calibrationProgress
        )

        # ----------------------------------------------------
        # XYZ
        # ----------------------------------------------------

        self.xyzGroup = QtWidgets.QGroupBox(
            "TRACKER POSITIONS"
        )

        xyzLayout = QtWidgets.QVBoxLayout()

        self.hipLabel = QtWidgets.QLabel(
            "HIP : Not calibrated"
        )

        self.headLabel = QtWidgets.QLabel(
            "HEAD : Not calibrated"
        )

        self.hipLabel.setStyleSheet(
            "font-size: 11pt;"
        )

        self.headLabel.setStyleSheet(
            "font-size: 11pt;"
        )

        xyzLayout.addWidget(
            self.hipLabel
        )

        xyzLayout.addWidget(
            self.headLabel
        )

        self.xyzGroup.setLayout(
            xyzLayout
        )

        mainLayout.addWidget(
            self.xyzGroup
        )

        # ----------------------------------------------------
        # OUTPUTS
        # ----------------------------------------------------

        outputLayout = QtWidgets.QHBoxLayout()

        seatGroup = QtWidgets.QGroupBox(
            "SEAT POSITION"
        )

        seatLayout = QtWidgets.QVBoxLayout()

        self.seatLabel = QtWidgets.QLabel(
            "Press Calibrate Hip Movement"
        )

        self.seatLabel.setStyleSheet(
            "font-size: 11pt;"
        )

        seatLayout.addWidget(
            self.seatLabel
        )

        seatGroup.setLayout(
            seatLayout
        )

        tiltGroup = QtWidgets.QGroupBox(
            "BACKWARD SEAT TILT"
        )

        tiltLayout = QtWidgets.QVBoxLayout()

        self.tiltLabel = QtWidgets.QLabel(
            "Press Calibrate Seat Tilt"
        )

        self.tiltLabel.setStyleSheet(
            "font-size: 11pt;"
        )

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

        # ----------------------------------------------------
        # LAST UPDATE
        # ----------------------------------------------------

        self.timeLabel = QtWidgets.QLabel(
            "Last display update: Waiting"
        )

        mainLayout.addWidget(
            self.timeLabel
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttonLayout = QtWidgets.QHBoxLayout()

        self.calibrateHipButton = QtWidgets.QPushButton(
            "Calibrate Hip Movement"
        )

        self.resetHipButton = QtWidgets.QPushButton(
            "Reset Hip Position"
        )

        self.calibrateTiltButton = QtWidgets.QPushButton(
            "Calibrate Seat Tilt"
        )

        self.resetTiltButton = QtWidgets.QPushButton(
            "Reset Tilt Position"
        )

        self.resetHipButton.setEnabled(
            False
        )

        self.resetTiltButton.setEnabled(
            False
        )

        buttonLayout.addWidget(
            self.calibrateHipButton
        )

        buttonLayout.addWidget(
            self.resetHipButton
        )

        buttonLayout.addWidget(
            self.calibrateTiltButton
        )

        buttonLayout.addWidget(
            self.resetTiltButton
        )

        mainLayout.addLayout(
            buttonLayout
        )

        # ----------------------------------------------------
        # SIGNALS
        # ----------------------------------------------------

        self.refreshButton.clicked.connect(
            self.refreshTrackers
        )

        self.calibrateHipButton.clicked.connect(
            self.startHipCalibration
        )

        self.resetHipButton.clicked.connect(
            self.resetHipPosition
        )

        self.calibrateTiltButton.clicked.connect(
            self.startTiltCalibration
        )

        self.resetTiltButton.clicked.connect(
            self.resetTiltPosition
        )

        self.hipCombo.currentIndexChanged.connect(
            self.updateSelectedTrackers
        )

        self.headCombo.currentIndexChanged.connect(
            self.updateSelectedTrackers
        )

        self.showXYZCheck.toggled.connect(
            self.updateVisibility
        )

        # ----------------------------------------------------
        # TIMERS
        # ----------------------------------------------------

        self.trackingTimer = QtCore.QTimer(
            self
        )

        self.trackingTimer.timeout.connect(
            self.sampleTracking
        )

        self.trackingTimer.start(
            TRACKING_INTERVAL
        )

        self.displayTimer = QtCore.QTimer(
            self
        )

        self.displayTimer.timeout.connect(
            self.updateDisplay
        )

        self.displayTimer.start(
            DISPLAY_INTERVAL
        )

        self.refreshTrackers()

    # ========================================================
    # UI STATE
    # ========================================================

    def updateVisibility(self):
        self.xyzGroup.setVisible(
            self.showXYZCheck.isChecked()
        )

    def isCalibrationActive(self):
        return (
            self.hipCalibrationPhase is not None or
            self.tiltCalibrationPhase is not None
        )

    def updateButtonStates(self):
        active = self.isCalibrationActive()

        self.calibrateHipButton.setEnabled(
            not active
        )

        self.calibrateTiltButton.setEnabled(
            not active
        )

        self.resetHipButton.setEnabled(
            hipCalibrationValid and
            not active
        )

        self.resetTiltButton.setEnabled(
            tiltCalibrationValid and
            not active
        )

    def updateAxisLabel(self):
        hipText = "Hip axes: Not calibrated"
        tiltText = "Tilt axis: Not calibrated"

        if hipCalibrationValid:
            hipText = (
                "Hip axes: X Forward/Backward, "
                "Y Up/Down, Z Left/Right"
            )

        if tiltCalibrationValid:
            tiltText = (
                "Tilt axis: Forward/Backward calibrated, "
                "backward-only output"
            )

        self.axisLabel.setText(
            "{} | {}".format(
                hipText,
                tiltText
            )
        )

        if (
            hipCalibrationValid and
            tiltCalibrationValid
        ):
            self.axisLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #20a050;"
            )

        elif (
            hipCalibrationValid or
            tiltCalibrationValid
        ):
            self.axisLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d08000;"
            )

        else:
            self.axisLabel.setStyleSheet(
                "color: #707070;"
            )

    # ========================================================
    # CLEAR CALIBRATIONS
    # ========================================================

    def clearHipCalibration(self):
        global hipCalibrationValid
        global hipPositionResetValid

        global seatForwardWorld
        global seatUpWorld
        global seatRightWorld

        hipCalibrationValid = False
        hipPositionResetValid = False

        seatForwardWorld = None
        seatUpWorld = None
        seatRightWorld = None

        self.hipCalibrationPhase = None
        self.hipForwardSamples = []
        self.hipBackwardSamples = []

        self.seatSamples.clear()

        self.averagedSeatX = 0
        self.averagedSeatY = 0
        self.averagedSeatZ = 0

        self.hipCalibrationLabel.setText(
            "Hip calibration: Not calibrated"
        )

        self.hipCalibrationLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        self.hipResetLabel.setText(
            "Hip position: Not reset"
        )

        self.hipResetLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        self.hipLabel.setText(
            "HIP : Not calibrated"
        )

        self.seatLabel.setText(
            "Press Calibrate Hip Movement"
        )

        self.updateButtonStates()
        self.updateAxisLabel()

    def clearTiltCalibration(self):
        global tiltCalibrationValid
        global tiltPositionResetValid

        global tiltForwardWorld
        global tiltUpWorld
        global tiltRightWorld

        global neutralTiltPitch
        global neutralTiltRoll

        tiltCalibrationValid = False
        tiltPositionResetValid = False

        tiltForwardWorld = None
        tiltUpWorld = None
        tiltRightWorld = None

        neutralTiltPitch = 0.0
        neutralTiltRoll = 0.0

        self.tiltCalibrationPhase = None
        self.tiltForwardSamples = []
        self.tiltBackwardSamples = []

        self.tiltSamples.clear()
        self.averagedBackwardTilt = 0

        self.tiltCalibrationLabel.setText(
            "Tilt calibration: Not calibrated"
        )

        self.tiltCalibrationLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        self.tiltResetLabel.setText(
            "Tilt position: Not reset"
        )

        self.tiltResetLabel.setStyleSheet(
            "font-weight: bold;"
            "color: #d08000;"
        )

        self.headLabel.setText(
            "HEAD : Not calibrated"
        )

        self.tiltLabel.setText(
            "Press Calibrate Seat Tilt"
        )

        self.updateButtonStates()
        self.updateAxisLabel()

    # ========================================================
    # TRACKER SELECTION
    # ========================================================

    def refreshTrackers(self):
        previousHip = self.hipCombo.currentText()
        previousHead = self.headCombo.currentText()

        trackers = getAvailableTrackers()

        self.hipCombo.blockSignals(
            True
        )

        self.headCombo.blockSignals(
            True
        )

        self.hipCombo.clear()
        self.headCombo.clear()

        self.hipCombo.addItems(
            trackers
        )

        self.headCombo.addItems(
            trackers
        )

        hipIndex = self.hipCombo.findText(
            previousHip
        )

        headIndex = self.headCombo.findText(
            previousHead
        )

        if hipIndex >= 0:
            self.hipCombo.setCurrentIndex(
                hipIndex
            )

        elif len(trackers) >= 1:
            self.hipCombo.setCurrentIndex(
                0
            )

        if headIndex >= 0:
            self.headCombo.setCurrentIndex(
                headIndex
            )

        elif len(trackers) >= 2:
            self.headCombo.setCurrentIndex(
                1
            )

        elif len(trackers) >= 1:
            self.headCombo.setCurrentIndex(
                0
            )

        self.hipCombo.blockSignals(
            False
        )

        self.headCombo.blockSignals(
            False
        )

        if trackers:
            activeNames = []

            for trackerName in trackers:
                activeNames.append(
                    "● " + trackerName
                )

            self.connectedLabel.setText(
                "Active: " +
                " ".join(
                    activeNames
                )
            )

        else:
            self.connectedLabel.setText(
                "Active: No trackers detected"
            )

        self.updateSelectedTrackers()

    def updateSelectedTrackers(self):
        try:
            hipName = self.hipCombo.currentText()
            headName = self.headCombo.currentText()

            self.hipTracker = None
            self.headTracker = None

            self.clearHipCalibration()
            self.clearTiltCalibration()

            if not hipName or not headName:
                self.connectedLabel.setText(
                    "Select hip and head trackers"
                )

                return

            if hipName == headName:
                self.connectedLabel.setText(
                    "Hip and head trackers must be different"
                )

                return

            self.hipTracker = vrDeviceService.getVRDevice(
                hipName
            )

            self.headTracker = vrDeviceService.getVRDevice(
                headName
            )

            if self.hipTracker is None:
                raise RuntimeError(
                    "Selected hip tracker is unavailable."
                )

            if self.headTracker is None:
                raise RuntimeError(
                    "Selected head tracker is unavailable."
                )

            self.connectedLabel.setText(
                "Selected: Hip {} | Head {}".format(
                    hipName,
                    headName
                )
            )

        except Exception as error:
            self.connectedLabel.setText(
                "Tracker selection error: {}".format(
                    error
                )
            )

            print(
                "Tracker selection error: {}".format(
                    error
                )
            )

    # ========================================================
    # HIP CALIBRATION
    # ========================================================

    def startHipCalibration(self):
        global hipCalibrationValid
        global hipPositionResetValid

        try:
            if self.isCalibrationActive():
                raise RuntimeError(
                    "Another calibration is running."
                )

            if self.hipTracker is None:
                raise RuntimeError(
                    "No hip tracker is selected."
                )

            hipNode = self.hipTracker.getNode()

            if hipNode is None:
                raise RuntimeError(
                    "Hip tracker node is unavailable."
                )

            hipCalibrationValid = False
            hipPositionResetValid = False

            self.hipForwardSamples = []
            self.hipBackwardSamples = []

            self.hipCalibrationPhase = "FORWARD"

            self.hipCalibrationStartTime = (
                time.monotonic()
            )

            self.seatSamples.clear()

            self.calibrationProgress.setValue(
                0
            )

            self.calibrationProgress.show()

            self.hipCalibrationLabel.setText(
                "Hip calibration: Move FORWARD and hold."
            )

            self.hipCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d08000;"
            )

            self.hipResetLabel.setText(
                "Hip position: Waiting for calibration"
            )

            self.seatLabel.setText(
                "HIP CALIBRATION\n\n"
                "Phase 1 of 2\n"
                "Move FORWARD and hold."
            )

            self.updateButtonStates()

        except Exception as error:
            self.hipCalibrationPhase = None
            self.calibrationProgress.hide()

            self.hipCalibrationLabel.setText(
                "Hip calibration failed: {}".format(
                    error
                )
            )

            self.hipCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d03030;"
            )

            self.updateButtonStates()

    def startHipBackwardPhase(self):
        self.hipCalibrationPhase = "BACKWARD"

        self.hipCalibrationStartTime = (
            time.monotonic()
        )

        self.calibrationProgress.setValue(
            50
        )

        self.hipCalibrationLabel.setText(
            "Hip calibration: Move BACKWARD and hold."
        )

        self.seatLabel.setText(
            "HIP CALIBRATION\n\n"
            "Phase 2 of 2\n"
            "Move BACKWARD and hold."
        )

    def finishHipCalibration(self):
        global hipCalibrationValid
        global hipPositionResetValid

        global seatForwardWorld
        global seatUpWorld
        global seatRightWorld

        self.hipCalibrationPhase = None
        self.calibrationProgress.hide()

        try:
            forwardSamples = getStableSamples(
                self.hipForwardSamples
            )

            backwardSamples = getStableSamples(
                self.hipBackwardSamples
            )

            forwardPosition = averagePositions(
                forwardSamples
            )

            backwardPosition = averagePositions(
                backwardSamples
            )

            (
                seatRightWorld,
                seatUpWorld,
                seatForwardWorld,
                detectedDistance
            ) = createCoordinateFrame(
                forwardPosition,
                backwardPosition,
                MINIMUM_HIP_CALIBRATION_DISTANCE,
                "Hip"
            )

            hipCalibrationValid = True
            hipPositionResetValid = False

            self.seatSamples.clear()

            self.hipCalibrationLabel.setText(
                "Hip calibration: Calibrated successfully"
            )

            self.hipCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #20a050;"
            )

            self.hipResetLabel.setText(
                "Hip position: Return to neutral and press "
                "Reset Hip Position"
            )

            self.hipResetLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d08000;"
            )

            self.seatLabel.setText(
                "Hip calibration complete.\n\n"
                "Return to neutral and press "
                "Reset Hip Position."
            )

            self.updateAxisLabel()
            self.updateButtonStates()

            print(
                "Hip calibration completed."
            )

            print(
                "Hip calibration distance: {:.3f} mm".format(
                    detectedDistance
                )
            )

            print(
                "Seat forward vector: {}".format(
                    formatVector(
                        seatForwardWorld
                    )
                )
            )

        except Exception as error:
            hipCalibrationValid = False
            hipPositionResetValid = False

            seatForwardWorld = None
            seatUpWorld = None
            seatRightWorld = None

            self.hipCalibrationLabel.setText(
                "Hip calibration failed: {}".format(
                    error
                )
            )

            self.hipCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d03030;"
            )

            self.seatLabel.setText(
                "Hip calibration failed.\n"
                "Move farther forward and backward."
            )

            self.updateAxisLabel()
            self.updateButtonStates()

    def resetHipPosition(self):
        global hipZero
        global hipPositionResetValid

        try:
            if self.isCalibrationActive():
                raise RuntimeError(
                    "Wait for calibration to finish."
                )

            if not hipCalibrationValid:
                raise RuntimeError(
                    "Calibrate hip movement first."
                )

            if self.hipTracker is None:
                raise RuntimeError(
                    "No hip tracker is selected."
                )

            hipNode = self.hipTracker.getNode()

            if hipNode is None:
                raise RuntimeError(
                    "Hip tracker node is unavailable."
                )

            hipZero = getPosition(
                hipNode
            )

            hipPositionResetValid = True

            self.seatSamples.clear()

            self.averagedSeatX = 0
            self.averagedSeatY = 0
            self.averagedSeatZ = 0

            self.hipResetLabel.setText(
                "Hip position: Reset successfully"
            )

            self.hipResetLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #20a050;"
            )

            self.seatLabel.setText(
                "Seat X, Forward / Backward : 0 mm\n"
                "Seat Y, Up / Down : 0 mm\n"
                "Seat Z, Left / Right : 0 mm"
            )

            self.hipLabel.setText(
                "HIP SEAT FRAME : X 0 mm Y 0 mm Z 0 mm"
            )

        except Exception as error:
            hipPositionResetValid = False

            self.hipResetLabel.setText(
                "Hip reset failed: {}".format(
                    error
                )
            )

            self.hipResetLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d03030;"
            )

    # ========================================================
    # TILT CALIBRATION
    # ========================================================

    def startTiltCalibration(self):
        global tiltCalibrationValid
        global tiltPositionResetValid

        try:
            if self.isCalibrationActive():
                raise RuntimeError(
                    "Another calibration is running."
                )

            if self.hipTracker is None:
                raise RuntimeError(
                    "No hip tracker is selected."
                )

            if self.headTracker is None:
                raise RuntimeError(
                    "No head tracker is selected."
                )

            hipNode = self.hipTracker.getNode()
            headNode = self.headTracker.getNode()

            if hipNode is None:
                raise RuntimeError(
                    "Hip tracker node is unavailable."
                )

            if headNode is None:
                raise RuntimeError(
                    "Head tracker node is unavailable."
                )

            tiltCalibrationValid = False
            tiltPositionResetValid = False

            self.tiltForwardSamples = []
            self.tiltBackwardSamples = []

            self.tiltCalibrationPhase = "FORWARD"

            self.tiltCalibrationStartTime = (
                time.monotonic()
            )

            self.tiltSamples.clear()

            self.calibrationProgress.setValue(
                0
            )

            self.calibrationProgress.show()

            self.tiltCalibrationLabel.setText(
                "Tilt calibration: Tilt FORWARD and hold."
            )

            self.tiltCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d08000;"
            )

            self.tiltResetLabel.setText(
                "Tilt position: Waiting for calibration"
            )

            self.tiltLabel.setText(
                "TILT CALIBRATION\n\n"
                "Phase 1 of 2\n"
                "Tilt FORWARD and hold."
            )

            self.updateButtonStates()

        except Exception as error:
            self.tiltCalibrationPhase = None
            self.calibrationProgress.hide()

            self.tiltCalibrationLabel.setText(
                "Tilt calibration failed: {}".format(
                    error
                )
            )

            self.tiltCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d03030;"
            )

            self.updateButtonStates()

    def startTiltBackwardPhase(self):
        self.tiltCalibrationPhase = "BACKWARD"

        self.tiltCalibrationStartTime = (
            time.monotonic()
        )

        self.calibrationProgress.setValue(
            50
        )

        self.tiltCalibrationLabel.setText(
            "Tilt calibration: Tilt BACKWARD and hold."
        )

        self.tiltLabel.setText(
            "TILT CALIBRATION\n\n"
            "Phase 2 of 2\n"
            "Tilt BACKWARD and hold."
        )

    def finishTiltCalibration(self):
        global tiltCalibrationValid
        global tiltPositionResetValid

        global tiltForwardWorld
        global tiltUpWorld
        global tiltRightWorld

        self.tiltCalibrationPhase = None
        self.calibrationProgress.hide()

        try:
            forwardSamples = getStableSamples(
                self.tiltForwardSamples
            )

            backwardSamples = getStableSamples(
                self.tiltBackwardSamples
            )

            forwardPosition = averagePositions(
                forwardSamples
            )

            backwardPosition = averagePositions(
                backwardSamples
            )

            (
                tiltRightWorld,
                tiltUpWorld,
                tiltForwardWorld,
                detectedDistance
            ) = createCoordinateFrame(
                forwardPosition,
                backwardPosition,
                MINIMUM_TILT_CALIBRATION_DISTANCE,
                "Tilt"
            )

            tiltCalibrationValid = True
            tiltPositionResetValid = False

            self.tiltSamples.clear()
            self.averagedBackwardTilt = 0

            self.tiltCalibrationLabel.setText(
                "Tilt calibration: Calibrated successfully"
            )

            self.tiltCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #20a050;"
            )

            self.tiltResetLabel.setText(
                "Tilt position: Return to neutral and press "
                "Reset Tilt Position"
            )

            self.tiltResetLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d08000;"
            )

            self.tiltLabel.setText(
                "Tilt calibration complete.\n\n"
                "Return to neutral and press "
                "Reset Tilt Position."
            )

            self.updateAxisLabel()
            self.updateButtonStates()

            print(
                "Tilt calibration completed."
            )

            print(
                "Tilt calibration distance: {:.3f} mm".format(
                    detectedDistance
                )
            )

            print(
                "Tilt forward vector: {}".format(
                    formatVector(
                        tiltForwardWorld
                    )
                )
            )

        except Exception as error:
            tiltCalibrationValid = False
            tiltPositionResetValid = False

            tiltForwardWorld = None
            tiltUpWorld = None
            tiltRightWorld = None

            self.tiltCalibrationLabel.setText(
                "Tilt calibration failed: {}".format(
                    error
                )
            )

            self.tiltCalibrationLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d03030;"
            )

            self.tiltLabel.setText(
                "Tilt calibration failed.\n"
                "Tilt farther forward and backward."
            )

            self.updateAxisLabel()
            self.updateButtonStates()

    def resetTiltPosition(self):
        global headZero
        global neutralTiltPitch
        global neutralTiltRoll
        global tiltPositionResetValid

        try:
            if self.isCalibrationActive():
                raise RuntimeError(
                    "Wait for calibration to finish."
                )

            if not tiltCalibrationValid:
                raise RuntimeError(
                    "Calibrate seat tilt first."
                )

            if self.hipTracker is None:
                raise RuntimeError(
                    "No hip tracker is selected."
                )

            if self.headTracker is None:
                raise RuntimeError(
                    "No head tracker is selected."
                )

            hipNode = self.hipTracker.getNode()
            headNode = self.headTracker.getNode()

            if hipNode is None:
                raise RuntimeError(
                    "Hip tracker node is unavailable."
                )

            if headNode is None:
                raise RuntimeError(
                    "Head tracker node is unavailable."
                )

            hipPosition = getPosition(
                hipNode
            )

            headPosition = getPosition(
                headNode
            )

            headZero = list(
                headPosition
            )

            (
                neutralTiltPitch,
                neutralTiltRoll
            ) = calculateTiltAngles(
                hipPosition,
                headPosition
            )

            tiltPositionResetValid = True

            self.tiltSamples.clear()
            self.averagedBackwardTilt = 0

            self.tiltResetLabel.setText(
                "Tilt position: Reset successfully"
            )

            self.tiltResetLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #20a050;"
            )

            self.tiltLabel.setText(
                "Backward Tilt Angle : 0°\n\n"
                "Direction : CENTER"
            )

            self.headLabel.setText(
                "HEAD WORLD : X 0 mm Y 0 mm Z 0 mm"
            )

            print(
                "Tilt neutral position reset."
            )

            print(
                "Neutral pitch: {:.3f} degrees".format(
                    neutralTiltPitch
                )
            )

        except Exception as error:
            tiltPositionResetValid = False

            self.tiltResetLabel.setText(
                "Tilt reset failed: {}".format(
                    error
                )
            )

            self.tiltResetLabel.setStyleSheet(
                "font-weight: bold;"
                "color: #d03030;"
            )

    # ========================================================
    # TRACKING SAMPLE
    # ========================================================

    def sampleTracking(self):
        try:
            if self.hipTracker is None:
                return

            hipNode = self.hipTracker.getNode()

            if hipNode is None:
                return

            currentTime = time.monotonic()

            # ------------------------------------------------
            # HIP CALIBRATION SAMPLING
            # ------------------------------------------------

            if self.hipCalibrationPhase is not None:
                hipPosition = getPosition(
                    hipNode
                )

                elapsed = (
                    currentTime -
                    self.hipCalibrationStartTime
                )

                phaseProgress = min(
                    1.0,
                    elapsed /
                    HIP_PHASE_SECONDS
                )

                if self.hipCalibrationPhase == "FORWARD":
                    self.hipForwardSamples.append(
                        hipPosition
                    )

                    progress = int(
                        phaseProgress * 50.0
                    )

                    remaining = max(
                        0.0,
                        HIP_PHASE_SECONDS - elapsed
                    )

                    self.hipCalibrationLabel.setText(
                        "Hip calibration: Move FORWARD and "
                        "hold. {:.1f} seconds remaining."
                        .format(
                            remaining
                        )
                    )

                    if elapsed >= HIP_PHASE_SECONDS:
                        self.startHipBackwardPhase()

                else:
                    self.hipBackwardSamples.append(
                        hipPosition
                    )

                    progress = 50 + int(
                        phaseProgress * 50.0
                    )

                    remaining = max(
                        0.0,
                        HIP_PHASE_SECONDS - elapsed
                    )

                    self.hipCalibrationLabel.setText(
                        "Hip calibration: Move BACKWARD and "
                        "hold. {:.1f} seconds remaining."
                        .format(
                            remaining
                        )
                    )

                    if elapsed >= HIP_PHASE_SECONDS:
                        self.finishHipCalibration()

                self.calibrationProgress.setValue(
                    min(
                        100,
                        progress
                    )
                )

                return

            # ------------------------------------------------
            # TILT CALIBRATION SAMPLING
            # ------------------------------------------------

            if self.tiltCalibrationPhase is not None:
                if self.headTracker is None:
                    return

                headNode = self.headTracker.getNode()

                if headNode is None:
                    return

                relativePosition = getRelativeHeadPosition(
                    hipNode,
                    headNode
                )

                elapsed = (
                    currentTime -
                    self.tiltCalibrationStartTime
                )

                phaseProgress = min(
                    1.0,
                    elapsed /
                    TILT_PHASE_SECONDS
                )

                if self.tiltCalibrationPhase == "FORWARD":
                    self.tiltForwardSamples.append(
                        relativePosition
                    )

                    progress = int(
                        phaseProgress * 50.0
                    )

                    remaining = max(
                        0.0,
                        TILT_PHASE_SECONDS - elapsed
                    )

                    self.tiltCalibrationLabel.setText(
                        "Tilt calibration: Tilt FORWARD and "
                        "hold. {:.1f} seconds remaining."
                        .format(
                            remaining
                        )
                    )

                    if elapsed >= TILT_PHASE_SECONDS:
                        self.startTiltBackwardPhase()

                else:
                    self.tiltBackwardSamples.append(
                        relativePosition
                    )

                    progress = 50 + int(
                        phaseProgress * 50.0
                    )

                    remaining = max(
                        0.0,
                        TILT_PHASE_SECONDS - elapsed
                    )

                    self.tiltCalibrationLabel.setText(
                        "Tilt calibration: Tilt BACKWARD and "
                        "hold. {:.1f} seconds remaining."
                        .format(
                            remaining
                        )
                    )

                    if elapsed >= TILT_PHASE_SECONDS:
                        self.finishTiltCalibration()

                self.calibrationProgress.setValue(
                    min(
                        100,
                        progress
                    )
                )

                return

            # ------------------------------------------------
            # NORMAL OUTPUT SAMPLING
            # ------------------------------------------------

            hipPosition = getPosition(
                hipNode
            )

            if (
                hipCalibrationValid and
                hipPositionResetValid
            ):
                seatX, seatY, seatZ = transformHipMovement(
                    hipPosition,
                    hipZero
                )

                self.seatSamples.append(
                    (
                        currentTime,
                        seatX,
                        seatY,
                        seatZ
                    )
                )

            if (
                tiltCalibrationValid and
                tiltPositionResetValid and
                self.headTracker is not None
            ):
                headNode = self.headTracker.getNode()

                if headNode is not None:
                    headPosition = getPosition(
                        headNode
                    )

                    currentPitch, currentRoll = (
                        calculateTiltAngles(
                            hipPosition,
                            headPosition
                        )
                    )

                    backwardTilt = calculateBackwardOnlyTilt(
                        currentPitch,
                        neutralTiltPitch
                    )

                    self.tiltSamples.append(
                        (
                            currentTime,
                            backwardTilt,
                            currentPitch,
                            currentRoll
                        )
                    )

            oldestAllowedTime = (
                currentTime -
                AVERAGING_WINDOW_SECONDS
            )

            while (
                self.seatSamples and
                self.seatSamples[0][0] <
                oldestAllowedTime
            ):
                self.seatSamples.popleft()

            while (
                self.tiltSamples and
                self.tiltSamples[0][0] <
                oldestAllowedTime
            ):
                self.tiltSamples.popleft()

        except Exception as error:
            print(
                "Tracking sample error: {}".format(
                    error
                )
            )

    # ========================================================
    # DISPLAY UPDATE
    # ========================================================

    def updateDisplay(self):
        try:
            if self.hipTracker is None:
                return

            if self.headTracker is None:
                return

            hipNode = self.hipTracker.getNode()
            headNode = self.headTracker.getNode()

            if hipNode is None:
                return

            if headNode is None:
                return

            hipPosition = getPosition(
                hipNode
            )

            headPosition = getPosition(
                headNode
            )

            # ------------------------------------------------
            # SEAT AVERAGE
            # ------------------------------------------------

            if (
                hipCalibrationValid and
                hipPositionResetValid and
                self.seatSamples
            ):
                xValues = []
                yValues = []
                zValues = []

                for sample in self.seatSamples:
                    xValues.append(
                        sample[1]
                    )

                    yValues.append(
                        sample[2]
                    )

                    zValues.append(
                        sample[3]
                    )

                self.averagedSeatX = roundValue(
                    applyDeadband(
                        getAverage(xValues),
                        POSITION_DEADBAND
                    )
                )

                if ENABLE_SEAT_VERTICAL_OUTPUT:
                    self.averagedSeatY = roundValue(
                        applyDeadband(
                            getAverage(yValues),
                            VERTICAL_DEADBAND
                        )
                    )

                else:
                    self.averagedSeatY = 0

                self.averagedSeatZ = roundValue(
                    applyDeadband(
                        getAverage(zValues),
                        POSITION_DEADBAND
                    )
                )

            else:
                self.averagedSeatX = 0
                self.averagedSeatY = 0
                self.averagedSeatZ = 0

            # ------------------------------------------------
            # TILT AVERAGE
            # ------------------------------------------------

            diagnosticPitch = 0
            diagnosticRoll = 0

            if (
                tiltCalibrationValid and
                tiltPositionResetValid and
                self.tiltSamples
            ):
                tiltValues = []
                pitchValues = []
                rollValues = []

                for sample in self.tiltSamples:
                    tiltValues.append(
                        sample[1]
                    )

                    pitchValues.append(
                        normalizeAngle180(
                            sample[2] -
                            neutralTiltPitch
                        )
                    )

                    rollValues.append(
                        normalizeAngle180(
                            sample[3] -
                            neutralTiltRoll
                        )
                    )

                self.averagedBackwardTilt = roundValue(
                    applyDeadband(
                        getAverage(tiltValues),
                        ANGLE_DEADBAND
                    )
                )

                diagnosticPitch = roundValue(
                    getAverage(pitchValues)
                )

                diagnosticRoll = roundValue(
                    getAverage(rollValues)
                )

            else:
                self.averagedBackwardTilt = 0

            if self.averagedBackwardTilt > 0:
                tiltDirection = "BACKWARD"

            else:
                tiltDirection = "CENTER"

            # ------------------------------------------------
            # HEAD POSITION
            # ------------------------------------------------

            if tiltPositionResetValid:
                headX = roundValue(
                    applyDeadband(
                        headPosition[0] - headZero[0],
                        POSITION_DEADBAND
                    )
                )

                headY = roundValue(
                    applyDeadband(
                        headPosition[1] - headZero[1],
                        POSITION_DEADBAND
                    )
                )

                headZ = roundValue(
                    applyDeadband(
                        headPosition[2] - headZero[2],
                        POSITION_DEADBAND
                    )
                )

            else:
                headX = 0
                headY = 0
                headZ = 0

            # ------------------------------------------------
            # XYZ LABELS
            # ------------------------------------------------

            if self.showXYZCheck.isChecked():
                self.xyzGroup.show()

                if (
                    hipCalibrationValid and
                    hipPositionResetValid
                ):
                    self.hipLabel.setText(
                        "HIP SEAT FRAME : "
                        "X {} mm Y {} mm Z {} mm".format(
                            self.averagedSeatX,
                            self.averagedSeatY,
                            self.averagedSeatZ
                        )
                    )

                elif hipCalibrationValid:
                    self.hipLabel.setText(
                        "HIP SEAT FRAME : "
                        "Press Reset Hip Position"
                    )

                else:
                    self.hipLabel.setText(
                        "HIP SEAT FRAME : Not calibrated"
                    )

                if tiltPositionResetValid:
                    self.headLabel.setText(
                        "HEAD WORLD : "
                        "X {} mm Y {} mm Z {} mm".format(
                            headX,
                            headY,
                            headZ
                        )
                    )

                elif tiltCalibrationValid:
                    self.headLabel.setText(
                        "HEAD WORLD : "
                        "Press Reset Tilt Position"
                    )

                else:
                    self.headLabel.setText(
                        "HEAD WORLD : Not calibrated"
                    )

            else:
                self.xyzGroup.hide()

            # ------------------------------------------------
            # SEAT OUTPUT
            # ------------------------------------------------

            if self.hipCalibrationPhase is not None:
                pass

            elif (
                hipCalibrationValid and
                hipPositionResetValid
            ):
                if ENABLE_SEAT_VERTICAL_OUTPUT:
                    seatYText = (
                        "Seat Y, Up / Down : {} mm"
                    ).format(
                        self.averagedSeatY
                    )

                else:
                    seatYText = (
                        "Seat Y, Up / Down : 0 mm "
                        "(Output disabled)"
                    )

                self.seatLabel.setText(
                    "Seat X, Forward / Backward : {} mm\n"
                    "{}\n"
                    "Seat Z, Left / Right : {} mm".format(
                        self.averagedSeatX,
                        seatYText,
                        self.averagedSeatZ
                    )
                )

            elif hipCalibrationValid:
                self.seatLabel.setText(
                    "Return to neutral and press "
                    "Reset Hip Position."
                )

            else:
                self.seatLabel.setText(
                    "Press Calibrate Hip Movement"
                )

            # ------------------------------------------------
            # TILT OUTPUT
            # ------------------------------------------------

            if self.tiltCalibrationPhase is not None:
                pass

            elif not tiltCalibrationValid:
                self.tiltLabel.setText(
                    "Press Calibrate Seat Tilt"
                )

            elif not tiltPositionResetValid:
                self.tiltLabel.setText(
                    "Return to neutral and press "
                    "Reset Tilt Position."
                )

            elif self.showDiagnosticsCheck.isChecked():
                self.tiltLabel.setText(
                    "Backward Tilt Angle : {}°\n\n"
                    "Signed Pitch Change : {}°\n"
                    "Signed Roll Change : {}°\n\n"
                    "Direction : {}".format(
                        self.averagedBackwardTilt,
                        diagnosticPitch,
                        diagnosticRoll,
                        tiltDirection
                    )
                )

            else:
                self.tiltLabel.setText(
                    "Backward Tilt Angle : {}°\n\n"
                    "Direction : {}".format(
                        self.averagedBackwardTilt,
                        tiltDirection
                    )
                )

            self.timeLabel.setText(
                "Last display update: {} | "
                "5-second rolling average | "
                "Backward tilt only".format(
                    time.strftime(
                        "%H:%M:%S"
                    )
                )
            )

        except Exception as error:
            print(
                "Display update error: {}".format(
                    error
                )
            )


# ============================================================
# SINGLE INSTANCE
# ============================================================

try:
    seatMotionTool.close()
    seatMotionTool.deleteLater()

except Exception:
    pass


seatMotionTool = SeatMotionTool()
seatMotionTool.show()