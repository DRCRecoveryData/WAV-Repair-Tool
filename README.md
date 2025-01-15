# WAV Repair Tool

[![Stop/DJVU Ransomware](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/2651b85a-e97e-4322-b9ff-f462ed51269e)](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/2651b85a-e97e-4322-b9ff-f462ed51269e)
[![Header Corrupted](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/c03ba6af-539a-46da-8ef0-cb01d18e9c88)](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/c03ba6af-539a-46da-8ef0-cb01d18e9c88)

![Build Status](https://img.shields.io/github/actions/workflow/status/DRCRecoveryData/WAV-Repair-Tool/build.yml)
![License](https://img.shields.io/github/license/DRCRecoveryData/WAV-Repair-Tool)
![Version](https://img.shields.io/github/v/release/DRCRecoveryData/WAV-Repair-Tool)

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)
- [Contact](#contact)

## Overview

The WAV Repair Tool is a program developed by DRC Recovery that repairs WAV audio files corrupted by the Stop/DJVU Ransomware. This ransomware encrypts various file types, including audio files, causing them to be unusable. The WAV Repair Tool leverages advanced algorithms to restore these files to their original state.

## Installation

To install the WAV Repair Tool:

1. Download the latest release from the [releases page](https://github.com/DRCRecoveryData/WAV-Repair-Tool/releases).
2. Extract the contents to a directory.
3. Ensure you have Python installed. You can download it from [python.org](https://www.python.org/).
4. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

To use the tool:

1. Run `main.py` or `waverepair-gui.py` & `waveheader-gui.py`.
2. Enter the reference wave file path and the directory with corrupted wave files.
3. Wait for repair completion, indicated by the progress bar.
4. Repaired files are saved to a directory named "Repaired".

**Note:** The tool repairs files but doesn't decrypt or remove the ransomware. Victims should take steps for malware removal and data recovery.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

For issues or suggestions, please open an issue on GitHub.

## License

Licensed under the GNU General Public License (GPL). See [LICENSE](LICENSE) for details.

## References

- [Stop/DJVU Ransomware Description on Bleeping Computer](https://www.bleepingcomputer.com/news/security/djvu-ransomware-updated-to-v91-uses-new-encryption-mode/)
- [Python Programming Language](https://www.python.org/)
- [PyQt6 Library](https://pypi.org/project/PyQt6/)

## Contact

For support or questions, please contact us at [hanaloginstruments@gmail.com](mailto:hanaloginstruments@gmail.com)
