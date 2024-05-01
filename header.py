import os
import struct

def cut_wav_header(input_path):
    try:
        with open(input_path, 'rb') as file:
            return file.read(44)
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file '{input_path}': {e}")
        return None

def load_corrupted_wav(input_path):
    try:
        with open(input_path, 'rb') as file:
            file.seek(44)  # Skip the first 44 bytes as they are the header
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
        return None
    except Exception as e:
        print(f"Error loading corrupted WAV file '{input_path}': {e}")
        return None

def merge_wav_files(reference_header, corrupted_header, corrupted_data):
    return corrupted_header + corrupted_data[44:]

def save_repaired_wav(input_path, repaired_data, riff_chunk_size, data_chunk_size, output_folder):
    try:
        os.makedirs(output_folder, exist_ok=True)
        print(f"Attempting to save in directory: {os.path.abspath(output_folder)}")

        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_full_path = os.path.join(output_folder, f"{input_filename}.wav")

        header = bytearray(repaired_data[:44])
        header[4:8] = struct.pack('<I', riff_chunk_size)
        header[40:44] = struct.pack('<I', data_chunk_size)

        with open(output_full_path, 'wb') as file:
            file.write(header)
            file.write(repaired_data[44:])
        print(f"File saved to {output_full_path}")
    except Exception as e:
        print(f"Error saving repaired WAV file: {e}")

def main():
    print("Welcome to the WAV file repair tool!")

    reference_wav_path = input("Enter the path to the reference WAV file: ").strip()

    reference_header = cut_wav_header(reference_wav_path)
    if reference_header is None:
        return

    corrupted_wav_folder = input("Enter the path to the folder containing corrupted WAV files: ").strip()

    output_folder = os.path.join(corrupted_wav_folder, "Repaired")

    for file in os.listdir(corrupted_wav_folder):
        file_path = os.path.join(corrupted_wav_folder, file)
        if os.path.isfile(file_path) and file.endswith('.wav'):
            print(f"Processing file: {file}")
            corrupted_header = cut_wav_header(file_path)
            if corrupted_header is None:
                continue

            corrupted_data = load_corrupted_wav(file_path)
            if corrupted_data is None:
                continue

            file_size = len(corrupted_data) + 44
            riff_chunk_size = file_size - 8
            data_chunk_size = file_size - 44

            repaired_wav_data = merge_wav_files(reference_header, corrupted_header, corrupted_data)

            save_repaired_wav(file_path, repaired_wav_data, riff_chunk_size, data_chunk_size, output_folder)

    print("Repair process complete.")

if __name__ == "__main__":
    main()
