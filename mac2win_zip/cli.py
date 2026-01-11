#!/usr/bin/env python3
"""
mac2win-zip: Create Windows-compatible ZIP files from macOS
Handles Unicode normalization (NFD->NFC) and removes Windows forbidden characters
"""

import argparse
import os
import sys
import unicodedata
import zipfile


def sanitize_windows_filename(filename):
    """Remove Windows forbidden characters from filename, preserving path separators"""
    parts = filename.split("/")

    # Forbidden characters in Windows filenames (excluding forward slash for path separator)
    forbidden = '<>:"|?*'

    sanitized_parts = []
    for part in parts:
        # Skip empty parts and current/parent directory references
        if not part or part == "." or part == "..":
            continue

        # Remove forbidden characters
        result = part
        for char in forbidden:
            result = result.replace(char, "")

        # Remove backslash which could cause issues
        result = result.replace("\\", "")

        # Remove null bytes (security)
        result = result.replace("\x00", "")

        # Normalize whitespace
        result = " ".join(result.split())

        # Skip if result is empty after sanitization
        if not result:
            continue

        sanitized_parts.append(result)

    return "/".join(sanitized_parts)


def create_windows_compatible_zip(paths, output="archive.zip"):
    """Create Windows-compatible ZIP file from files and/or folders

    Args:
        paths: List of file or folder paths to zip
        output: Output ZIP filename

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        files_to_zip = []

        # Get absolute path of output file to exclude it from being zipped
        output_abspath = os.path.abspath(output)

        # Validate output path is writable
        output_dir = os.path.dirname(output_abspath)
        if output_dir and not os.path.exists(output_dir):
            print(f"Error: Output directory does not exist: {output_dir}")
            return False

        # Collect all files from the provided paths
        for path in paths:
            if not os.path.exists(path):
                print(f"Warning: Path not found: {path}")
                continue

            try:
                if os.path.isfile(path):
                    # Skip if this is the output file to avoid self-inclusion
                    if os.path.abspath(path) != output_abspath:
                        files_to_zip.append(path)
                elif os.path.isdir(path):
                    # Walk through directory recursively
                    for root, dirs, files in os.walk(path):
                        # Exclude hidden directories
                        dirs[:] = [d for d in dirs if not d.startswith(".")]

                        for file in files:
                            # Skip system files and hidden files
                            if file.startswith(".") or file in [".DS_Store", "__MACOSX"]:
                                continue
                            full_path = os.path.join(root, file)
                            # Skip if this is the output file to avoid self-inclusion
                            if os.path.abspath(full_path) != output_abspath:
                                files_to_zip.append(full_path)
            except PermissionError as e:
                print(f"Warning: Permission denied for {path}: {e}")
                continue
            except OSError as e:
                print(f"Warning: Cannot access {path}: {e}")
                continue

        if not files_to_zip:
            print("No files found in the specified paths")
            return False

        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in files_to_zip:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        files_to_zip = unique_files

        print(f"Processing {len(files_to_zip)} files...")

        # Create ZIP file
        try:
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zipf:
                for filepath in sorted(files_to_zip):
                    try:
                        # Normalize to NFC and sanitize filename
                        nfc_filename = unicodedata.normalize("NFC", filepath)
                        safe_filename = sanitize_windows_filename(nfc_filename)
                        zipf.write(filepath, arcname=safe_filename)
                        print(f"  Added: {filepath}")
                    except FileNotFoundError:
                        print(f"Warning: File disappeared during zipping: {filepath}")
                        continue
                    except PermissionError as e:
                        print(f"Warning: Cannot read {filepath}: {e}")
                        continue
                    except OSError as e:
                        print(f"Warning: Error adding {filepath}: {e}")
                        continue
        except OSError as e:
            print(f"Error: Cannot create ZIP file {output}: {e}")
            return False
        except zipfile.BadZipFile as e:
            print(f"Error: ZIP file creation failed: {e}")
            return False

        print(f"\nCreated: {output} ({os.path.getsize(output) / 1024 / 1024:.2f} MB)")

        # Verify - check each path component separately
        forbidden = '<>:"|\\?*'  # Exclude / as it's used for path separator in ZIP
        try:
            with zipfile.ZipFile(output, "r") as zipf:
                for info in zipf.filelist:
                    # Check NFC normalization
                    if unicodedata.normalize("NFC", info.filename) != info.filename:
                        print(f"Warning: {info.filename} is not NFC normalized")
                        return False

                    # Check forbidden characters in each path component
                    parts = info.filename.split("/")
                    for part in parts:
                        if any(char in forbidden for char in part):
                            print(f"Warning: {part} contains forbidden characters")
                            return False
        except zipfile.BadZipFile as e:
            print(f"Warning: ZIP verification failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="Create Windows-compatible ZIP files from macOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                               # Zip current directory to archive.zip
  %(prog)s folder1                       # Zip folder1 (recursive)
  %(prog)s file1.pdf file2.jpg           # Zip specific files
  %(prog)s folder1 file.pdf -o out.zip   # Zip mixed items
  %(prog)s -o backup.zip                 # Zip current dir with custom name

Features:
  - Recursively includes all subdirectories
  - Preserves folder structure in ZIP
  - Handles Unicode filenames (NFD->NFC)
  - Removes Windows-forbidden characters
  - Excludes hidden files (.DS_Store, etc)
        """,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or folders to zip (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output", default="archive.zip", help="Output ZIP filename (default: archive.zip)"
    )

    args = parser.parse_args()

    # Auto-name zip file based on folder name
    output = args.output
    if output == "archive.zip" and len(args.paths) == 1:
        path = args.paths[0]
        if os.path.isdir(path):
            # Use folder name as zip filename (including current directory)
            folder_name = os.path.basename(os.path.abspath(path))
            if folder_name:
                output = f"{folder_name}.zip"

    success = create_windows_compatible_zip(args.paths, output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
