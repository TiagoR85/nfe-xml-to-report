from __future__ import annotations

import subprocess
from pathlib import Path


def executar_tool(
    dir_in: Path, dir_out: Path, formato: str = "all", tool_path: str | None = None
) -> int:
    dir_out.mkdir(parents=True, exist_ok=True)
    cmd = [
        tool_path or "nfe-report",
        "generate",
        "--in", str(dir_in),
        "--out", str(dir_out),
        "--format", formato,
    ]
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).returncode
    except (OSError, subprocess.SubprocessError):
        return 3
