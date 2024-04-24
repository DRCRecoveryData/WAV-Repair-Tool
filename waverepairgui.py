import os
import struct
from math import ceil
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QProgressBar
from PyQt6.QtCore import Qt, QThread, pyqtSignal

def cut_wav_header(input_path):
    with open(input_path, 'rb') as file:
        return file.read(44)

def load_encrypted_wav(input_path, offset):
    with open(input_path, 'rb') as file:
        encrypted_wav = file.read()
        return encrypted_wav[offset:-334]

def merge_wav_files(reference_header, encrypted_data):
    return reference_header + encrypted_data

def save_repaired_wav(input_path, repaired_data, riff_chunk_size, data_chunk_size, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    print(f"Attempting to save in directory: {os.path.abspath(output_folder)}")

    input_filename = os.path.splitext(os.path.splitext(os.path.basename(input_path))[0])[0]
    output_full_path = os.path.join(output_folder, f"{input_filename}.wav")

    header = bytearray(repaired_data[:44])
    header[4:8] = struct.pack('<I', riff_chunk_size)
    header[40:44] = struct.pack('<I', data_chunk_size)

    with open(output_full_path, 'wb') as file:
        file.write(header + repaired_data[44:])
    print(f"File saved to {output_full_path}")

def calculate_first_complete_frame_position(bits_per_sample, num_channels):
    frame_size = (bits_per_sample // 8) * num_channels
    first_complete_frame_number = ceil((153605 - 44) / frame_size)
    return 44 + (first_complete_frame_number * frame_size)

def is_double_extension_wav(file_name):
    name_without_ext, first_ext = os.path.splitext(file_name)
    _, second_ext = os.path.splitext(name_without_ext)
    
    return second_ext.lower() == '.wav'

class RepairThread(QThread):
    update_progress = pyqtSignal(int)
    update_verbose = pyqtSignal(str)

    def __init__(self, reference_path, corrupted_folder):
        super().__init__()
        self.reference_path = reference_path
        self.corrupted_folder = corrupted_folder

    def run(self):
        reference_header = cut_wav_header(self.reference_path)
        bits_per_sample = struct.unpack('<H', reference_header[34:36])[0]
        num_channels = struct.unpack('<H', reference_header[22:24])[0]
        position = calculate_first_complete_frame_position(bits_per_sample, num_channels)

        total_files = len([file for file in os.listdir(self.corrupted_folder) if is_double_extension_wav(file)])
        processed_files = 0

        for file in os.listdir(self.corrupted_folder):
            if is_double_extension_wav(file):
                encrypted_wav_path = os.path.join(self.corrupted_folder, file)
                offset = position
                encrypted_data = load_encrypted_wav(encrypted_wav_path, offset)

                file_size = len(encrypted_data) + 44
                riff_chunk_size = file_size - 8
                data_chunk_size = file_size - 44

                repaired_wav_data = merge_wav_files(reference_header, encrypted_data)

                output_folder = os.path.join(self.corrupted_folder, "Repaired")
                save_repaired_wav(encrypted_wav_path, repaired_wav_data, riff_chunk_size, data_chunk_size, output_folder)

                processed_files += 1
                progress = (processed_files / total_files) * 100
                self.update_progress.emit(progress)
                self.update_verbose.emit(f"Processed file: {file}")

                # Let's add a delay to simulate processing time
                self.msleep(100)

        # After processing all files, emit progress signal with 100% value
        self.update_progress.emit(100)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WAV Repair Tool")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.reference_label = QLabel("Reference WAV:")
        self.reference_path_edit = QLineEdit()
        self.reference_browse_button = QPushButton("Browse")

        self.corrupt_label = QLabel("Corrupted Folder:")
        self.corrupt_path_edit = QLineEdit()
        self.corrupt_browse_button = QPushButton("Browse")

        self.repair_button = QPushButton("Repair")
        self.repair_button.setStyleSheet("background-color: #007ACC; color: white;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)  # Show text on progress bar

        self.verbose_label = QLabel("Verbose:")
        self.verbose_text_edit = QTextEdit()

        layout.addWidget(self.reference_label)
        layout.addWidget(self.reference_path_edit)
        layout.addWidget(self.reference_browse_button)
        layout.addWidget(self.corrupt_label)
        layout.addWidget(self.corrupt_path_edit)
        layout.addWidget(self.corrupt_browse_button)
        layout.addWidget(self.repair_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.verbose_label)
        layout.addWidget(self.verbose_text_edit)

        self.reference_browse_button.clicked.connect(self.browse_reference)
        self.corrupt_browse_button.clicked.connect(self.browse_corrupt)
        self.repair_button.clicked.connect(self.start_repair)

    def browse_reference(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("WAV files (*.wav)")
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            self.reference_path_edit.setText(file_paths[0])

    def browse_corrupt(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        if folder_dialog.exec():
            folder_paths = folder_dialog.selectedFiles()
            self.corrupt_path_edit.setText(folder_paths[0])

    def start_repair(self):
        reference_path = self.reference_path_edit.text()
        corrupted_folder = self.corrupt_path_edit.text()

        if not os.path.exists(reference_path) or not os.path.exists(corrupted_folder):
            self.verbose_text_edit.append("Reference WAV file or corrupted folder path is invalid.")
            return

        self.progress_bar.setValue(0)  # Reset progress bar to 0
        self.repair_thread = RepairThread(reference_path, corrupted_folder)
        self.repair_thread.update_progress.connect(self.update_progress)
        self.repair_thread.update_verbose.connect(self.update_verbose)
        self.repair_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}%")  # Update the format with the current progress

    def update_verbose(self, message):
        self.verbose_text_edit.append(message)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    # Apply Fusion style for rounded corners
    app.setStyle("Fusion")

    # Apply the system color palette
    app.setPalette(app.style().standardPalette())

    # Apply styles to "Browse" buttons
    button_style = '''
        QPushButton {
            background-color: #007ACC;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }

        QPushButton:hover {
            background-color: #005F99;
        }
    '''
    app.setStyleSheet(button_style)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
