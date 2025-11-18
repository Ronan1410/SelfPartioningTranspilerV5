# src/transpilers/java_transpiler.py
import re
import shutil
import subprocess
import tempfile
import os
from typing import Tuple

def _escape_java_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

class JavaTranspiler:
    """
    Hybrid Java generator. compile_and_run uses javac + java.
    """
    def file_extension(self):
        return ".java"

    def transpile(self, segment: str) -> str:
        lines = [ln.rstrip() for ln in segment.strip().splitlines()]
        methods = []
        main_lines = []
        in_func = False
        func_body = []
        func_sig = None

        def flush_func():
            nonlocal func_sig, func_body, methods
            if not func_sig:
                return
            methods.append(func_sig)
            methods.extend("    " + b for b in func_body)
            methods.append("}")
            func_body = []

        for raw in lines:
            line = raw.strip()
            m = re.match(r"def\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*:", line)
            if m:
                flush_func()
                name = m.group(1)
                args = m.group(2).strip()
                if args:
                    arg_list = ", ".join(f"int {a.strip()}" for a in args.split(","))
                else:
                    arg_list = ""
                func_sig = f"public static int {name}({arg_list}) " + "{"
                in_func = True
                func_body = []
                continue

            if (raw.startswith("    ") or raw.startswith("\t")) and in_func:
                src = raw.lstrip()
                mr = re.match(r"return\s+(.+)", src)
                if mr:
                    func_body.append(f"return {mr.group(1)};")
                    continue
                ma = re.match(r"([A-Za-z_]\w*)\s*=\s*(.+)", src)
                if ma:
                    func_body.append(f"int {ma.group(1)} = {ma.group(2)};")
                    continue
                mp = re.match(r"print\((.*)\)", src)
                if mp:
                    expr = mp.group(1)
                    func_body.append(f"System.out.println({expr});")
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
                main_lines.append(f"System.out.println({expr});")
                continue
            ma = re.match(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
            if ma:
                main_lines.append(f"int {ma.group(1)} = {ma.group(2)};")
                continue
            mc = re.match(r"([A-Za-z_]\w*)\((.*)\)", line)
            if mc:
                name = mc.group(1)
                args = mc.group(2).strip()
                main_lines.append(f"{name}({args});")
                continue
            if not line:
                continue
            main_lines.append(f'System.out.println("UNSUPPORTED: {_escape_java_str(line)}");')

        if in_func:
            flush_func()

        out = []
        out.append("public class Generated {")
        if methods:
            for m in methods:
                out.append("    " + m)
        out.append("    public static void main(String[] args) {")
        if main_lines:
            for ml in main_lines:
                out.append("        " + ml)
        else:
            out.append('        System.out.println("Java segment executed");')
        out.append("    }")
        out.append("}")
        return "\n".join(out)

    def compile_and_run(self, source: str) -> Tuple[str, str, int]:
        if shutil.which("javac") is None or shutil.which("java") is None:
            return ("", "[ERROR] 'javac' or 'java' not found in PATH. Install JDK.", 127)

        with tempfile.TemporaryDirectory() as tmp:
            src_path = os.path.join(tmp, "Generated.java")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(source)
            proc = subprocess.run(["javac", src_path], capture_output=True, text=True)
            if proc.returncode != 0:
                return ("", proc.stderr, proc.returncode)
            # run
            run = subprocess.run(["java", "-cp", tmp, "Generated"], capture_output=True, text=True)
            return (run.stdout, run.stderr, run.returncode)
