import sys
import os
import glob
import struct
from math import ceil  # Add this import
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class FileRepairWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    repair_finished = pyqtSignal(str)

    def __init__(self, reference_file_path, encrypted_folder_path):
        super().__init__()
        self.reference_file_path = reference_file_path
        self.encrypted_folder_path = encrypted_folder_path

    def run(self):
        repaired_folder_path = os.path.join(self.encrypted_folder_path, "Repaired")
        os.makedirs(repaired_folder_path, exist_ok=True)

        encrypted_files = glob.glob(os.path.join(self.encrypted_folder_path, '*.wav'))

        total_files = len(encrypted_files)

        for i, encrypted_file in enumerate(encrypted_files):
            file_name = os.path.basename(encrypted_file)
            progress_value = (i + 1) * 100 // total_files
            self.progress_updated.emit(progress_value)
            self.log_updated.emit(f"Processing {file_name}...")
            repaired_file_path = os.path.join(repaired_folder_path, file_name)

            self.repair_wav_file(encrypted_file, repaired_file_path)

        self.repair_finished.emit("Repaired files saved to the 'Repaired' folder.")

    def repair_wav_file(self, encrypted_file, output_file):
        with open(encrypted_file, 'rb') as f:
            data = f.read()

        # Repair process
        reference_header = self.load_reference_header(self.reference_file_path)
        bits_per_sample, num_channels = self.extract_audio_parameters(reference_header)
        position = self.calculate_first_complete_frame_position(bits_per_sample, num_channels)

        with open(self.reference_file_path, 'rb') as ref_file:
            ref_header = ref_file.read(position)

        with open(encrypted_file, 'rb') as enc_file:
            enc_data = enc_file.read()[position:]

        repaired_data = self.merge_wav_files(ref_header, enc_data)

        with open(output_file, 'wb') as repaired_file:
            repaired_file.write(repaired_data)

    def load_reference_header(self, reference_file_path):
        with open(reference_file_path, 'rb') as ref_file:
            reference_header = ref_file.read(44)
        return reference_header

    def extract_audio_parameters(self, header):
        bits_per_sample = struct.unpack('<H', header[34:36])[0]
        num_channels = struct.unpack('<H', header[22:24])[0]
        return bits_per_sample, num_channels

    def calculate_first_complete_frame_position(self, bits_per_sample, num_channels):
        frame_size = (bits_per_sample // 8) * num_channels
        first_complete_frame_number = ceil((153605 - 44) / frame_size)
        return 44 + (first_complete_frame_number * frame_size)

    def merge_wav_files(self, reference_header, encrypted_data):
        return reference_header + encrypted_data

class FileRepairApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WAV Repair Tool")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.reference_label = QLabel("Reference File:")
        self.reference_path_edit = QLineEdit()
        self.reference_browse_button = QPushButton("Browse", self)
        self.reference_browse_button.setObjectName("browseButton")
        self.reference_browse_button.clicked.connect(self.browse_reference_file)

        self.encrypted_label = QLabel("Encrypted Folder:")
        self.encrypted_path_edit = QLineEdit()
        self.encrypted_browse_button = QPushButton("Browse", self)
        self.encrypted_browse_button.setObjectName("browseButton")
        self.encrypted_browse_button.clicked.connect(self.browse_encrypted_folder)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.repair_button = QPushButton("Repair", self)
        self.repair_button.setObjectName("blueButton")
        self.repair_button.clicked.connect(self.repair_files)

        layout.addWidget(self.reference_label)
        layout.addWidget(self.reference_path_edit)
        layout.addWidget(self.reference_browse_button)
        layout.addWidget(self.encrypted_label)
        layout.addWidget(self.encrypted_path_edit)
        layout.addWidget(self.encrypted_browse_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_box)
        layout.addWidget(self.repair_button)

        self.setLayout(layout)

        self.setStyleSheet("""
        #browseButton, #blueButton {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 4px;
        }
        #browseButton:hover, #blueButton:hover {
            background-color: #2980b9;
        }
        """)

    def browse_reference_file(self):
        reference_file, _ = QFileDialog.getOpenFileName(self, "Select Reference File", "", "All Files (*)")
        if reference_file:
            self.reference_path_edit.setText(reference_file)

    def browse_encrypted_folder(self):
        encrypted_folder = QFileDialog.getExistingDirectory(self, "Select Encrypted Folder")
        if encrypted_folder:
            self.encrypted_path_edit.setText(encrypted_folder)

    def repair_files(self):
        reference_file_path = self.reference_path_edit.text()
        encrypted_folder_path = self.encrypted_path_edit.text()

        if not os.path.exists(reference_file_path):
            self.show_message("Error", "Reference file does not exist.")
            return
        if not os.path.exists(encrypted_folder_path):
            self.show_message("Error", "Encrypted folder does not exist.")
            return

        self.worker = FileRepairWorker(reference_file_path, encrypted_folder_path)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.update_log)
        self.worker.repair_finished.connect(self.repair_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_box.append(message)

    def repair_finished(self, message):
        self.show_message("Success", message)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileRepairApp()
    window.show()
    sys.exit(app.exec())
