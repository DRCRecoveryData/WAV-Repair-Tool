import sys
import os
import glob
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar, QTextEdit, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal

class FileRepairWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    repair_finished = pyqtSignal(str)

    def __init__(self, reference_file_path, corrupted_folder_path):
        super().__init__()
        self.reference_file_path = reference_file_path
        self.corrupted_folder_path = corrupted_folder_path

    def run(self):
        reference_header = self.cut_wav_header(self.reference_file_path)
        if reference_header is None:
            self.log_updated.emit("Error: Reference file header could not be read.")
            return

        repaired_folder_path = os.path.join(self.corrupted_folder_path, "Repaired")
        os.makedirs(repaired_folder_path, exist_ok=True)

        corrupted_files = glob.glob(os.path.join(self.corrupted_folder_path, '*.wav'))

        total_files = len(corrupted_files)

        for i, corrupted_file in enumerate(corrupted_files):
            file_name = os.path.basename(corrupted_file)
            progress_value = (i + 1) * 100 // total_files
            self.progress_updated.emit(progress_value)
            self.log_updated.emit(f"Processing {file_name}...")

            corrupted_header = self.cut_wav_header(corrupted_file)
            if corrupted_header is None:
                continue

            corrupted_data = self.load_corrupted_wav(corrupted_file)
            if corrupted_data is None:
                continue

            repaired_data = reference_header + corrupted_data[44:]

            riff_chunk_size = len(repaired_data) - 8
            data_chunk_size = len(repaired_data) - 44

            self.save_repaired_wav(corrupted_file, repaired_data, riff_chunk_size, data_chunk_size, repaired_folder_path)

        self.repair_finished.emit("Repair process complete.")

    def cut_wav_header(self, input_path):
        try:
            with open(input_path, 'rb') as file:
                return file.read(44)
        except FileNotFoundError:
            self.log_updated.emit(f"Error: File '{input_path}' not found.")
            return None
        except Exception as e:
            self.log_updated.emit(f"Error reading file '{input_path}': {e}")
            return None

    def load_corrupted_wav(self, input_path):
        try:
            with open(input_path, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            self.log_updated.emit(f"Error: File '{input_path}' not found.")
            return None
        except Exception as e:
            self.log_updated.emit(f"Error loading corrupted WAV file '{input_path}': {e}")
            return None

    def save_repaired_wav(self, input_path, repaired_data, riff_chunk_size, data_chunk_size, output_folder):
        try:
            input_filename = os.path.splitext(os.path.basename(input_path))[0]
            output_full_path = os.path.join(output_folder, f"{input_filename}.wav")

            header = bytearray(repaired_data[:44])
            header[4:8] = riff_chunk_size.to_bytes(4, byteorder='little')
            header[40:44] = data_chunk_size.to_bytes(4, byteorder='little')

            with open(output_full_path, 'wb') as file:
                file.write(header)
                file.write(repaired_data[44:])
            self.log_updated.emit(f"File saved to {output_full_path}")
        except Exception as e:
            self.log_updated.emit(f"Error saving repaired WAV file: {e}")

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

        self.corrupted_label = QLabel("corrupted Folder:")
        self.corrupted_path_edit = QLineEdit()
        self.corrupted_browse_button = QPushButton("Browse", self)
        self.corrupted_browse_button.setObjectName("browseButton")
        self.corrupted_browse_button.clicked.connect(self.browse_corrupted_folder)

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
        layout.addWidget(self.corrupted_label)
        layout.addWidget(self.corrupted_path_edit)
        layout.addWidget(self.corrupted_browse_button)
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

    def browse_corrupted_folder(self):
        corrupted_folder = QFileDialog.getExistingDirectory(self, "Select Corrupted Folder")
        if corrupted_folder:
            self.corrupted_path_edit.setText(corrupted_folder)

    def repair_files(self):
        reference_file_path = self.reference_path_edit.text()
        corrupted_folder_path = self.corrupted_path_edit.text()

        if not os.path.exists(reference_file_path):
            self.show_message("Error", "Reference file does not exist.")
            return
        if not os.path.exists(corrupted_folder_path):
            self.show_message("Error", "Corrupted folder does not exist.")
            return

        self.worker = FileRepairWorker(reference_file_path, corrupted_folder_path)
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
