import sys
import os
import tempfile
import re

# PySide6 is required for VRED 2024, 2025, and 2026+ (API v2)
from PySide6 import QtCore, QtGui, QtWidgets

# Import VRED API v2
try:
    import vr
    from vr import vrUiService
except ImportError:
    vrUiService = None

class SeatMotionCalibrationUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SeatMotionCalibrationUI, self).__init__(parent)
        self.setWindowTitle("Seat Motion Calibration Tool")
        
        # Enforce exactly 750 width, let the layout strictly manage the height
        self.setMinimumWidth(750)
        
        # Load the Mahindra watermark logo
        logo_path = r"\\10.204.16.58\sharefolder\Mahindra-Mahindra-New-Logo.png"
        self.watermark_pixmap = QtGui.QPixmap(logo_path)
        
        # State tracker for the coordinate toggle
        self.coordinates_visible = False
        
        # Set the main background color and global font
        self.setStyleSheet("""
            SeatMotionCalibrationUI { background-color: #f3f3f3; }
            QWidget { font-family: "Segoe UI", Arial, sans-serif; }
            QGroupBox {
                font-size: 11px; font-weight: bold; color: #555555;
                border: 1px solid #d3d3d3; border-radius: 8px;
                margin-top: 12px; background-color: transparent;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
        """)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)
        
        # PySide6 Strict Enums Updates
        self.main_layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.title_label = QtWidgets.QLabel("Seat Motion Calibration Tool")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a365d; background: transparent; border: none;")
        self.main_layout.addWidget(self.title_label)

        self.build_tracker_setup()
        self.build_data_output()
        self.build_active_trackers() 
        self.build_footer()
        
        self.adjustSize()

    def paintEvent(self, event):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        
        # PySide6 Strict Enum Update
        self.style().drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
        
        if hasattr(self, 'watermark_pixmap') and not self.watermark_pixmap.isNull():
            # PySide6 Strict Enum Updates
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setOpacity(0.04) 
            scaled_pix = self.watermark_pixmap.scaled(
                int(self.width() * 0.7), 
                int(self.height() * 0.7), 
                QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap((self.width() - scaled_pix.width()) // 2, (self.height() - scaled_pix.height()) // 2 + 20, scaled_pix)

    def build_tracker_setup(self):
        group = QtWidgets.QGroupBox("• TRACKER SETUP")
        layout = QtWidgets.QHBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.addWidget(self.create_standard_label("Hip Tracker"))
        hip_combo = QtWidgets.QComboBox()
        hip_combo.addItems(["HTC VIVE Tracker"])
        hip_combo.setStyleSheet(self.get_combobox_style())
        layout.addWidget(hip_combo)
        layout.addSpacing(25)
        layout.addWidget(self.create_standard_label("Head Tracker"))
        head_combo = QtWidgets.QComboBox()
        head_combo.addItems(["HTC VIVE Tracker"])
        head_combo.setStyleSheet(self.get_combobox_style())
        layout.addWidget(head_combo)
        layout.addStretch()
        refresh_btn = QtWidgets.QPushButton("↻ Refresh")
        refresh_btn.setStyleSheet(self.get_solid_blue_btn_style(large=False))
        refresh_btn.setMinimumWidth(100)
        layout.addWidget(refresh_btn)
        self.main_layout.addWidget(group)

    def build_data_output(self):
        group = QtWidgets.QGroupBox("• DATA OUTPUT")
        layout = QtWidgets.QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)

        # Seat Position
        seat_layout = QtWidgets.QHBoxLayout()
        lbl_seat = self.create_standard_label("Seat position")
        lbl_seat.setMinimumWidth(100)
        seat_layout.addWidget(lbl_seat)
        seat_layout.addWidget(self.create_inline_box("X = ", "1496 mm"))
        seat_layout.addWidget(self.create_inline_box("Z = ", "326 mm"))
        seat_layout.addStretch()
        layout.addLayout(seat_layout)

        # Tilt Output Row
        tilt_layout = QtWidgets.QHBoxLayout()
        lbl_tilt = self.create_standard_label("Tilt Output")
        lbl_tilt.setMinimumWidth(100)
        tilt_layout.addWidget(lbl_tilt)
        
        self.tilt_angle_box = self.create_inline_box("Angle = ", "66°")
        self.pitch_box = self.create_inline_box("Pitch = ", "65°")
        self.roll_box = self.create_inline_box("Roll = ", "14°")
        self.pitch_box.setVisible(False)
        self.roll_box.setVisible(False)
        
        tilt_layout.addWidget(self.tilt_angle_box)
        tilt_layout.addWidget(self.pitch_box)
        tilt_layout.addWidget(self.roll_box)
        
        tilt_layout.addStretch()
        
        # Checkbox
        self.show_pitch_roll_cb = QtWidgets.QCheckBox("Show pitch/Roll")
        self.show_pitch_roll_cb.setStyleSheet(self.get_custom_checkbox_style())
        self.show_pitch_roll_cb.clicked.connect(self.toggle_pitch_roll)
        tilt_layout.addSpacing(10)
        tilt_layout.addWidget(self.show_pitch_roll_cb)
        layout.addLayout(tilt_layout)

        self.main_layout.addWidget(group)

    def build_active_trackers(self):
        group = QtWidgets.QGroupBox("• ACTIVE TRACKERS")
        layout = QtWidgets.QVBoxLayout(group)
        layout.setContentsMargins(15, 10, 15, 15)
        layout.setSpacing(8)
        
        # Header Row
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.create_standard_label("Active Trackers."))
        
        # ADDED: Active Tracker tags/indicators based on sketch
        header_layout.addSpacing(10)
        header_layout.addWidget(self.create_indicator_pill("Tracker-1"))
        header_layout.addWidget(self.create_indicator_pill("Tracker-2"))
        
        header_layout.addStretch() # Pushes button to far right
        
        self.show_coord_btn = QtWidgets.QPushButton("Show Coordinates")
        self.show_coord_btn.setStyleSheet(self.get_outline_blue_btn_style())
        self.show_coord_btn.clicked.connect(self.toggle_coordinates)
        header_layout.addWidget(self.show_coord_btn)
        layout.addLayout(header_layout)

        # Tracker List Container
        self.trackers_container = QtWidgets.QWidget()
        table_layout = QtWidgets.QVBoxLayout(self.trackers_container)
        table_layout.setContentsMargins(0, 10, 0, 0)
        table_layout.setSpacing(10)
        
        # Hip Tracker Row
        hip_layout = QtWidgets.QHBoxLayout()
        lbl_hip = self.create_standard_label("Hip Tracker")
        lbl_hip.setMinimumWidth(100)
        hip_layout.addWidget(lbl_hip)
        hip_layout.addWidget(self.create_inline_box("X = ", "1496"))
        hip_layout.addWidget(self.create_inline_box("Y = ", "2234")) 
        hip_layout.addWidget(self.create_inline_box("Z = ", "2250"))
        hip_layout.addStretch()
        table_layout.addLayout(hip_layout)

        # Head Tracker Row 
        head_layout = QtWidgets.QHBoxLayout()
        lbl_head = self.create_standard_label("Head Tracker")
        lbl_head.setMinimumWidth(100)
        head_layout.addWidget(lbl_head)
        head_layout.addWidget(self.create_inline_box("X = ", "1541"))
        head_layout.addWidget(self.create_inline_box("Y = ", "3456"))
        head_layout.addWidget(self.create_inline_box("Z = ", "2250"))
        head_layout.addStretch()
        table_layout.addLayout(head_layout)

        self.trackers_container.setVisible(False)
        layout.addWidget(self.trackers_container)
        self.main_layout.addWidget(group)

    def build_footer(self):
        footer_widget = QtWidgets.QWidget()
        footer_layout = QtWidgets.QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 10, 0, 0)
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.addWidget(QtWidgets.QLabel("Last Update : 12:11:04", styleSheet="color: #555555; font-size: 10px;"))
        status_layout.addStretch()
        status_layout.addWidget(QtWidgets.QLabel("Direction : FORWARD RIGHT", styleSheet="color: #555555; font-size: 10px; font-weight: bold;"))
        footer_layout.addLayout(status_layout)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch() 
        btn_layout.addWidget(QtWidgets.QPushButton("NEUTRAL POSITION HIP TRACKER", styleSheet=self.get_solid_blue_btn_style(large=True)))
        btn_layout.addSpacing(15)
        btn_layout.addWidget(QtWidgets.QPushButton("NEUTRAL POSITION HEAD TRACKER", styleSheet=self.get_solid_blue_btn_style(large=True)))
        btn_layout.addStretch() 
        
        footer_layout.addLayout(btn_layout)
        self.main_layout.addWidget(footer_widget)

    def toggle_coordinates(self):
        self.coordinates_visible = not self.coordinates_visible
        self.show_coord_btn.setText("Hide Coordinates" if self.coordinates_visible else "Show Coordinates")
        self.trackers_container.setVisible(self.coordinates_visible)
        self.adjustSize()
        
    def toggle_pitch_roll(self):
        is_checked = self.show_pitch_roll_cb.isChecked()
        self.pitch_box.setVisible(is_checked)
        self.roll_box.setVisible(is_checked)
        self.adjustSize()

    # --- UI Helpers ---
    def get_custom_checkbox_style(self):
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "vred_blue_tick.png").replace("\\", "/")
        if not os.path.exists(file_path):
            pixmap = QtGui.QPixmap(28, 28)
            
            # PySide6 Strict Enum Updates
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            
            pen = QtGui.QPen(QtGui.QColor("#1459c2"))
            pen.setWidth(5)
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(5, 14, 11, 21)
            painter.drawLine(11, 21, 23, 7)
            painter.end()
            pixmap.save(file_path, "PNG")
            
        return f"""
            QCheckBox {{ color: #555555; font-size: 11px; font-weight: bold; background: transparent; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; background-color: #ffffff; border: 1px solid #a0a0a0; border-radius: 3px; }}
            QCheckBox::indicator:hover {{ border: 1px solid #1459c2; }}
            QCheckBox::indicator:checked {{ background-color: #ffffff; border: 1px solid #1459c2; image: url({file_path}); }}
        """

    def create_inline_box(self, prefix, value):
        lbl = QtWidgets.QLabel(f'<span style="color: #1459c2; font-weight: bold;">{prefix}</span><span style="color: #333333;">{value}</span>')
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("border: 1px solid #c0c0c0; border-radius: 8px; background-color: rgba(255, 255, 255, 210); padding: 4px 14px; font-size: 12px; min-width: 80px;")
        return lbl

    def create_indicator_pill(self, text):
        """Creates a small bordered tag to indicate active components."""
        lbl = QtWidgets.QLabel(text)
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("""
            QLabel {
                color: #1459c2;
                border: 1px solid #1459c2;
                border-radius: 6px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: bold;
                background-color: rgba(20, 89, 194, 0.05);
            }
        """)
        return lbl

    def get_solid_blue_btn_style(self, large=False):
        return f"QPushButton {{ background-color: #1459c2; color: #ffffff; font-weight: bold; font-size: {'12px' if large else '11px'}; border-radius: 4px; padding: {'8px 20px' if large else '5px 15px'}; border: none; }} QPushButton:hover {{ background-color: #1a65db; }}"

    def get_outline_blue_btn_style(self):
        return "QPushButton { background-color: transparent; color: #1459c2; border: 1px solid #1459c2; border-radius: 12px; padding: 4px 14px; font-size: 11px; font-weight: bold; } QPushButton:hover { background-color: rgba(20, 89, 194, 0.1); }"

    def get_combobox_style(self):
        return "QComboBox { border: 1px solid #c0c0c0; border-radius: 12px; padding: 3px 12px; background-color: rgba(255, 255, 255, 200); color: #333333; min-width: 140px; font-size: 11px; } QComboBox::drop-down { border: none; width: 20px; }"

    def create_standard_label(self, text):
        return QtWidgets.QLabel(text, styleSheet="color: #444444; font-size: 12px; font-weight: 500; background: transparent; border: none;")

# ============================================================
# VRED 2026.2
# Seat Motion Calibration Tool
# ============================================================
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
# UI COMPATIBILITY ADAPTERS
# These adapters connect the supplied UI widgets to the unchanged core methods.
# They do not alter layout, styling, sizing, or visual behavior.
# ============================================================
class _StateProxy:
    def __init__(self, getter):
        self._getter = getter
    def isChecked(self):
        return bool(self._getter())

class _CoordinateProxy:
    def __init__(self, container, xLabel, yLabel, zLabel):
        self.container = container
        self.labels = (xLabel, yLabel, zLabel)
    def setText(self, text):
        values = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
        if len(values) >= 3:
            prefixes = ("X = ", "Y = ", "Z = ")
            for label, prefix, value in zip(self.labels, prefixes, values[-3:]):
                label.setText('<span style="color: #1459c2; font-weight: bold;">{}</span><span style="color: #333333;">{}</span>'.format(prefix, value))
    def show(self):
        self.container.setVisible(True)
    def hide(self):
        self.container.setVisible(False)

class _SeatProxy:
    def __init__(self, xLabel, zLabel):
        self.xLabel = xLabel
        self.zLabel = zLabel
    def setText(self, text):
        values = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
        if len(values) >= 2:
            self.xLabel.setText('<span style="color: #1459c2; font-weight: bold;">X = </span><span style="color: #333333;">{} mm</span>'.format(values[0]))
            self.zLabel.setText('<span style="color: #1459c2; font-weight: bold;">Z = </span><span style="color: #333333;">{} mm</span>'.format(values[1]))

class _TiltProxy:
    def __init__(self, angleLabel, pitchLabel, rollLabel, directionLabel):
        self.angleLabel = angleLabel
        self.pitchLabel = pitchLabel
        self.rollLabel = rollLabel
        self.directionLabel = directionLabel
    def setText(self, text):
        angle = re.search(r"Tilt Angle\s*:\s*(-?\d+)", text)
        pitch = re.search(r"Pitch\s*:\s*(-?\d+)", text)
        roll = re.search(r"Roll\s*:\s*(-?\d+)", text)
        direction = re.search(r"Direction\s*:\s*([^\n]+)", text)
        if angle:
            self.angleLabel.setText('<span style="color: #1459c2; font-weight: bold;">Angle = </span><span style="color: #333333;">{}°</span>'.format(angle.group(1)))
        if pitch:
            self.pitchLabel.setText('<span style="color: #1459c2; font-weight: bold;">Pitch = </span><span style="color: #333333;">{}°</span>'.format(pitch.group(1)))
        if roll:
            self.rollLabel.setText('<span style="color: #1459c2; font-weight: bold;">Roll = </span><span style="color: #333333;">{}°</span>'.format(roll.group(1)))
        if direction:
            self.directionLabel.setText("Direction : " + direction.group(1).strip())

class _ActiveProxy:
    def __init__(self, pills):
        self.pills = pills
    def setText(self, text):
        names = re.findall(r"tracker-\d+", text, re.IGNORECASE)
        for index, pill in enumerate(self.pills):
            if index < len(names):
                pill.setText(names[index].title())
                pill.show()
            else:
                pill.hide()


# ============================================================
# INTEGRATION CLASS
# Supplied UI is inherited unchanged. Core methods below are copied verbatim.
# ============================================================
class SeatMotionTool(SeatMotionCalibrationUI):
    def __init__(self, parent=None):
        super(SeatMotionTool, self).__init__(parent)
        self.hipTracker = None
        self.headTracker = None

        # UI-only display adaptation. Core motion logic remains untouched.
        self._displayScale = 1.0
        self._displayUpdatePending = False
        self._baseWindowStyle = self.styleSheet()
        self._baseMinimumWidth = self.minimumWidth()
        self._captureBaseTypography()
        self._setupAdaptiveDisplay()

        combos = self.findChildren(QtWidgets.QComboBox)
        buttons = self.findChildren(QtWidgets.QPushButton)
        labels = self.findChildren(QtWidgets.QLabel)

        self.hipCombo = combos[0]
        self.headCombo = combos[1]
        self.refreshButton = next(b for b in buttons if "Refresh" in b.text())
        self.resetHipButton = next(b for b in buttons if b.text() == "NEUTRAL POSITION HIP TRACKER")
        self.resetHeadButton = next(b for b in buttons if b.text() == "NEUTRAL POSITION HEAD TRACKER")
        self.showPitchRollCheck = self.show_pitch_roll_cb
        self.showXYZCheck = _StateProxy(lambda: self.coordinates_visible)

        inline = [label for label in labels if label.text().startswith('<span style="color: #1459c2')]
        # Supplied UI creation order: seat X/Z, angle/pitch/roll, hip XYZ, head XYZ.
        seatX, seatZ = inline[0], inline[1]
        angle, pitch, roll = inline[2], inline[3], inline[4]
        hipX, hipY, hipZ = inline[5], inline[6], inline[7]
        headX, headY, headZ = inline[8], inline[9], inline[10]

        footerLabels = [label for label in labels if label.text().startswith("Last Update") or label.text().startswith("Direction")]
        self.timeLabel = next(label for label in footerLabels if label.text().startswith("Last Update"))
        directionLabel = next(label for label in footerLabels if label.text().startswith("Direction"))
        pills = [label for label in labels if label.text() in ("Tracker-1", "Tracker-2")]

        self.connectedLabel = _ActiveProxy(pills)
        self.hipLabel = _CoordinateProxy(self.trackers_container, hipX, hipY, hipZ)
        self.headLabel = _CoordinateProxy(self.trackers_container, headX, headY, headZ)
        self.seatLabel = _SeatProxy(seatX, seatZ)
        self.tiltLabel = _TiltProxy(angle, pitch, roll, directionLabel)

        # Remove only the placeholder items inserted by uiLogic.py.
        self.hipCombo.clear()
        self.headCombo.clear()

        # Core signal wiring and timer behavior.
        self.refreshButton.clicked.connect(self.refreshTrackers)
        self.resetHipButton.clicked.connect(self.resetHip)
        self.resetHeadButton.clicked.connect(self.resetHead)
        self.hipCombo.currentIndexChanged.connect(self.updateSelectedTrackers)
        self.headCombo.currentIndexChanged.connect(self.updateSelectedTrackers)
        self.refreshTrackers()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start(UPDATE_INTERVAL)


    # ========================================================
    # DISPLAY ADAPTATION - UI ONLY
    # ========================================================
    def _captureBaseTypography(self):
        """Store original fonts and local styles for resolution-aware scaling."""
        widgets = [self] + self.findChildren(QtWidgets.QWidget)
        for widget in widgets:
            font = widget.font()
            widget.setProperty('_baseFontFamily', font.family())
            widget.setProperty('_baseFontPointSize', font.pointSizeF())
            widget.setProperty('_baseFontPixelSize', font.pixelSize())
            widget.setProperty('_baseFontWeight', font.weight())
            widget.setProperty('_baseFontItalic', font.italic())
            widget.setProperty('_baseLocalStyle', widget.styleSheet())

    def _applyAutomaticFonts(self, scale):
        """Scale all inherited and widget-specific fonts from their originals."""
        widgets = [self] + self.findChildren(QtWidgets.QWidget)
        for widget in widgets:
            baseStyle = widget.property('_baseLocalStyle')
            if baseStyle:
                widget.setStyleSheet(
                    self._scaledStyleSheet(str(baseStyle), scale)
                )

            font = QtGui.QFont(widget.font())
            family = widget.property('_baseFontFamily')
            pointSize = widget.property('_baseFontPointSize')
            pixelSize = widget.property('_baseFontPixelSize')
            weight = widget.property('_baseFontWeight')
            italic = widget.property('_baseFontItalic')

            if family:
                font.setFamily(str(family))
            if pixelSize is not None and int(pixelSize) > 0:
                font.setPixelSize(max(8, int(round(int(pixelSize) * scale))))
            elif pointSize is not None and float(pointSize) > 0:
                font.setPointSizeF(max(7.0, float(pointSize) * scale))
            if weight is not None:
                font.setWeight(QtGui.QFont.Weight(int(weight)))
            if italic is not None:
                font.setItalic(bool(italic))
            widget.setFont(font)

    def _setupAdaptiveDisplay(self):
        """Scale the supplied UI for the monitor that currently contains it."""
        QtCore.QTimer.singleShot(0, self._connectDisplaySignals)

    def _connectDisplaySignals(self):
        handle = self.windowHandle()
        if handle is not None:
            try:
                handle.screenChanged.disconnect(self._onDisplayChanged)
            except (TypeError, RuntimeError):
                pass
            handle.screenChanged.connect(self._onDisplayChanged)
        self._scheduleDisplayAdjustment()

    def _onDisplayChanged(self, _screen):
        self._scheduleDisplayAdjustment()

    def _scheduleDisplayAdjustment(self):
        if self._displayUpdatePending:
            return
        self._displayUpdatePending = True
        QtCore.QTimer.singleShot(75, self._applyDisplayAdjustment)

    def _currentDisplay(self):
        handle = self.windowHandle()
        if handle is not None and handle.screen() is not None:
            return handle.screen()
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos())
        if screen is None:
            screen = QtGui.QGuiApplication.primaryScreen()
        return screen

    @staticmethod
    def _scaledStyleSheet(styleSheet, scale):
        """Scale pixel-based fonts, padding, radius and border UI metrics."""
        metricPattern = re.compile(
            r'(?P<number>\d+(?:\.\d+)?)px'
        )

        def replaceMetric(match):
            value = float(match.group('number'))
            scaled = max(1, int(round(value * scale)))
            return '{}px'.format(scaled)

        return metricPattern.sub(replaceMetric, styleSheet)

    def _scaleLayoutTree(self, layout, scale):
        """Scale margins and spacing while preserving the supplied layout."""
        if layout is None:
            return
        baseMargins = layout.property('_baseMargins')
        if baseMargins is None:
            margins = layout.contentsMargins()
            baseMargins = (
                margins.left(), margins.top(),
                margins.right(), margins.bottom()
            )
            layout.setProperty('_baseMargins', baseMargins)
        layout.setContentsMargins(*[
            int(round(value * scale)) for value in baseMargins
        ])

        baseSpacing = layout.property('_baseSpacing')
        if baseSpacing is None:
            baseSpacing = layout.spacing()
            layout.setProperty('_baseSpacing', baseSpacing)
        if baseSpacing >= 0:
            layout.setSpacing(int(round(baseSpacing * scale)))

        for index in range(layout.count()):
            item = layout.itemAt(index)
            childLayout = item.layout()
            if childLayout is not None:
                self._scaleLayoutTree(childLayout, scale)
            widget = item.widget()
            if widget is not None and widget.layout() is not None:
                self._scaleLayoutTree(widget.layout(), scale)

    def _applyDisplayAdjustment(self):
        self._displayUpdatePending = False
        screen = self._currentDisplay()
        if screen is None:
            return

        available = screen.availableGeometry()
        widthScale = available.width() / 1920.0
        heightScale = available.height() / 1080.0
        resolutionScale = min(widthScale, heightScale)

        # Qt reports logical DPI after operating-system scaling. Combining it
        # with usable resolution keeps the tool readable on HD, QHD and 4K
        # displays, including large-format 50-inch and 110-inch screens.
        logicalDpiScale = max(0.75, screen.logicalDotsPerInch() / 96.0)
        scale = resolutionScale * logicalDpiScale
        scale = max(0.80, min(2.20, scale))
        self._displayScale = scale

        # Scale the exact supplied styles; no colors, hierarchy or arrangement
        # are changed.
        self.setStyleSheet(
            self._scaledStyleSheet(self._baseWindowStyle, scale)
        )
        self._applyAutomaticFonts(scale)
        self.setMinimumWidth(int(round(self._baseMinimumWidth * scale)))
        self._scaleLayoutTree(self.layout(), scale)

        # Scale explicit widget constraints used by the supplied UI.
        for widget in self.findChildren(QtWidgets.QWidget):
            baseMinWidth = widget.property('_baseMinWidth')
            if baseMinWidth is None:
                baseMinWidth = widget.minimumWidth()
                widget.setProperty('_baseMinWidth', baseMinWidth)
            if baseMinWidth > 0:
                widget.setMinimumWidth(int(round(baseMinWidth * scale)))

            baseMinHeight = widget.property('_baseMinHeight')
            if baseMinHeight is None:
                baseMinHeight = widget.minimumHeight()
                widget.setProperty('_baseMinHeight', baseMinHeight)
            if baseMinHeight > 0:
                widget.setMinimumHeight(int(round(baseMinHeight * scale)))

        self.adjustSize()

        # Keep the complete tool inside the usable desktop and center it on the
        # detected monitor. availableGeometry excludes the taskbar/dock.
        size = self.size()
        maxWidth = int(available.width() * 0.96)
        maxHeight = int(available.height() * 0.96)
        if size.width() > maxWidth or size.height() > maxHeight:
            fitScale = min(
                maxWidth / float(max(1, size.width())),
                maxHeight / float(max(1, size.height()))
            )
            correctedScale = max(0.70, scale * fitScale)
            if abs(correctedScale - scale) > 0.01:
                self._displayScale = correctedScale
                self.setStyleSheet(
                    self._scaledStyleSheet(
                        self._baseWindowStyle, correctedScale
                    )
                )
                self._applyAutomaticFonts(correctedScale)
                self.setMinimumWidth(
                    int(round(self._baseMinimumWidth * correctedScale))
                )
                self._scaleLayoutTree(self.layout(), correctedScale)
                self.adjustSize()

        frame = self.frameGeometry()
        frame.moveCenter(available.center())
        self.move(frame.topLeft())

    def showEvent(self, event):
        super(SeatMotionTool, self).showEvent(event)
        self._scheduleDisplayAdjustment()

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

parent = vrUiService.getVredMainWindow() if vrUiService else None
seatMotionTool = SeatMotionTool(parent)
if parent:
    seatMotionTool.setWindowFlags(QtCore.Qt.WindowType.Tool)
seatMotionTool.show()
QtCore.QTimer.singleShot(150, seatMotionTool._scheduleDisplayAdjustment)
