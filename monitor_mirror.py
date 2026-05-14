import sys
import mss
import mss.tools
import pyautogui
import dxcam
import logging
import time
import cv2
import os

# Fix DPI Awareness issue before QApplication starts
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox, QHBoxLayout
from PySide6.QtCore import QTimer, Qt, QPoint, QRect
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath, QColor, QIcon

class VideoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.setAttribute(Qt.WA_OpaquePaintEvent) # Optimization: don't clear background
        self.setMouseTracking(True)
        self.cursor_pos = None # Relative to monitor
        self.monitor_info = None

    def setImage(self, image):
        self.image = image
        self.update() # Trigger paintEvent

    def paintEvent(self, event):
        if self.image:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, False) # Performance
            painter.setRenderHint(QPainter.SmoothPixmapTransform, False) # Performance
            
            # Draw the image centered
            target_rect = self.rect()
            img_size = self.image.size()
            
            # Maintain aspect ratio
            w_ratio = target_rect.width() / img_size.width()
            h_ratio = target_rect.height() / img_size.height()
            ratio = min(w_ratio, h_ratio)
            
            new_w = int(img_size.width() * ratio)
            new_h = int(img_size.height() * ratio)
            
            x = (target_rect.width() - new_w) // 2
            y = (target_rect.height() - new_h) // 2
            
            
            painter.drawImage(QRect(x, y, new_w, new_h), self.image)

            # Draw Cursor on the SCALED image (much more efficient)
            if self.cursor_pos and self.monitor_info:
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Scale cursor position to widget coordinates
                rel_x = x + (self.cursor_pos[0] / self.monitor_info['width']) * new_w
                rel_y = y + (self.cursor_pos[1] / self.monitor_info['height']) * new_h
                
                # Draw a simple arrow cursor
                painter.setBrush(Qt.white)
                painter.setPen(Qt.black)
                path = QPainterPath()
                path.moveTo(rel_x, rel_y)
                path.lineTo(rel_x, rel_y + 15)
                path.lineTo(rel_x + 5, rel_y + 10)
                path.lineTo(rel_x + 10, rel_y + 15)
                path.closeSubpath()
                painter.drawPath(path)
            
            painter.end()

# Disable pyautogui's fail-safe to prevent it from crashing if the mouse hits a corner
pyautogui.FAILSAFE = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonitorMirror(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor Mirror")
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        logger.info("Initializing Monitor Mirror...")
        
        self.sct = mss.mss()
        self.monitors = self.sct.monitors
        self.current_monitor_index = 1 if len(self.monitors) > 1 else 0
        
        # Performance Tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        self.capture_mode = "None"
        
        # DXCAM Setup
        self.camera = None
        self.capture_mode = "MSS (Compatibility Mode)"
        
        for device_idx in range(3): # Try first 3 GPU devices
            try:
                output_idx = self.current_monitor_index - 1 if self.current_monitor_index > 0 else 0
                logger.info(f"Attempting DXCAM: Device {device_idx}, Output {output_idx}")
                cam = dxcam.create(device_idx=device_idx, output_idx=output_idx)
                if cam:
                    cam.start(target_fps=60)
                    self.camera = cam
                    self.capture_mode = "DXCAM (High Performance)"
                    logger.info(f"DXCAM initialized successfully on Device {device_idx}.")
                    break
            except Exception as e:
                logger.warning(f"DXCAM failed on Device {device_idx}: {e}")
        
        if not self.camera:
            logger.warning("All DXCAM attempts failed. Using MSS fallback.")
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Monitor Selection
        self.selector_layout = QHBoxLayout()
        self.selector_label = QLabel("Select Monitor:")
        self.monitor_combo = QComboBox()
        for i, m in enumerate(self.monitors):
            if i == 0: continue # Monitor 0 is usually the combined screen
            self.monitor_combo.addItem(f"Monitor {i} ({m['width']}x{m['height']} at {m['left']},{m['top']})")
        
        self.monitor_combo.currentIndexChanged.connect(self.change_monitor)
        self.selector_layout.addWidget(self.selector_label)
        self.selector_layout.addWidget(self.monitor_combo)
        self.layout.addLayout(self.selector_layout)
        
        # Mirror Display (Optimized Custom Widget)
        self.display_widget = VideoWidget()
        self.layout.addWidget(self.display_widget)
        
        # State for coordinate mapping
        self.current_display_rect = QRect()
        
        # Timer for screen capture
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16) # ~60 FPS
        
        # State for mouse interaction
        self.is_pressing = False
        
        # Set window size
        self.resize(800, 600)

    def change_monitor(self, index):
        self.current_monitor_index = index + 1 # +1 because 0 is all monitors
        if self.camera:
            self.camera.stop()
            self.camera = None
            
        for device_idx in range(3):
            try:
                logger.info(f"Switching DXCAM: Device {device_idx}, Output {index}")
                cam = dxcam.create(device_idx=device_idx, output_idx=index)
                if cam:
                    cam.start(target_fps=60)
                    self.camera = cam
                    logger.info(f"DXCAM switched successfully on Device {device_idx}.")
                    break
            except Exception as e:
                logger.warning(f"DXCAM switch failed on Device {device_idx}: {e}")
        
        if not self.camera:
            logger.warning("DXCAM switch failed for all devices. Using MSS.")

    def update_frame(self):
        monitor = self.monitors[self.current_monitor_index]
        widget_size = self.display_widget.size()
        if widget_size.width() <= 0 or widget_size.height() <= 0:
            return

        frame = None
        current_mode = "MSS"
        if self.camera:
            # Efficiently get the latest frame
            frame = self.camera.get_latest_frame()
            current_mode = "DXCAM"
        
        if frame is not None:
            # We skip resizing here and let VideoWidget handle it in paintEvent
            # This is much more efficient as it uses hardware acceleration if available via QPainter
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            # Create QImage directly from the DXCAM buffer (no copy)
            img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        else:
            # Fallback to MSS
            sct_img = self.sct.grab(monitor)
            img = QImage(sct_img.rgb, sct_img.size[0], sct_img.size[1], QImage.Format_RGB888)
            current_mode = "MSS (Fallback)"

        # Pass cursor info to widget for efficient drawing
        cursor_x, cursor_y = pyautogui.position()
        if (monitor['left'] <= cursor_x < monitor['left'] + monitor['width'] and
            monitor['top'] <= cursor_y < monitor['top'] + monitor['height']):
            self.display_widget.cursor_pos = (cursor_x - monitor['left'], cursor_y - monitor['top'])
            self.display_widget.monitor_info = monitor
        else:
            self.display_widget.cursor_pos = None

        # Update Display
        self.display_widget.setImage(img)

        # Calculate display rect for mouse mapping
        img_size = img.size()
        w_ratio = widget_size.width() / img_size.width()
        h_ratio = widget_size.height() / img_size.height()
        ratio = min(w_ratio, h_ratio)
        new_w = int(img_size.width() * ratio)
        new_h = int(img_size.height() * ratio)
        self.current_display_rect = QRect(
            (widget_size.width() - new_w) // 2,
            (widget_size.height() - new_h) // 2,
            new_w,
            new_h
        )

        # Update Performance Stats
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.setWindowTitle(f"Monitor Mirror - {current_mode} - {self.fps:.1f} FPS")
            self.frame_count = 0
            self.start_time = time.time()

    def map_to_monitor(self, pos):
        # Translate widget coordinates to display_rect coordinates
        if not self.current_display_rect.contains(pos):
            return None
            
        rel_x_rect = pos.x() - self.current_display_rect.x()
        rel_y_rect = pos.y() - self.current_display_rect.y()
        
        # Map to monitor coordinates
        monitor = self.monitors[self.current_monitor_index]
        mon_x = monitor['left'] + int((rel_x_rect / self.current_display_rect.width()) * monitor['width'])
        mon_y = monitor['top'] + int((rel_y_rect / self.current_display_rect.height()) * monitor['height'])
        
        return mon_x, mon_y

    def mouseMoveEvent(self, event):
        pos = self.display_widget.mapFrom(self, event.position().toPoint())
        mon_pos = self.map_to_monitor(pos)
        if mon_pos and self.is_pressing:
            pyautogui.moveTo(mon_pos[0], mon_pos[1])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressing = True
            pos = self.display_widget.mapFrom(self, event.position().toPoint())
            mon_pos = self.map_to_monitor(pos)
            if mon_pos:
                pyautogui.mouseDown(mon_pos[0], mon_pos[1], button='left')

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressing = False
            pos = self.display_widget.mapFrom(self, event.position().toPoint())
            mon_pos = self.map_to_monitor(pos)
            if mon_pos:
                pyautogui.mouseUp(mon_pos[0], mon_pos[1], button='left')
        elif event.button() == Qt.RightButton:
             pos = self.display_widget.mapFrom(self, event.position().toPoint())
             mon_pos = self.map_to_monitor(pos)
             if mon_pos:
                 pyautogui.click(mon_pos[0], mon_pos[1], button='right')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitorMirror()
    window.show()
    sys.exit(app.exec())
