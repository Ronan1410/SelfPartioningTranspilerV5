# src/transpilers/go_transpiler.py
import re
import shutil
import subprocess
import tempfile
import os
from typing import Tuple

def _escape_go_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

class GoTranspiler:
    """
    Hybrid Go generator. compile_and_run uses `go run`.
    """
    def file_extension(self):
        return ".go"


    def transpile(self, segment: str) -> str:
        lines = [ln.rstrip() for ln in segment.strip().splitlines()]
        funcs = []
        main_lines = []
        in_func = False
        func_body = []
        func_sig = None

        def flush_func():
            nonlocal func_sig, func_body, funcs
            if not func_sig:
                return
            funcs.append(func_sig)
            funcs.extend("    " + b for b in func_body)
            funcs.append("}")
            func_body = []

        for raw in lines:
            line = raw.strip()
            m = re.match(r"def\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*:", line)
            if m:
                flush_func()
                name = m.group(1)
                args = m.group(2).strip()
                if args:
                    arg_list = ", ".join(f"{a.strip()} int" for a in args.split(","))
                else:
                    arg_list = ""
                func_sig = f"func {name}({arg_list}) int " + "{"
                in_func = True
                func_body = []
                continue

            if (raw.startswith("    ") or raw.startswith("\t")) and in_func:
                src = raw.lstrip()
                mr = re.match(r"return\s+(.+)", src)
                if mr:
                    func_body.append(f"return {mr.group(1)}")
                    continue
                ma = re.match(r"([A-Za-z_]\w*)\s*=\s*(.+)", src)
                if ma:
                    func_body.append(f"var {ma.group(1)} int = {ma.group(2)}")
                    continue
                mp = re.match(r"print\((.*)\)", src)
                if mp:
                    expr = mp.group(1)
                    func_body.append(f"fmt.Println({expr})")
                    continue
                func_body.append(f"// [UNTRANSLATED] {src}")
                continue

            if in_func:
                flush_func()
                in_func = False
                func_sig = None

            mp = re.match(r"print\((.*)\)", line)
            if mp:
                expr = mp.group(1)
                main_lines.append(f"fmt.Println({expr})")
                continue
            ma = re.match(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
            if ma:
                main_lines.append(f"var {ma.group(1)} int = {ma.group(2)}")
                continue
            mc = re.match(r"([A-Za-z_]\w*)\((.*)\)", line)
            if mc:
                name = mc.group(1)
                args = mc.group(2).strip()
                main_lines.append(f"{name}({args})")
                continue
            if not line:
                continue
            main_lines.append(f'fmt.Println("UNSUPPORTED: {_escape_go_str(line)}")')

        if in_func:
            flush_func()

        out = []
        out.append("package main")
        out.append("")
        out.append("import \"fmt\"")
        out.append("")
        if funcs:
            out.extend(funcs)
            out.append("")
        out.append("func main() {")
        if main_lines:
            out.extend("    " + ml for ml in main_lines)
        else:
            out.append('    fmt.Println("Go segment executed")')
        out.append("}")
        return "\n".join(out)

    def compile_and_run(self, source: str) -> Tuple[str, str, int]:
        if shutil.which("go") is None:
            return ("", "[ERROR] 'go' not found in PATH. Install Go and add to PATH.", 127)

        with tempfile.TemporaryDirectory() as tmp:
            src_path = os.path.join(tmp, "segment.go")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(source)
            # Use `go run`
            proc = subprocess.run(["go", "run", src_path], capture_output=True, text=True)
            return (proc.stdout, proc.stderr, proc.returncode)
