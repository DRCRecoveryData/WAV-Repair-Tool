import os
import struct
from math import ceil

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

def main():
    print(f"Current working directory: {os.getcwd()}")

    reference_wav_path = input("Enter the path to the reference WAV file: ")

    reference_header = cut_wav_header(reference_wav_path)
    bits_per_sample = struct.unpack('<H', reference_header[34:36])[0]
    num_channels = struct.unpack('<H', reference_header[22:24])[0]
    position = calculate_first_complete_frame_position(bits_per_sample, num_channels)
    print(f"Position of the first complete frame: {position}")

    encrypted_wav_folder = input("Enter the path to the folder containing encrypted WAV files: ")

    corrupted_files_folder = os.path.dirname(encrypted_wav_folder)
    output_folder = os.path.join(corrupted_files_folder, "Repaired")

    for file in os.listdir(encrypted_wav_folder):
        print(f"Checking file: {file}")
        if is_double_extension_wav(file):
            encrypted_wav_path = os.path.join(encrypted_wav_folder, file)

            offset = position
            encrypted_data = load_encrypted_wav(encrypted_wav_path, offset)

            file_size = len(encrypted_data) + 44
            riff_chunk_size = file_size - 8
            data_chunk_size = file_size - 44

            repaired_wav_data = merge_wav_files(reference_header, encrypted_data)

            save_repaired_wav(encrypted_wav_path, repaired_wav_data, riff_chunk_size, data_chunk_size, output_folder)

if __name__ == "__main__":
    main()
