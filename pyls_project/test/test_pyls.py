import json
import pytest
import subprocess

@pytest.fixture(scope="module")
def sample_json(tmpdir_factory):
    structure = {
        "name": "root",
        "contents": [
            {
                "name": "go.mod",
                "permissions": "rw-r--r--",
                "size": 533,
                "time_modified": 1636920583
            },
            {
                "name": "parser",
                "permissions": "drwxr-xr-x",
                "size": 4096,
                "time_modified": 1636920583,
                "contents": [
                    {
                        "name": "parser.go",
                        "permissions": "rw-r--r--",
                        "size": 1622,
                        "time_modified": 1636920583
                    },
                    {
                        "name": "parser_test.go",
                        "permissions": "rw-r--r--",
                        "size": 1342,
                        "time_modified": 1636920583
                    }
                ]
            }
        ]
    }
    json_file = tmpdir_factory.mktemp("data").join("structure.json")
    with open(json_file, 'w') as f:
        json.dump(structure, f)
    return json_file

def test_ls(sample_json):
    result = subprocess.run(
        ["python", "-m", "pyls.pyls", "-l", "-H", "parser"],
        capture_output=True,
        text=True,
        env={"STRUCTURE_JSON": str(sample_json)}
    )
    assert result.returncode == 0
    output = result.stdout
    assert "-rw-r--r-- 1.6K" in output  # Check human-readable size format
    assert "-rw-r--r-- 1.3K" in output  # Check human-readable size format
    assert "parser.go" in output
    assert "parser_test.go" in output
    assert "go.mod" in output

def test_invalid_path(sample_json):
    result = subprocess.run(
        ["python", "-m", "pyls.pyls", "non_existent_path"],
        capture_output=True,
        text=True,
        env={"STRUCTURE_JSON": str(sample_json)}
    )
    assert result.returncode != 0
    assert "error: cannot access 'non_existent_path': No such file or directory" in result.stdout
