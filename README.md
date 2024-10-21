# OctaSort

OctaSort is a Python script designed to organize, process, and normalize audio files in a structured directory. It renames audio files according to a specific pattern, extracts musical keys for certain types of audio files, normalizes audio levels, and maintains a database to track processed files.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [File Naming Convention](#file-naming-convention)
- [Logging and Database](#logging-and-database)
- [License](#license)

## Features

- **Automatic File Renaming**: Renames audio files based on their descriptor, index, and musical key (if applicable).
- **Key Extraction**: Extracts the musical key of audio files using Essentia for specific descriptors.
- **Audio Normalization**: Normalizes audio files to -3 dBFS using pydub.
- **Database Management**: Keeps track of processed files in a JSON database to prevent redundant processing.
- **Logging**: Logs processing steps and errors to both console and a log file.

## Prerequisites

- **Python 3.6 or higher**
- **ffmpeg**: Required by pydub for audio processing.
- **Essentia**: For musical key extraction.
- **pydub**: For audio normalization and processing.

## Installation

1. **Install ffmpeg**

   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) and add it to your PATH.
   - **macOS**: Install via Homebrew:
     ```bash
     brew install ffmpeg
     ```
   - **Linux**: Install via package manager:
     ```bash
     sudo apt-get install ffmpeg
     ```

2. **Install Python Packages**

   ```bash
   pip install pydub essentia
   ```

   **Note**: Essentia might require additional dependencies. Refer to the [Essentia installation guide](https://essentia.upf.edu/installing.html) for detailed instructions.

## Usage

```bash
python3 octasort.py /path/to/root_directory
```

- Replace `/path/to/root_directory` with the path to your root directory containing audio folders.

## Directory Structure

Your root directory should contain folders named according to the descriptors in the script. The default descriptor mapping is:

- `BASS`: `B`
- `CHORD`: `C`
- `CP`: `CP`
- `FX`: `FX`
- `HH`: `HH`
- `INTRO`: `I`
- `KICK`: `K`
- `SYN`: `SYN`
- `TOP`: `T`
- `TRIBE`: `TRB`
- `VOX`: `V`

**Example:**

```
/path/to/root_directory/
├── BASS/
├── CHORD/
├── CP/
├── FX/
├── HH/
├── INTRO/
├── KICK/
├── SYN/
├── TOP/
├── TRIBE/
└── VOX/
```

Place your audio files inside the corresponding descriptor folders.

## File Naming Convention

After processing, files will be renamed using the following pattern:

```
<DESCRIPTOR><INDEX>_<KEY>_<ORIGINAL_FILENAME><EXTENSION>
```

- `<DESCRIPTOR>`: Descriptor code (e.g., `B`, `C`, `HH`).
- `<INDEX>`: Numerical index based on sorting.
- `<KEY>`: Musical key (if extracted; descriptors `B`, `C`, `SYN`, `FX`, `INTRO` only).
- `<ORIGINAL_FILENAME>`: Original base filename.
- `<EXTENSION>`: Original file extension.

**Examples:**

- `B1_Cmaj_MyBassline.wav`
- `HH3_MyHiHatLoop.wav`
- `SYN2_Dmin_SynthChord.aiff`

## Logging and Database

- **Log File**: `octasort.log` is created in the script's directory. It contains detailed logs of the processing steps.
- **Database File**: `octasort_db.json` stores metadata of processed files to prevent redundant processing.

## How It Works

1. **Initialization**: The script loads or creates a JSON database and sets up logging.
2. **Folder Processing**: Iterates over each descriptor folder in the root directory.
3. **File Collection**: Collects all audio files with supported extensions.
4. **Key Extraction**: For specific descriptors, extracts the musical key using Essentia.
5. **Sorting**: Sorts files based on the Circle of Fifths and filename.
6. **Renaming and Normalization**:
   - Renames files according to the naming convention.
   - Normalizes audio levels to -3 dBFS.
   - Updates the database with the new file information.
7. **Database Update**: Saves the updated database to `octasort_db.json`.
8. **Logging**: Records all actions and any errors encountered.

## Supported Audio Formats

- WAV
- MP3
- AIFF
- FLAC
- OGG

## Error Handling

- **Unsupported Formats**: Skips files with unsupported formats.
- **File Conflicts**: Logs errors if a naming conflict occurs and skips the file.
- **Missing Dependencies**: Logs and exits if required dependencies are missing.

## License

This project is licensed under the MIT License.

---

**Disclaimer**: Use this script at your own risk. Always back up your files before processing.