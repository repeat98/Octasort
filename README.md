# OctaSort

**OctaSort** is a Python script designed to organize and manage your audio library efficiently. It automatically analyzes audio files to determine their musical key and tonality, normalizes their volume, and renames them systematically based on their key and other metadata. Additionally, OctaSort maintains a JSON-based database to track processed files, ensuring consistent and reliable organization over time.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [File Renaming Structure](#file-renaming-structure)
- [Logging](#logging)
- [Database](#database)
- [Supported Audio Formats](#supported-audio-formats)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Musical Key Detection:** Utilizes the Essentia library to extract the key and scale (major/minor) of each audio file.
- **Tonality Assessment:** Determines the tonality of audio files using spectral flatness to differentiate between tonal and non-tonal samples.
- **Automated Renaming:** Renames audio files based on their detected key, ensuring a consistent naming convention.
- **Volume Normalization:** Normalizes audio files to a target loudness (-3.0 dBFS) to maintain consistent playback levels.
- **Database Management:** Maintains a JSON database (`octasort_db.json`) to track processed files, their metadata, and changes over time.
- **Logging:** Provides detailed logs (`octasort.log`) of all operations, including processing steps, errors, and actions taken.
- **Conflict Resolution:** Detects and handles filename conflicts to prevent data loss or overwriting.
- **Support for Multiple Audio Formats:** Compatible with various audio file types, including WAV, MP3, AIFF, FLAC, and OGG.

## Prerequisites

Before installing OctaSort, ensure that your system meets the following requirements:

- **Operating System:** Compatible with Windows, macOS, and Linux.
- **Python:** Version **3.11**.
- **Python Packages:** Ensure that `numpy` version **1.26** is installed.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/octasort.git
   cd octasort
   ```

2. **Create a Virtual Environment (Optional but Recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Python Packages:**

   OctaSort relies on several Python libraries. Install them using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

   **`requirements.txt`** should include:

   ```plaintext
   numpy==1.26
   pydub
   essentia
   ```

4. **Install FFmpeg:**

   OctaSort uses FFmpeg for audio processing. Download and install FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).

   - **Windows:** Add FFmpeg to your system's PATH.
   - **macOS:** You can install via Homebrew:

     ```bash
     brew install ffmpeg
     ```

   - **Linux:** Install via your distribution's package manager, e.g., for Debian/Ubuntu:

     ```bash
     sudo apt-get install ffmpeg
     ```

## Usage

Run OctaSort by specifying the root directory containing your audio files organized into descriptor folders.

```bash
python3 octasort.py /path/to/root_directory
```

### Example

Suppose you have a directory structure like:

```
/SampleLibrary
├── Descriptor1
│   ├── sample1.mp3
│   ├── sample2.wav
│   └── ...
├── Descriptor2
│   ├── sample3.flac
│   ├── sample4.ogg
│   └── ...
└── ...
```

Run OctaSort as follows:

```bash
python3 octasort.py /MusicLibrary
```

OctaSort will process each descriptor folder (`Descriptor1`, `Descriptor2`, etc.), analyze the audio files, normalize them, and rename them based on their detected key and other metadata.

## Configuration

### Key Groups

OctaSort organizes keys based on predefined groups aligned with the Circle of Fifths. The script defines these groups in a specific order to facilitate consistent sorting and renaming.

```python
KEY_GROUPS = [
    ['Cmaj', 'Amin'],
    ['Gmaj', 'Emin'],
    ['Dmaj', 'Bmin'],
    ['Amaj', 'F#min'],
    ['Emaj', 'C#min'],
    ['Bmaj', 'G#min'],
    ['F#maj', 'D#min'],
    ['Dbmaj', 'Bbmin'],
    ['Abmaj', 'Fmin'],
    ['Ebmaj', 'Cmin'],
    ['Bbmaj', 'Gmin'],
    ['Fmaj', 'Dmin']
]
```

You can modify these groups or add new ones as needed to fit your organizational preferences.

### Tonality Threshold

The tonality threshold determines whether an audio file is considered tonal or non-tonal based on its spectral flatness.

```python
tonality_threshold = 0.1  # Adjust as needed
```

A lower threshold makes the script more stringent in classifying files as tonal.

## File Renaming Structure

OctaSort employs a systematic file renaming convention to ensure consistency and ease of navigation within your audio library. The renaming structure follows this pattern:

```
{Descriptor}{Index}_{Key}_{OriginalName}{Extension}
```

### Components:

- **Descriptor:** The name of the folder containing the audio file. This helps in categorizing files based on their descriptors.
  
- **Index:** A numerical value assigned based on the sorted order of the files within the descriptor folder. This ensures that files are organized sequentially.

- **Key:** The detected musical key and scale of the audio file (e.g., `Cmaj` for C major or `Amin` for A minor). If the file is non-tonal, this part is omitted.

- **OriginalName:** The original name of the audio file before processing. This maintains the identity of the file.

- **Extension:** The original file extension (e.g., `.mp3`, `.wav`).

### Example:

Given a descriptor folder named `Descriptor1` containing a file `song1.mp3` detected to be in C major, the renamed file would be:

```
Descriptor11_Cmaj_song1.mp3
```

If another file `song2.wav` is detected to be non-tonal, it would be renamed as:

```
Descriptor12_song2.wav
```

### Handling Conflicts:

If a target filename already exists, OctaSort logs the conflict and skips renaming the problematic file to prevent data loss or overwriting. Ensure that your descriptor names and indices are unique to minimize conflicts.

## Logging

OctaSort generates a log file named `octasort.log` in the script's directory. This log records all operations, including:

- Start and completion of processing.
- Files being processed, skipped, or renamed.
- Errors encountered during processing.
- Database load and save operations.

**Example Log Entry:**

```
2024-04-27 10:15:30,123 - INFO - Loaded database from /path/to/octasort_db.json.
2024-04-27 10:15:30,124 - INFO - Starting octasort with root directory: /MusicLibrary
2024-04-27 10:15:31,456 - INFO - 
Processing folder: Descriptor1
2024-04-27 10:15:32,789 - INFO - Spectral Flatness for '/MusicLibrary/Descriptor1/song1.mp3': 0.05
2024-04-27 10:15:32,790 - INFO - Detected tonal sample. Extracted Key: Cmaj with strength 0.8
2024-04-27 10:15:33,012 - INFO - Processed and renamed to: Descriptor11_Cmaj_song1.mp3
...
2024-04-27 10:20:45,678 - INFO - Database saved successfully to /path/to/octasort_db.json.
2024-04-27 10:20:45,679 - INFO - 
Processing complete.
```

## Database

OctaSort maintains a JSON database file named `octasort_db.json` in the script's directory. This database tracks information about each processed file, including:

- **Original Name:** The original filename before processing.
- **New Filename:** The new, standardized filename after processing.
- **Last Modified:** Timestamp of the last modification to the file.
- **Descriptor:** The descriptor folder the file belongs to.
- **Index:** The assigned index based on sorting.
- **Key:** Detected musical key and scale.

**Sample Database Entry:**

```json
{
    "Descriptor1": {
        "Descriptor11_Cmaj_song1.mp3": {
            "original_name": "song1.mp3",
            "new_filename": "Descriptor11_Cmaj_song1.mp3",
            "last_modified": 1619472000.0,
            "descriptor": "Descriptor1",
            "index": 1,
            "key": "cmaj"
        },
        ...
    },
    ...
}
```

This database allows OctaSort to detect changes in your audio library, such as added or deleted files, and act accordingly in subsequent runs.

## Supported Audio Formats

OctaSort supports the following audio file formats:

- **WAV (`.wav`)**
- **MP3 (`.mp3`)**
- **AIFF (`.aif`, `.aiff`)**
- **FLAC (`.flac`)**
- **OGG (`.ogg`)**

Ensure that your audio files have the correct extensions to be recognized and processed by OctaSort.

## Error Handling

OctaSort includes comprehensive error handling to manage potential issues during processing:

- **Database Errors:** Issues with loading or saving the JSON database are logged.
- **Audio Processing Errors:** Failures in loading or analyzing audio files are logged with details.
- **Filename Conflicts:** If a target filename already exists, the conflict is logged, and the file is skipped to prevent overwriting.
- **File System Errors:** Problems with file access, such as permission issues or missing files, are logged.

Review the `octasort.log` file to identify and resolve any errors encountered during processing.

## Contributing

Contributions are welcome! If you encounter issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add your feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

## License

This project is licensed under the [MIT License](LICENSE).

---

*Happy Sorting! 🎵*