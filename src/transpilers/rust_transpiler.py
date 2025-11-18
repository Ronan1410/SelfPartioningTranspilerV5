# src/transpilers/rust_transpiler.py

import subprocess
import tempfile
import os

class RustTranspiler:
    def transpile(self, code: str) -> str:
        """
        Uses py2rust from py2many to generate Rust code.
        """
        with tempfile.TemporaryDirectory() as tmp:
            src_path = os.path.join(tmp, "input.py")
            out_path = os.path.join(tmp, "output.rs")

            with open(src_path, "w") as f:
                f.write(code)

            cmd = ["py2rust", src_path, "-o", out_path]
            subprocess.run(cmd, check=False)

            if not os.path.exists(out_path):
                return "// ERROR: py2rust failed"

            with open(out_path, "r") as f:
                return f.read()
