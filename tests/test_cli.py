"""Tests for mac2win_zip.cli module"""

import tempfile
import unicodedata
import zipfile
from pathlib import Path

import pytest

from mac2win_zip.cli import create_windows_compatible_zip, sanitize_windows_filename


class TestSanitizeWindowsFilename:
    """Test sanitize_windows_filename function"""

    def test_removes_forbidden_characters(self):
        """Test that forbidden characters are removed"""
        assert sanitize_windows_filename("test<file>.txt") == "testfile.txt"
        assert sanitize_windows_filename("file:with|bad*chars?.txt") == "filewithbadchars.txt"

    def test_preserves_path_separators(self):
        """Test that path separators are preserved"""
        assert sanitize_windows_filename("folder/subfolder/file.txt") == "folder/subfolder/file.txt"

    def test_removes_backslashes(self):
        """Test that backslashes are removed"""
        assert sanitize_windows_filename("folder\\file.txt") == "folderfile.txt"

    def test_normalizes_whitespace(self):
        """Test that whitespace is normalized"""
        assert sanitize_windows_filename("file   with   spaces.txt") == "file with spaces.txt"

    def test_complex_path(self):
        """Test complex path with multiple issues"""
        input_path = "folder/sub:folder/file*name?.txt"
        expected = "folder/subfolder/filename.txt"
        assert sanitize_windows_filename(input_path) == expected

    def test_sanitize_path_traversal(self):
        """Test that path traversal attempts are blocked"""
        assert sanitize_windows_filename("../../etc/passwd") == "etc/passwd"
        assert sanitize_windows_filename("file/../../../secret") == "file/secret"
        assert sanitize_windows_filename("../../../") == ""
        assert sanitize_windows_filename("./file.txt") == "file.txt"

    def test_sanitize_null_bytes(self):
        """Test that null bytes are removed"""
        assert sanitize_windows_filename("file\x00.txt") == "file.txt"
        assert sanitize_windows_filename("folder\x00/file.txt") == "folder/file.txt"

    def test_sanitize_empty_components(self):
        """Test that empty path components are removed"""
        assert sanitize_windows_filename("////file.txt") == "file.txt"
        assert sanitize_windows_filename("folder//file.txt") == "folder/file.txt"
        assert sanitize_windows_filename("file.txt/") == "file.txt"


class TestCreateWindowsCompatibleZip:
    """Test create_windows_compatible_zip function"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files and folders for testing"""
        # Create simple file
        file1 = temp_dir / "file1.txt"
        file1.write_text("content1")

        # Create folder with files
        folder = temp_dir / "folder"
        folder.mkdir()
        (folder / "file2.txt").write_text("content2")

        # Create nested folder
        subfolder = folder / "subfolder"
        subfolder.mkdir()
        (subfolder / "file3.txt").write_text("content3")

        # Create hidden file (should be excluded)
        (folder / ".hidden").write_text("hidden")

        # Create .DS_Store (should be excluded)
        (folder / ".DS_Store").write_text("mac metadata")

        return {
            "file1": file1,
            "folder": folder,
            "subfolder": subfolder,
        }

    def test_zip_single_file(self, temp_dir, sample_files):
        """Test zipping a single file"""
        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip([str(sample_files["file1"])], str(output))

        assert result is True
        assert output.exists()

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            assert len(names) == 1
            assert sample_files["file1"].name in names[0]

    def test_zip_folder_recursive(self, temp_dir, sample_files):
        """Test zipping a folder recursively"""
        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip([str(sample_files["folder"])], str(output))

        assert result is True
        assert output.exists()

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            # Should include file2.txt and file3.txt, but not .hidden or .DS_Store
            assert len(names) == 2
            assert any("file2.txt" in name for name in names)
            assert any("file3.txt" in name for name in names)
            assert not any(".hidden" in name for name in names)
            assert not any(".DS_Store" in name for name in names)

    def test_zip_multiple_files(self, temp_dir, sample_files):
        """Test zipping multiple files"""
        output = temp_dir / "output.zip"
        file2 = sample_files["folder"] / "file2.txt"
        result = create_windows_compatible_zip(
            [str(sample_files["file1"]), str(file2)], str(output)
        )

        assert result is True

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            assert len(names) == 2

    def test_zip_mixed_files_and_folders(self, temp_dir, sample_files):
        """Test zipping a mix of files and folders"""
        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip(
            [str(sample_files["file1"]), str(sample_files["folder"])], str(output)
        )

        assert result is True

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            # file1.txt + folder/file2.txt + folder/subfolder/file3.txt
            assert len(names) == 3

    def test_preserves_folder_structure(self, temp_dir, sample_files):
        """Test that folder structure is preserved in ZIP"""
        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip([str(sample_files["folder"])], str(output))

        assert result is True

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            assert any("folder/file2.txt" in name for name in names)
            assert any("folder/subfolder/file3.txt" in name for name in names)

    def test_unicode_normalization(self, temp_dir):
        """Test that Unicode filenames are normalized to NFC"""
        # Create file with NFD normalized name (common on macOS)
        nfd_name = unicodedata.normalize("NFD", "한글파일.txt")
        nfd_file = temp_dir / nfd_name
        nfd_file.write_text("unicode content")

        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip([str(nfd_file)], str(output))

        assert result is True

        # Verify NFC normalization
        with zipfile.ZipFile(output, "r") as zf:
            for info in zf.filelist:
                assert unicodedata.normalize("NFC", info.filename) == info.filename

    def test_nonexistent_path(self, temp_dir):
        """Test handling of nonexistent paths"""
        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip([str(temp_dir / "nonexistent")], str(output))

        # Should return False when no valid files found
        assert result is False

    def test_empty_folder(self, temp_dir):
        """Test zipping an empty folder"""
        empty_folder = temp_dir / "empty"
        empty_folder.mkdir()

        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip([str(empty_folder)], str(output))

        # Should return False when no files to zip
        assert result is False

    def test_duplicate_files_removed(self, temp_dir, sample_files):
        """Test that duplicate file paths are removed"""
        output = temp_dir / "output.zip"
        # Pass the same file twice
        result = create_windows_compatible_zip(
            [str(sample_files["file1"]), str(sample_files["file1"])], str(output)
        )

        assert result is True

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            # Should only have one entry
            assert len(names) == 1

    def test_hidden_directories_excluded(self, temp_dir):
        """Test that hidden directories are excluded"""
        hidden_dir = temp_dir / ".hidden_folder"
        hidden_dir.mkdir()
        (hidden_dir / "file.txt").write_text("hidden content")

        regular_dir = temp_dir / "regular"
        regular_dir.mkdir()
        (regular_dir / "file.txt").write_text("regular content")

        output = temp_dir / "output.zip"
        result = create_windows_compatible_zip([str(temp_dir)], str(output))

        assert result is True

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            # Should not include files from .hidden_folder
            assert not any(".hidden_folder" in name for name in names)
            # Should include file from regular folder
            assert any("regular/file.txt" in name for name in names)

    def test_output_file_size_reported(self, temp_dir, sample_files, capsys):
        """Test that output file size is reported"""
        output = temp_dir / "output.zip"
        create_windows_compatible_zip([str(sample_files["file1"])], str(output))

        captured = capsys.readouterr()
        assert "Created:" in captured.out
        assert "MB" in captured.out

    def test_output_file_not_included_in_zip(self, temp_dir):
        """Test that the output zip file is not included in itself"""
        # Create a test directory with files
        test_folder = temp_dir / "test_folder"
        test_folder.mkdir()
        (test_folder / "file1.txt").write_text("content1")
        (test_folder / "file2.txt").write_text("content2")

        # Create the zip in the same directory
        output = test_folder / "archive.zip"
        result = create_windows_compatible_zip([str(test_folder)], str(output))

        assert result is True
        assert output.exists()

        # Verify that archive.zip is not included in itself
        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            # Should only have file1.txt and file2.txt
            assert len(names) == 2
            assert any("file1.txt" in name for name in names)
            assert any("file2.txt" in name for name in names)
            # archive.zip should NOT be included
            assert not any("archive.zip" in name for name in names)

    def test_output_file_not_included_when_running_twice(self, temp_dir):
        """Test that running zip creation twice doesn't create nested archives"""
        test_folder = temp_dir / "test_folder"
        test_folder.mkdir()
        (test_folder / "file.txt").write_text("content")

        output = test_folder / "archive.zip"

        # First run
        result1 = create_windows_compatible_zip([str(test_folder)], str(output))
        assert result1 is True

        # Second run (archive.zip now exists)
        result2 = create_windows_compatible_zip([str(test_folder)], str(output))
        assert result2 is True

        # Verify no nested archive
        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            # Should only have file.txt
            assert len(names) == 1
            assert "file.txt" in names[0]
            # archive.zip should NOT be in the zip
            assert not any("archive.zip" in name for name in names)


class TestMain:
    """Test main() function and CLI behavior"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_auto_naming_single_folder(self, temp_dir, monkeypatch):
        """Test that single folder is named after the folder"""
        import sys

        from mac2win_zip.cli import main

        test_folder = temp_dir / "MyFolder"
        test_folder.mkdir()
        (test_folder / "file.txt").write_text("content")

        # Change to temp directory
        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr(sys, "argv", ["mac2win-zip", "MyFolder"])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        # Should create MyFolder.zip, not archive.zip
        assert (temp_dir / "MyFolder.zip").exists()
        assert not (temp_dir / "archive.zip").exists()

    def test_auto_naming_current_directory(self, temp_dir, monkeypatch):
        """Test that current directory uses directory name"""
        import sys

        from mac2win_zip.cli import main

        test_folder = temp_dir / "ProjectDir"
        test_folder.mkdir()
        (test_folder / "file.txt").write_text("content")

        # Change to test folder
        monkeypatch.chdir(test_folder)
        monkeypatch.setattr(sys, "argv", ["mac2win-zip", "."])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        # Should create ProjectDir.zip in current directory
        assert (test_folder / "ProjectDir.zip").exists()

    def test_explicit_output_overrides_auto_naming(self, temp_dir, monkeypatch):
        """Test that -o option overrides auto-naming"""
        import sys

        from mac2win_zip.cli import main

        test_folder = temp_dir / "MyFolder"
        test_folder.mkdir()
        (test_folder / "file.txt").write_text("content")

        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr(sys, "argv", ["mac2win-zip", "MyFolder", "-o", "custom.zip"])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        # Should create custom.zip, not MyFolder.zip
        assert (temp_dir / "custom.zip").exists()
        assert not (temp_dir / "MyFolder.zip").exists()

    def test_multiple_items_use_archive_zip(self, temp_dir, monkeypatch):
        """Test that multiple items use default archive.zip"""
        import sys

        from mac2win_zip.cli import main

        folder1 = temp_dir / "Folder1"
        folder1.mkdir()
        (folder1 / "file1.txt").write_text("content1")

        folder2 = temp_dir / "Folder2"
        folder2.mkdir()
        (folder2 / "file2.txt").write_text("content2")

        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr(sys, "argv", ["mac2win-zip", "Folder1", "Folder2"])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        # Should create archive.zip, not Folder1.zip
        assert (temp_dir / "archive.zip").exists()
        assert not (temp_dir / "Folder1.zip").exists()

    def test_single_file_uses_archive_zip(self, temp_dir, monkeypatch):
        """Test that single file uses default archive.zip"""
        import sys

        from mac2win_zip.cli import main

        test_file = temp_dir / "document.pdf"
        test_file.write_text("pdf content")

        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr(sys, "argv", ["mac2win-zip", "document.pdf"])

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        # Should create archive.zip, not document.zip
        assert (temp_dir / "archive.zip").exists()
