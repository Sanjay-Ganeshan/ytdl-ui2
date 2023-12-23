import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, \
    QAction, QVBoxLayout, QHBoxLayout, QWidget, QRadioButton, QLineEdit, \
    QPushButton, QScrollArea, QLabel, QFrame, QProgressBar
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QEvent

from backend import validate_url
import typing as T

class ModeSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        self.audio_button = QRadioButton("Audio")
        self.audio_button.setChecked(True)
        self.video_button = QRadioButton("Video")
        self.both_button = QRadioButton("Both")
        layout.addWidget(self.audio_button)
        layout.addWidget(self.video_button)
        layout.addWidget(self.both_button)

class UrlEntryWidget(QWidget):
    def __init__(self, handle_url: T.Optional[T.Callable[[str], bool]] = None):
        super().__init__()
        self.handle_url: T.Optional[T.Callable[[str], bool]] = handle_url
        layout = QHBoxLayout(self)
        self.url_entry = QLineEdit()
        self.add_button = QPushButton("Add")
        layout.addWidget(self.url_entry)
        layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.on_add_clicked)
        self.url_entry.returnPressed.connect(self.on_return_pressed)


    def warn_invalid(self) -> None:
        pass

    def on_return_pressed(self):
        # Emit a custom signal or call a method directly
        # For example, you might want to simulate clicking the 'Add to Queue' button
        self.on_add_clicked()

    def on_add_clicked(self) -> None:
        url = validate_url(self.url_entry.text())

        if url is None:
            self.warn_invalid()
            return
        
        if self.handle_url is not None and not self.handle_url(url):
            self.warn_invalid()
        else:
            self.url_entry.clear()

class QueueDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.queue: T.List[str] = []

    def add_to_queue(self, url: str) -> bool:
        if not url:
            return False
        
        self.queue.append(url)
        self.update_queue_display()
        return True

    def update_queue_display(self):
        # Clear the current queue display
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        # Add each URL in the queue to the queue display
        for url in self.queue:
            label = QLabel(url)
            label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.layout.addWidget(label)

class DownloadDisplayWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.go_button = QPushButton("Go")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        layout.addWidget(self.go_button)
        layout.addWidget(self.progress_bar)

class DLApp(QMainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.initialize_window()
        self.initialize_system_tray()
        self.initialize_main_layout()
        

    def initialize_window(self) -> None:
        """
        Set the title & initial size of the window
        """
        self.setWindowTitle("Youtube Downloader")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(800, 600)

    def initialize_system_tray(self) -> None:
        # Create a QSystemTrayIcon object
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon("icon.png"))  # Path to your icon
        self.trayIcon.setToolTip("Youtube Downloader")

        self.trayIcon.activated.connect(self.on_tray_icon_activated)


        # Create a menu for the tray icon
        trayMenu = QMenu()

        # Add a 'Show' action to the menu
        showAction = QAction("Show", self)
        showAction.triggered.connect(self.restore_from_icon)
        trayMenu.addAction(showAction)

        # Add a 'Quit' action to the menu
        quitAction = QAction("Quit", self)
        quitAction.triggered.connect(self.app.quit)
        trayMenu.addAction(quitAction)

        # Add the menu to the tray
        self.trayIcon.setContextMenu(trayMenu)

        # Show the tray icon
        self.trayIcon.hide()

    def initialize_main_layout(self) -> None:
        # Main layout
        main_layout = QVBoxLayout()

        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(18)

        # Mode selection widget
        self.mode_header = QLabel("Mode")
        self.mode_selection = ModeSelectionWidget()

        # Queue display widget
        self.queue_header = QLabel("Queue")
        self.queue_display = QueueDisplayWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.queue_display)

        # URL entry widget
        self.url_header = QLabel("URL")
        self.url_entry_widget = UrlEntryWidget(self.queue_display.add_to_queue)

        # Go button & progress bar
        self.download_controls = DownloadDisplayWidget()
        
        # Set fonts
        for each_header in [self.mode_header, self.queue_header, self.url_header]:
            each_header.setFont(header_font)

        # Place widgets
        main_layout.addWidget(self.mode_header)
        main_layout.addWidget(self.mode_selection)
        main_layout.addWidget(self.url_header)
        main_layout.addWidget(self.url_entry_widget)
        main_layout.addWidget(self.queue_header)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.download_controls)

        # Set main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.Trigger:  # Trigger is the reason for a left-click
            self.restore_from_icon()
    
    def restore_from_icon(self) -> None:
        """
        Restores the window from the tray icon, bringing it to the forefront,
        and hiding the tray icon.
        """
        self.showNormal()  # Restore the window if it's minimized
        self.activateWindow()
        self.raise_()
        self.trayIcon.hide()

    def changeEvent(self, event):
        """
        Override minimize events
        """
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                # Custom behavior when the window is minimized
                self.onMinimize()

        # Call the base class implementation to ensure default behavior for other events
        super().changeEvent(event)

    def onMinimize(self) -> None:
        """
        Minimize to tray icon
        """
        self.hide()
        self.trayIcon.show()

def start():
    app = QApplication(sys.argv)

    # Set the default font and size for the entire application
    default_font = QFont()
    default_font.setPointSize(16)  # Set this to your desired default size
    app.setFont(default_font)

    window = DLApp(app)
    window.show()
    sys.exit(app.exec_())
