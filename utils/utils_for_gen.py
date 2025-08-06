from typing import Optional

import chardet
import yaml

CONFIDENCE_THRESHOLD = 0.7


def detect_encoding(file_path: str) -> str:
    """Detect the encoding of a file with a fallback to utf-8.

    @param file_path: Path to the file whose encoding is to be detected.
    """
    with open(file_path, "rb") as file:
        raw_data = file.read(10000)  # Read first 10k bytes for efficiency

    result = chardet.detect(raw_data)
    encoding = result["encoding"]

    # Fallback to utf-8 if confidence is too low
    if result["confidence"] < CONFIDENCE_THRESHOLD:
        encoding = "utf-8"

    return encoding or "utf-8"  # Default to utf-8 if encoding is None


def convert_to_utf8(file_path: str):
    """Convert a file to UTF-8 encoding.

    Handles cases where the detected encoding might fail.

    @param file_path: Path to the file to be converted.
    """
    try:
        # First try with detected encoding
        encoding = detect_encoding(file_path)
        with open(file_path, encoding=encoding, errors="replace") as file:
            content = file.read()
    except UnicodeDecodeError:
        # If detection fails, try common encodings with error handling
        encodings_to_try = ["utf-8", "cp1252", "iso-8859-1", "cp437"]
        for enc in encodings_to_try:
            try:
                with open(file_path, encoding=enc, errors="strict") as file:
                    content = file.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            # If all encodings fail, use replace mode to handle invalid chars
            with open(file_path, encoding="utf-8", errors="replace") as file:
                content = file.read()

    # Write back as UTF-8
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def get_description_from_yaml(file_path: str) -> Optional[str]:
    """Extract the description from a YAML file.

    @param file_path: Path to the YAML file.
    @return: The description string or None.
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            yaml_content = yaml.safe_load(file)
        return yaml_content.get("info", {}).get("description", None)
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as e:
        print(f"Error reading YAML file {file_path}: {e!s}")
        return None


def add_description_to_file(file_path: str, description: str, ms: str):
    """Add a description comment to the beginning of a file.

    @param file_path: Path to the file where the description will be added.
    @param description: The description to be added.
    @param ms: The message to be added.
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            content = file.read()

        description_comment = f"# {ms}: {description}\n" if description else ""

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(description_comment + content)
    except OSError as e:
        print(f"Error processing file {file_path}: {e!s}")
