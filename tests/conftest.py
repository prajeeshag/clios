import os
import shutil

import pytest


@pytest.fixture
def copy_file(request, tmp_path):
    # Directory where this test file is located
    test_file_dir = request.path.parent
    # Directory where pytest is running

    def _copy(file_name: str):
        source_file = test_file_dir / file_name
        destination_file = tmp_path / file_name
        if source_file.exists():
            shutil.copy(source_file, destination_file)
        else:
            raise FileNotFoundError(f"File not found: {source_file}")
        os.chdir(tmp_path)

    # Return the list of copied files
    return _copy
