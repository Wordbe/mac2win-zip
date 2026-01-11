# mac2win-zip

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-macOS-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
  <img src="https://img.shields.io/badge/package%20manager-uv-ff69b4.svg" alt="Package Manager">
</p>

<p align="center">
  <strong>Create Windows-compatible ZIP files from macOS</strong>
</p>


> **"Where's my files after I zip on Mac and open it in Windows?"**
> Garbled Korean filenames and missing characters? You're not alone. This tool fixes it.

| macOS (ZIP created)   | Windows (ZIP opened) |
| --------------------- | -------------------- |
| 📄 Hello?.pdf          | ❌ (removed)          |
| 📄 안녕하세요 세상.pdf | ❌ (removed)          |

​                                                                            **⬇️  Use mac2win-zip  ⬇️**

| macOS (ZIP created)   | Windows (ZIP opened)  |
| --------------------- | --------------------- |
| 📄 Hello.pdf          | ✅ Hello.pdf           |
| 📄 안녕하세요 세상.pdf | ✅ 안녕하세요 세상.pdf |

> With mac2win-zip, your filenames stay intact when opening on Windows!
> macOS에서 생성한 ZIP 파일을 Windows에서 열어도 파일명이 깨지지 않습니다.


## Why mac2win-zip?

### The Problem

macOS uses **NFD (Normalization Form Decomposed)** for Unicode filenames, while Windows uses **NFC (Normalization Form Composed)**. When you create a ZIP file on macOS containing files with Unicode characters (like Korean, Japanese, or special characters), Windows users often see garbled filenames.

Additionally, macOS allows certain characters in filenames (like `:` or `|`) that are forbidden on Windows.

### The Solution

`mac2win-zip` automatically:
1. Normalizes all filenames from NFD to NFC
2. Removes or replaces Windows-forbidden characters
3. Excludes macOS-specific files (`.DS_Store`, etc.)
4. Preserves the folder structure

**Result:** ZIP files that work perfectly on both macOS and Windows!

## Installation

### Option 1: Install from PyPI (Recommended)

Install directly using pip:

```bash
pip install mac2win-zip
```

Or using uv (faster):

```bash
uv tool install mac2win-zip
```

Now you can use `mac2win-zip` from anywhere!

### Option 2: Install from Source

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/Wordbe/mac2win-zip.git
cd mac2win-zip

# Install globally
uv tool install .
```

## Quick Start

```bash
# Zip current directory (creates current-folder-name.zip)
mac2win-zip

# Zip a specific folder (creates my-folder.zip)
mac2win-zip my-folder

# Zip multiple files (creates archive.zip by default)
mac2win-zip file1.pdf file2.jpg

# Custom output name with -o option
mac2win-zip my-folder -o backup.zip
```

## Usage Examples

### Basic Usage

```bash
# Zip everything in current directory (creates folder-name.zip)
mac2win-zip

# Zip a folder (automatically includes all subdirectories, creates folder1.zip)
mac2win-zip folder1

# Zip specific files (creates archive.zip)
mac2win-zip report.pdf presentation.pptx
```

### Advanced Usage

```bash
# Custom output name with -o option
mac2win-zip folder1 -o backup.zip

# Zip multiple folders and files together
mac2win-zip folder1 folder2 notes.txt -o backup-2024.zip

# Custom output location
mac2win-zip ~/Downloads -o ~/Desktop/downloads-backup.zip
```

### Help

```bash
mac2win-zip --help
```

## Features

- **Unicode Normalization**: Converts macOS NFD filenames to Windows-compatible NFC
- **Character Sanitization**: Removes Windows-forbidden characters (`<>:"|?*\`)
- **Auto Recursive**: Automatically includes all subdirectories when zipping folders
- **Smart Naming**: Creates `folder-name.zip` by default (no -o needed for single folder)
- **Structure Preservation**: Maintains original folder hierarchy in ZIP
- **Smart Filtering**: Excludes hidden files (`.DS_Store`, etc.)
- **Korean Support**: Perfect handling of Korean and other Unicode filenames
- **Simple CLI**: Intuitive command-line interface


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Bug Reports

If you discover any bugs, please create an issue on GitHub with:
- Your operating system and version
- Python version
- Steps to reproduce the bug
- Expected vs actual behavior

## Show Your Support

If this project helped you, please give it a star!

---

## How It Works

### Installation Process

When you run `uv tool install .`, here's what happens:

1. **Creates isolated environment**: uv creates a dedicated virtual environment at `~/.local/share/uv/tools/mac2win-zip/`
2. **Installs dependencies**: All required packages (pytest, black, ruff, etc.) are installed in this isolated environment
3. **Creates executable**: A wrapper script is generated that calls your Python code
4. **Symlinks to PATH**: A symbolic link is created at `~/.local/bin/mac2win-zip` pointing to the executable
5. **Ready to use**: Since `~/.local/bin` is in your PATH, you can now run `mac2win-zip` from anywhere

### File Locations

```
~/.local/share/uv/tools/mac2win-zip/  # Isolated environment with all dependencies
~/.local/bin/mac2win-zip              # Executable symlink (in your PATH)
```

### The Wrapper Script

The generated executable at `~/.local/bin/mac2win-zip` is a simple Python script:

```python
#!/path/to/python
import sys
from mac2win_zip.cli import main
sys.exit(main())
```

This is defined in `pyproject.toml`:

```toml
[project.scripts]
mac2win-zip = "mac2win_zip.cli:main"
```

### Benefits

- **Isolation**: Each tool has its own environment, no conflicts with other Python packages
- **System-wide access**: Works from any directory
- **Clean uninstall**: Easy to remove without leaving traces

### Uninstall

To remove the tool completely:

```bash
uv tool uninstall mac2win-zip
```

This removes both the isolated environment and the executable symlink.

---

<p align="center">
  Made with ❤️ by Wordbe for seamless macOS-Windows file sharing
</p>
