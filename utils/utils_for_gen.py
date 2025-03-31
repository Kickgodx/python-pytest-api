import chardet
import yaml
from typing import Optional


def detect_encoding(file_path: str) -> str:
    """
    Detects the encoding of a file with a fallback to utf-8.
    """
    with open(file_path, "rb") as file:
        raw_data = file.read(10000)  # Read first 10k bytes for efficiency

    result = chardet.detect(raw_data)
    encoding = result["encoding"]

    # Fallback to utf-8 if confidence is too low
    if result["confidence"] < 0.7:
        encoding = "utf-8"

    return encoding or "utf-8"  # Default to utf-8 if encoding is None


def convert_to_utf8(file_path: str):
    """
    Converts a file to UTF-8 encoding.
    Handles cases where the detected encoding might fail.
    """
    try:
        # First try with detected encoding
        encoding = detect_encoding(file_path)
        with open(file_path, "r", encoding=encoding, errors="replace") as file:
            content = file.read()
    except UnicodeDecodeError:
        # If detection fails, try common encodings with error handling
        encodings_to_try = ["utf-8", "cp1252", "iso-8859-1", "cp437"]
        for enc in encodings_to_try:
            try:
                with open(file_path, "r", encoding=enc, errors="strict") as file:
                    content = file.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            # If all encodings fail, use replace mode to handle invalid chars
            with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                content = file.read()

    # Write back as UTF-8
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def get_description_from_yaml(file_path: str) -> Optional[str]:
    """
    Extracts the description from a YAML file.
    Returns None if the description is not found or if there's an error.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            yaml_content = yaml.safe_load(file)
        return yaml_content.get("info", {}).get("description", None)
    except (yaml.YAMLError, UnicodeDecodeError, IOError) as e:
        print(f"Error reading YAML file {file_path}: {str(e)}")
        return None


def add_description_to_file(file_path: str, description: str, ms: str):
    """
    Adds a description comment to the beginning of a file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        description_comment = f"# {ms}: {description}\n" if description else ""

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(description_comment + content)
    except IOError as e:
        print(f"Error processing file {file_path}: {str(e)}")