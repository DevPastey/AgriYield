import subprocess
import sys
from pathlib import Path


def test_evapotranspiration_module_path_is_resolved_when_run_as_script():
    backend_dir = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "app/services/evapotranspiration.py"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "No module named 'app'" not in result.stderr
