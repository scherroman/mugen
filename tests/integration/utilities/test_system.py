import os
from typing import Optional

from mugen.utilities import system

TEST_DIRECTORY_NAME = "test_directory"
TEST_FILE_NAME = "test.txt"


def test_touch__creates_file(tmp_path):
    file_path = os.path.join(tmp_path, TEST_FILE_NAME)
    assert not os.path.exists(file_path)
    system.touch(file_path)
    assert os.path.exists(file_path)


def test_ensure_directory_exists__leaves_directory_alone_if_it_already_exists(tmp_path):
    file_path = os.path.join(tmp_path, TEST_FILE_NAME)
    assert not os.path.exists(file_path)
    system.touch(file_path)
    system.ensure_directory_exists(tmp_path)
    assert os.path.exists(file_path)


def test_ensure_directory_exists__creates_directory_if_it_doesnt_exist(tmp_path):
    directory_path = os.path.join(tmp_path, TEST_DIRECTORY_NAME)
    assert not os.path.exists(directory_path)
    system.ensure_directory_exists(directory_path)
    assert os.path.exists(directory_path)


def test_recreate_directory__creates_directory_if_it_doesnt_exist(tmp_path):
    directory_path = os.path.join(tmp_path, TEST_DIRECTORY_NAME)
    assert not os.path.exists(directory_path)
    system.recreate_directory(directory_path)
    assert os.path.exists(directory_path)


def test_recreate_directory__deletes_and_recreates_directory_if_it_already_exists(
    tmp_path,
):
    directory_path = os.path.join(tmp_path, TEST_DIRECTORY_NAME)
    file_path = os.path.join(directory_path, TEST_FILE_NAME)
    system.ensure_directory_exists(directory_path)
    system.touch(file_path)
    assert os.path.exists(file_path)
    system.recreate_directory(directory_path)
    assert os.path.exists(directory_path)
    assert not os.path.exists(file_path)


def test_list_directory_files__lists_only_files(tmp_path):
    items = system.list_directory_files(tmp_path)
    assert len(items) == 0

    directory_path = os.path.join(tmp_path, TEST_DIRECTORY_NAME)
    file_path = os.path.join(tmp_path, TEST_FILE_NAME)
    system.ensure_directory_exists(directory_path)
    system.touch(file_path)
    items = system.list_directory_files(tmp_path)
    assert len(list(items)) == 1


def test_run_command__runs_successfully():
    result = system.run_command(["which", "python"])
    assert result is not None


@system.use_temporary_file_fallback("path", ".txt")
def create_file(path: Optional[str] = None):
    system.touch(path)
    return path


def test_use_temporary_file_fallback__uses_path_if_path_is_passed_in(tmp_path):
    file_path = os.path.join(tmp_path, "other.txt")
    path = create_file(file_path)
    assert path == file_path


def test_use_temporary_file_fallback__uses_a_temporary_fallback_path_if_path_is_not_passed_in():
    path = create_file()
    assert isinstance(path, str)
    assert os.path.exists(path)
