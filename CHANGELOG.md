# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-11

### Added
- Initial public release
- Windows-compatible ZIP file creation from macOS
- Unicode normalization (NFD to NFC) for filenames
- Windows forbidden character sanitization
- Recursive directory zipping
- Automatic exclusion of hidden files and system files (.DS_Store, etc.)
- Auto-naming feature for single folder zips
- Custom output naming with `-o` option
- Comprehensive test suite with 72% coverage
- Full documentation (README, CONTRIBUTING, LICENSE)

### Features
- CLI tool with intuitive interface
- Support for multiple files and folders
- Folder structure preservation in ZIP files
- Path traversal prevention
- Self-exclusion (output zip not included in itself)
- Korean and Unicode filename support

## [Unreleased]

### Planned
- Improve test coverage to 90%+
- Add GitHub Actions CI/CD
- Consider PyPI distribution
- Performance optimizations for large files
- Progress bar for large operations

---

## Version History

- **1.0.1** (2025-01-11): Initial public release
