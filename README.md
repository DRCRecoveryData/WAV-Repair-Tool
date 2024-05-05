![GitHub release (latest by date)](https://img.shields.io/github/v/release/DRCRecoveryData/WAV-Repair-Tool)
![GitHub Release Date](https://img.shields.io/github/release-date/DRCRecoveryData/WAV-Repair-Tool)
![GitHub repo size](https://img.shields.io/github/repo-size/DRCRecoveryData/WAV-Repair-Tool)
![GitHub all releases](https://img.shields.io/github/downloads/DRCRecoveryData/WAV-Repair-Tool)
![GitHub](https://img.shields.io/github/license/DRCRecoveryData/WAV-Repair-Tool)

# WAV Repair Tool

[![Stop/DJVU Ransomware](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/2651b85a-e97e-4322-b9ff-f462ed51269e)](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/2651b85a-e97e-4322-b9ff-f462ed51269e) [![Header Corrupted](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/c03ba6af-539a-46da-8ef0-cb01d18e9c88)](https://github.com/DRCRecoveryData/WAV-Repair-Tool/assets/85211068/c03ba6af-539a-46da-8ef0-cb01d18e9c88)

## Overview

The WAV Repair Tool is a program developed by DRC Recovery that repairs WAV audio files corrupted by the Stop/DJVU Ransomware. This ransomware encrypts various file types, including audio files, causing significant disruption and loss. This tool helps mitigate the damage by repairing the audio files, making them accessible once again.

## Usage
To use the tool:
1. Download the latest release from the releases page.
2. Extract the contents to a directory.
3. Run `main.py` or `waverepair-gui.py` & `waveheader-gui.py`.
4. Enter the reference wave file path and the directory with corrupted wave files.
5. Wait for repair completion, indicated by the progress bar.
6. Repaired files are saved to a directory named "Repaired".

**Note:** The tool repairs files but doesn't decrypt or remove the ransomware. Victims should take steps for malware removal and data recovery.

## Contributing
For issues or suggestions, open an issue or submit a pull request.

## License
Licensed under the GNU General Public License (GPL). See LICENSE for details.

## References
- [Stop/DJVU Ransomware Description on Bleeping Computer](https://www.bleepingcomputer.com/news/security/djvu-ransomware-updated-to-v91-uses-new-encryption-mode/)
- [Python Programming Language](https://www.python.org/)
- [PyQt6 Library](https://pypi.org/project/PyQt6/)
