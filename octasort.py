import os
import re
import sys
import logging
import json
from datetime import datetime
from pydub import AudioSegment
import essentia
import essentia.standard as ess

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, 'octasort_db.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'octasort.log')

# Configure logging to both file and console
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clear existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Map folder names to descriptors
descriptor_mapping = {
    'BASS': 'B',
    'CHORD': 'C',
    'CP': 'CP',
    'FX': 'FX',
    'HH': 'HH',
    'INTRO': 'I',
    'KICK': 'K',
    'SYN': 'SYN',
    'TOP': 'T',
    'TRIBE': 'TRB',
    'VOX': 'V'
}

# Supported audio file extensions
audio_extensions = ('.wav', '.mp3', '.aif', '.aiff', '.flac', '.ogg')

# Mapping from file extensions to ffmpeg format identifiers
format_mapping = {
    'wav': 'wav',
    'mp3': 'mp3',
    'aif': 'aiff',
    'aiff': 'aiff',
    'flac': 'flac',
    'ogg': 'ogg'
}

# Circle of Fifths mapping
note_names_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_names_flat = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

pitch_class_to_notes = {
    0: ['C'],
    1: ['C#', 'Db'],
    2: ['D'],
    3: ['D#', 'Eb'],
    4: ['E'],
    5: ['F'],
    6: ['F#', 'Gb'],
    7: ['G'],
    8: ['G#', 'Ab'],
    9: ['A'],
    10: ['A#', 'Bb'],
    11: ['B', 'Cb'],
}

circle_order = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]  # Circle of Fifths order

circle_of_fifths_positions = {}
for position, pc in enumerate(circle_order):
    for note in pitch_class_to_notes[pc]:
        circle_of_fifths_positions[note] = position

def get_root_note_and_scale(key_scale_clean):
    match = re.match(r'^([A-G][#b]?)(.*)$', key_scale_clean)
    if match:
        root_note = match.group(1)
        scale = match.group(2)
        return root_note, scale
    else:
        return None, None

def get_circle_of_fifths_position(root_note):
    return circle_of_fifths_positions.get(root_note, 100)  # Default to a large number if not found

def load_db():
    """Load the JSON database."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                db = json.load(f)
            logging.info(f"Loaded database from {DB_FILE}.")
            return db
        except Exception as e:
            logging.error(f"Failed to load database file {DB_FILE}: {e}")
            return {}
    else:
        logging.info(f"No existing database found. Starting with an empty database.")
        return {}

def save_db(db):
    """Save the JSON database."""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(db, f, indent=4)
        logging.info(f"Database saved successfully to {DB_FILE}.")
    except Exception as e:
        logging.error(f"Failed to save database file {DB_FILE}: {e}")

def normalize_audio(audio):
    """Normalize audio to -3.0 dBFS."""
    target_dBFS = -3.0
    change_in_dBFS = target_dBFS - audio.max_dBFS
    return audio.apply_gain(change_in_dBFS)

def extract_key(audio_file_path):
    """Extract Key using Essentia."""
    try:
        # Load audio using Essentia
        loader = ess.MonoLoader(filename=audio_file_path)
        audio = loader()

        # Key extraction using KeyExtractor
        key_extractor = ess.KeyExtractor()
        key, scale, strength = key_extractor(audio)

        # Condense scale (e.g., 'minor' -> 'min', 'major' -> 'maj')
        scale_short = {'minor': 'min', 'major': 'maj'}.get(scale.lower(), scale)

        # Combine key and condensed scale (e.g., 'Amin', 'Cmaj')
        key_scale = f"{key}{scale_short}"

        return key_scale
    except Exception as e:
        logging.error(f"Essentia key extraction failed for {audio_file_path}: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 octasort.py /path/to/root_directory")
        sys.exit(1)

    # Root directory where the folders are located
    root_dir = sys.argv[1]

    if not os.path.isdir(root_dir):
        logging.error(f"The provided root directory '{root_dir}' does not exist or is not a directory.")
        sys.exit(1)

    logging.info(f"Starting octasort with root directory: {root_dir}")

    # Load existing database
    db = load_db()

    # Process each descriptor folder
    for folder_name, descriptor in descriptor_mapping.items():
        folder_path = os.path.join(root_dir, folder_name)
        if not os.path.isdir(folder_path):
            logging.warning(f"Folder '{folder_name}' does not exist in the root directory.")
            continue
        logging.info(f"\nProcessing folder: {folder_name}")

        # Decide whether to extract Key
        if descriptor in ['B', 'C', 'SYN', 'FX', 'I']:
            extract_key_flag = True
            files_with_keys = []
        else:
            extract_key_flag = False

        # Collect all current audio files in the folder
        current_files = []
        for filename in os.listdir(folder_path):
            if not filename.lower().endswith(audio_extensions):
                logging.info(f"  Skipping non-audio file: {filename}")
                continue  # Skip non-audio files
            current_files.append(filename)

        # Initialize folder in db if not present
        if folder_name not in db:
            db[folder_name] = {}

        db_folder = db[folder_name]

        # Corrected Deletion Detection: Compare new filenames in DB with current filenames
        db_current_files = set(db_folder.keys())
        current_files_set = set(current_files)
        deleted_files = db_current_files - current_files_set

        if deleted_files:
            for del_file in deleted_files:
                logging.info(f"  File deleted since last run: {del_file}")
                del db_folder[del_file]

        # Prepare list of files to process
        files_to_process = []
        for filename in current_files:
            # Extract the original base filename (without prefix) if it has one
            match = re.match(r'^(' + descriptor + r')\d+(_[A-Za-z#]+)?_(.+)', filename)
            if match:
                original_base_with_ext = match.group(3)
            else:
                # File has no prefix
                original_base_with_ext = filename

            # Split the original base to get base name and extension
            original_base, ext = os.path.splitext(original_base_with_ext)
            if not ext:
                # If there was no extension in original_base_with_ext, get it from filename
                ext = os.path.splitext(filename)[1]
            files_to_process.append((filename, original_base, ext))

        # Extract keys for files that require it
        if extract_key_flag:
            files_with_keys = []
            for filename, original_base, ext in files_to_process:
                original_file_path = os.path.join(folder_path, filename)
                key_scale = extract_key(original_file_path)
                if key_scale is None:
                    key_scale = "Unknown"
                # Remove any problematic characters from key_scale
                key_scale_clean = re.sub(r'[^\w#]+', '', key_scale)
                files_with_keys.append((key_scale_clean, original_base, ext, filename))
            # Sort files based on Circle of Fifths positions
            files_with_keys.sort(key=lambda x: (
                get_circle_of_fifths_position(get_root_note_and_scale(x[0])[0]),
                get_root_note_and_scale(x[0])[1],  # Scale ('maj', 'min', etc.)
                x[1]))  # Original base filename
            sorted_files = files_with_keys
        else:
            # For descriptors without key extraction, sort alphabetically
            files_with_keys = [(None, original_base, ext, filename) for filename, original_base, ext in files_to_process]
            sorted_files = sorted(files_with_keys, key=lambda x: x[1])

        # Reindexing: Assign new indices based on sorted order
        for idx, (key_scale_clean, original_base, ext, filename) in enumerate(sorted_files, start=1):
            original_file_path = os.path.join(folder_path, filename)
            try:
                file_mtime = os.path.getmtime(original_file_path)
            except Exception as e:
                logging.error(f"    Unable to get modification time for {original_file_path}: {e}")
                continue

            # Build the new filename
            new_filename = f"{descriptor}{idx}"
            if extract_key_flag and key_scale_clean and key_scale_clean != "Unknown":
                new_filename += f"_{key_scale_clean}"
            new_filename += f"_{original_base}{ext}"

            new_file_path = os.path.join(folder_path, new_filename)

            # Check if the file has been processed before
            existing_entry = db_folder.get(new_filename)

            # Check if the file needs to be processed or renamed
            needs_processing = True
            if existing_entry:
                if existing_entry['last_modified'] == file_mtime and existing_entry['index'] == idx:
                    # File unchanged and index unchanged, skip processing
                    needs_processing = False

            if needs_processing:
                # Normalize and export
                try:
                    # Extract the file extension without the dot and convert to lower case
                    file_ext = ext[1:].lower()
                    # Map the file extension to the correct ffmpeg format identifier
                    format_identifier = format_mapping.get(file_ext)
                    if not format_identifier:
                        logging.warning(f"    Unsupported file format for file: {original_file_path}")
                        continue
                    # Load the audio file using pydub
                    audio = AudioSegment.from_file(original_file_path, format=format_identifier)
                    # Normalize the audio
                    normalized_audio = normalize_audio(audio)
                    # Check for filename conflicts
                    if os.path.exists(new_file_path) and new_file_path != original_file_path:
                        logging.error(f"    Conflict: The target filename '{new_filename}' already exists. Skipping file: {filename}")
                        continue
                    # Export the normalized audio with the new filename
                    normalized_audio.export(new_file_path, format=format_identifier)
                    # Remove the original file if the name has changed
                    if new_file_path != original_file_path:
                        os.remove(original_file_path)
                        logging.info(f"    Processed and renamed to: {new_filename}")
                    else:
                        logging.info(f"    Processed without renaming: {new_filename}")
                    # Update db entry
                    db_folder[new_filename] = {
                        'original_name': original_base + ext,
                        'new_filename': new_filename,
                        'last_modified': file_mtime,
                        'descriptor': descriptor,
                        'index': idx,
                        'key': key_scale_clean if extract_key_flag else None
                    }
                    # Remove old db entry if filename changed
                    if filename != new_filename and filename in db_folder:
                        del db_folder[filename]
                except Exception as e:
                    logging.error(f"    Error processing file {original_file_path}: {e}")
                    continue
            else:
                # File unchanged, ensure it's correctly named
                if filename != new_filename:
                    try:
                        # Check for filename conflicts
                        if os.path.exists(new_file_path) and new_file_path != original_file_path:
                            logging.error(f"    Conflict: The target filename '{new_filename}' already exists. Skipping renaming for file: {filename}")
                            continue
                        # Rename the file
                        os.rename(original_file_path, new_file_path)
                        logging.info(f"    Renamed to: {new_filename}")
                        # Update db entry
                        db_folder[new_filename] = db_folder.pop(filename)
                        db_folder[new_filename]['new_filename'] = new_filename
                        db_folder[new_filename]['index'] = idx
                    except Exception as e:
                        logging.error(f"    Error renaming file {filename}: {e}")
                        continue

        # Update the database for this folder
        db[folder_name] = db_folder

    # Save the updated database
    save_db(db)

    logging.info("\nProcessing complete.")

if __name__ == "__main__":
    main()