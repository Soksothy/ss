# UI definitions for YouTube Shorts Harvester
from PyQt5 import QtWidgets, QtCore


class MainWindow(QtWidgets.QMainWindow):
    start_clicked = QtCore.pyqtSignal(str, str, int, str)
    cancel_clicked = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Shorts Harvester")
        self.resize(600, 400)
        self._setup_ui()

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        form_layout = QtWidgets.QFormLayout()
        self.api_key_edit = QtWidgets.QLineEdit()
        self.api_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter API Key")
        form_layout.addRow("API Key", self.api_key_edit)

        self.channel_edit = QtWidgets.QLineEdit()
        self.channel_edit.setPlaceholderText("https://www.youtube.com/@handle/shorts")
        form_layout.addRow("Channel URL", self.channel_edit)

        self.max_spin = QtWidgets.QSpinBox()
        self.max_spin.setRange(1, 5000)
        self.max_spin.setValue(50)
        form_layout.addRow("Max Shorts", self.max_spin)

        folder_layout = QtWidgets.QHBoxLayout()
        self.folder_edit = QtWidgets.QLineEdit()
        self.folder_btn = QtWidgets.QPushButton("Browse")
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.folder_btn)
        form_layout.addRow("Save Folder", folder_layout)

        layout.addLayout(form_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("▶ Start Harvesting")
        self.start_btn.setEnabled(False)
        self.cancel_btn = QtWidgets.QPushButton("■ Cancel")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.log_edit = QtWidgets.QTextEdit()
        self.log_edit.setReadOnly(True)
        layout.addWidget(self.log_edit)

        self.setCentralWidget(central)

        # connections
        self.api_key_edit.textChanged.connect(self._check_ready)
        self.channel_edit.textChanged.connect(self._check_ready)
        self.folder_edit.textChanged.connect(self._check_ready)
        self.start_btn.clicked.connect(self._on_start)
        self.cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit())
        self.folder_btn.clicked.connect(self._select_folder)

        self._apply_dark_theme()

    def _select_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_edit.setText(folder)

    def _on_start(self):
        self.start_clicked.emit(
            self.api_key_edit.text().strip(),
            self.channel_edit.text().strip(),
            int(self.max_spin.value()),
            self.folder_edit.text().strip(),
        )

    def _check_ready(self):
        ok = bool(self.api_key_edit.text().strip() and self.channel_edit.text().strip() and self.folder_edit.text().strip())
        self.start_btn.setEnabled(ok)

    def log(self, text: str):
        self.log_edit.append(text)

    def _apply_dark_theme(self):
        palette = self.palette()
        palette.setColor(palette.Window, QtCore.Qt.black)
        palette.setColor(palette.WindowText, QtCore.Qt.white)
        palette.setColor(palette.Base, QtCore.Qt.black)
        palette.setColor(palette.AlternateBase, QtCore.Qt.black)
        palette.setColor(palette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(palette.ToolTipText, QtCore.Qt.white)
        palette.setColor(palette.Text, QtCore.Qt.white)
        palette.setColor(palette.Button, QtCore.Qt.darkGray)
        palette.setColor(palette.ButtonText, QtCore.Qt.white)
        palette.setColor(palette.Highlight, QtCore.Qt.darkBlue)
        palette.setColor(palette.HighlightedText, QtCore.Qt.white)
        self.setPalette(palette)
