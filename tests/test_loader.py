from pathlib import Path

from src.common.loader import ls_all, ls_dir, ls_file


def test_ls_functions_with_tmp_path(tmp_path):
    # Create directories and files
    d1 = tmp_path / "dir1"
    d2 = tmp_path / "dir2"
    f1 = tmp_path / "file1.txt"
    f2 = tmp_path / "file2.txt"
    d1.mkdir()
    d2.mkdir()
    f1.write_text("a")
    f2.write_text("b")

    all_items = ls_all(str(tmp_path))
    dir_items = ls_dir(str(tmp_path))
    file_items = ls_file(str(tmp_path))

    # Ensure sorted and correct contents
    assert all_items == sorted([str(p) for p in [d1, d2, f1, f2]])
    assert dir_items == sorted([str(d1), str(d2)])
    assert file_items == sorted([str(f1), str(f2)])
