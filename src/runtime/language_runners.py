import os
import subprocess
import tempfile
import uuid
from typing import Optional


# ------------------------------------------------------------
# Helper: run shell commands safely
# ------------------------------------------------------------
def run_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1


# ------------------------------------------------------------
# C++ RUNNER
# ------------------------------------------------------------
def run_cpp(code: str) -> str:
    """
    Saves C++ code, compiles it with g++/clang++, runs it, returns output.
    """
    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, "segment.cpp")
    exe_path = os.path.join(tempdir, "a.out")

    with open(file_path, "w") as f:
        f.write(code)

    # Compile
    out, err, rc = run_cmd(f"g++ {file_path} -o {exe_path}")
    if rc != 0:
        return f"[C++ COMPILE ERROR]\n{err}"

    # Run
    out, err, rc = run_cmd(exe_path)
    if rc != 0:
        return f"[C++ RUNTIME ERROR]\n{err}"

    return out


# ------------------------------------------------------------
# RUST RUNNER
# ------------------------------------------------------------
def run_rust(code: str) -> str:
    """
    Uses rustc to compile and run Rust segments.
    """
    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, "segment.rs")
    exe_path = os.path.join(tempdir, "segment_exec")

    with open(file_path, "w") as f:
        f.write(code)

    # Compile
    out, err, rc = run_cmd(f"rustc {file_path} -o {exe_path}")
    if rc != 0:
        return f"[RUST COMPILE ERROR]\n{err}"

    # Run
    out, err, rc = run_cmd(exe_path)
    if rc != 0:
        return f"[RUST RUNTIME ERROR]\n{err}"

    return out


# ------------------------------------------------------------
# GO RUNNER
# ------------------------------------------------------------
def run_go(code: str) -> str:
    """
    Uses 'go run' to directly execute Go code.
    """
    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, "segment.go")

    with open(file_path, "w") as f:
        f.write(code)

    out, err, rc = run_cmd(f"go run {file_path}")
    if rc != 0:
        return f"[GO ERROR]\n{err}"

    return out


# ------------------------------------------------------------
# JAVA RUNNER
# ------------------------------------------------------------
def run_java(code: str) -> str:
    """
    Saves Java code, compiles with javac, runs it.
    Requires that the transpiled Java code has:
    
        public class Segment { public static void main(String[] args) {...} }
    """
    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, "Segment.java")

    with open(file_path, "w") as f:
        f.write(code)

    # Compile
    out, err, rc = run_cmd(f"javac {file_path}")
    if rc != 0:
        return f"[JAVA COMPILE ERROR]\n{err}"

    # Run
    out, err, rc = run_cmd(f"java -cp {tempdir} Segment")
    if rc != 0:
        return f"[JAVA RUNTIME ERROR]\n{err}"

    return out


# ------------------------------------------------------------
# Unified interface for orchestrator
# ------------------------------------------------------------
LANGUAGE_RUNNERS = {
    "cpp": run_cpp,
    "rust": run_rust,
    "go": run_go,
    "java": run_java
}
