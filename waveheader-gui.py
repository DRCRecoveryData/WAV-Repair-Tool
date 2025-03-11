import sys
import os
import glob
import struct
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
        self.log_updated.emit("🔧 Bắt đầu sửa chữa file...")
        
        # Create output folder
        repaired_folder_path = os.path.join(self.corrupted_folder_path, "Repaired")
        os.makedirs(repaired_folder_path, exist_ok=True)
        self.log_updated.emit(f"💾 Thư mục lưu file sửa: {repaired_folder_path}")

        # Get all WAV files in the corrupted folder
        corrupted_files = glob.glob(os.path.join(self.corrupted_folder_path, '*.wav'))
        total_files = len(corrupted_files)
        
        if total_files == 0:
            self.log_updated.emit("⚠️ Không tìm thấy file WAV nào trong thư mục!")
            self.repair_finished.emit("Không có file để sửa.")
            return

        for i, corrupted_file in enumerate(corrupted_files):
            file_name = os.path.basename(corrupted_file)
            output_path = os.path.join(repaired_folder_path, file_name)
            
            progress_value = (i + 1) * 100 // total_files
            self.progress_updated.emit(progress_value)
            
            self.log_updated.emit(f"🔧 Đang sửa file: {file_name}")
            success = self.repair_wav(self.reference_file_path, corrupted_file, output_path)
        
        self.log_updated.emit("✅ Hoàn tất sửa chữa!")
        self.repair_finished.emit(f"Đã sửa xong tất cả file. Các file đã được lưu trong thư mục {repaired_folder_path}")

    def get_wav_info(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                file_size = os.path.getsize(file_path)
                header = f.read(44)
                if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                    return None
                
                fmt_chunk = header[20:36]
                audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', fmt_chunk)
                
                return {
                    'File Size': f"{file_size} bytes",
                    'Audio Format': "PCM" if audio_format == 1 else f"Nén ({audio_format})",
                    'Sample Rate': f"{sample_rate} Hz",
                    'Channels': num_channels,
                    'Bit Depth': f"{bits_per_sample}-bit"
                }
        except Exception as e:
            self.log_updated.emit(f"Lỗi khi đọc file {file_path}: {str(e)}")
            return None

    def repair_wav(self, reference_path, corrupt_path, output_path):
        try:
            with open(reference_path, 'rb') as ref_file:
                ref_data = ref_file.read()
            with open(corrupt_path, 'rb') as corrupt_file:
                corrupt_data = corrupt_file.read()
            
            ref_fmt_offset = ref_data.find(b'fmt ')
            ref_data_offset = ref_data.find(b'data')
            
            if ref_fmt_offset == -1 or ref_data_offset == -1:
                raise ValueError("File tham chiếu không hợp lệ.")
            
            corrupt_fmt_offset = corrupt_data.find(b'fmt ')
            corrupt_data_offset = corrupt_data.find(b'data')
            
            fmt_offset = corrupt_fmt_offset if corrupt_fmt_offset != -1 else ref_fmt_offset
            fmt_chunk = corrupt_data[fmt_offset:fmt_offset+24] if corrupt_fmt_offset != -1 else ref_data[ref_fmt_offset:ref_fmt_offset+24]
            
            if corrupt_data_offset == -1:
                cleaned_data = ref_data[ref_data_offset + 8:]
            else:
                cleaned_data = corrupt_data[corrupt_data_offset + 8:]
            
            new_data_size = len(cleaned_data)
            new_data_chunk = b'data' + struct.pack('<I', new_data_size)
            
            final_wav = ref_data[:fmt_offset] + fmt_chunk + ref_data[fmt_offset+24:ref_data_offset] + new_data_chunk + cleaned_data
            
            # Update RIFF chunk size
            riff_chunk_size = len(final_wav) - 8
            final_wav = final_wav[:4] + struct.pack('<I', riff_chunk_size) + final_wav[8:]
            
            with open(output_path, 'wb') as out_file:
                out_file.write(final_wav)
            
            self.log_updated.emit(f"✅ Sửa thành công: {os.path.basename(output_path)}")
            return True
        except Exception as e:
            self.log_updated.emit(f"❌ Lỗi khi sửa {os.path.basename(corrupt_path)}: {str(e)}")
            return False

class FileRepairApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WAV Header Tool")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.reference_label = QLabel("Reference File:")
        self.reference_path_edit = QLineEdit()
        self.reference_browse_button = QPushButton("Browse", self)
        self.reference_browse_button.setObjectName("browseButton")
        self.reference_browse_button.clicked.connect(self.browse_reference_file)

        self.corrupted_label = QLabel("Corrupted Folder:")
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
        reference_file, _ = QFileDialog.getOpenFileName(self, "Select Reference File", "", "WAV Files (*.wav)")
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
