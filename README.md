# WAV Audio File Repair Tool for Stop/DJVU Ransomware

![Image](https://github.com/DRCRecoveryData/WAV-Repair-Tool/blob/main/Images/Screenshot%20from%202024-04-30%2008-10-03.png)

## Overview
The WAV Audio File Repair Tool is a program developed by DRC Recovery that repairs WAV audio files corrupted by the Stop/DJVU Ransomware. This ransomware encrypts various file types, including audio files, causing significant disruption and loss. This tool helps mitigate the damage by repairing the audio files, making them accessible once again.

## Usage
To use the tool:
1. Download the latest release from the releases page.
2. Extract the contents to a directory.
3. Run `main.py` or `waverepairgui.py`.
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