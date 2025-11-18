# src/transpilers/rust_transpiler.py
import re
import shutil
import subprocess
import tempfile
import os
from typing import Tuple, List

def _escape_rust_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

class RustTranspiler:
    """
    Hybrid Rust transpiler for simple Python -> Rust code.
    - Supports: def ... (simple), return, assignments, print(), simple calls
    - Falls back to comments / println placeholders for unsupported constructs.
    """
    def file_extension(self):
        return ".rs"

    def transpile(self, segment: str) -> str:
        lines = [ln.rstrip() for ln in segment.strip().splitlines()]
        funcs: List[str] = []
        main_lines: List[str] = []
        in_func = False
        func_body: List[str] = []
        func_sig: str | None = None

        def flush_func():
            nonlocal func_sig, func_body, funcs
            if not func_sig:
                return
            funcs.append(func_sig)
            funcs.extend("    " + b for b in func_body)
            funcs.append("}")
            # reset
            func_body = []

        for raw in lines:
            line = raw.strip()

            # function header
            m = re.match(r"def\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*:", line)
            if m:
                # flush any previous
                flush_func()
                name = m.group(1)
                args = m.group(2).strip()
                if args:
                    arg_list = ", ".join(f"{a.strip()}: i64" for a in args.split(","))
                else:
                    arg_list = ""
                # assume i64 return for numeric functions
                func_sig = f"fn {name}({arg_list}) -> i64 " + "{"
                in_func = True
                func_body = []
                continue

            # function body lines (rudimentary: detect indentation)
            if (raw.startswith("    ") or raw.startswith("\t")) and in_func:
                src = raw.lstrip()

                # return
                mr = re.match(r"return\s+(.+)", src)
                if mr:
                    func_body.append(f"return {mr.group(1)};")
                    continue

                # assignment
                ma = re.match(r"([A-Za-z_]\w*)\s*=\s*(.+)", src)
                if ma:
                    func_body.append(f"let mut {ma.group(1)} = {ma.group(2)};")
                    continue

                # print inside function
                mp = re.match(r"print\((.*)\)", src)
                if mp:
                    expr = mp.group(1)
                    # print value with debug formatting to be generic
                    func_body.append(f'println!("{{:?}}", {expr});')
                    continue

                # fallback comment
                func_body.append(f'// [UNTRANSLATED] {src}')
                continue

            # end of function if indent ended
            if in_func and not (raw.startswith("    ") or raw.startswith("\t")):
                flush_func()
                in_func = False
                func_sig = None

            # top-level: print
            mp = re.match(r"print\((.*)\)", line)
            if mp:
                expr = mp.group(1)
                main_lines.append(f'println!("{{:?}}", {expr});')
                continue

            # top-level assignment
            ma = re.match(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
            if ma:
                main_lines.append(f"let mut {ma.group(1)} = {ma.group(2)};")
                continue

            # top-level function call
            mc = re.match(r"([A-Za-z_]\w*)\((.*)\)", line)
            if mc:
                name = mc.group(1)
                args = mc.group(2).strip()
                if args:
                    main_lines.append(f"{name}({args});")
                else:
                    main_lines.append(f"{name}();")
                continue

            # blank line
            if not line:
                continue

            # fallback: print unsupported line as message
            main_lines.append(f'println!("UNSUPPORTED: { _escape_rust_str(line) }");')

        # flush if function still open
        if in_func:
            flush_func()

        # assemble output
        out: List[str] = []
        out.append("// AUTO-GENERATED Rust segment")
        out.append("")
        if funcs:
            out.extend(funcs)
            out.append("")

        out.append("fn main() {")
        if main_lines:
            out.extend("    " + l for l in main_lines)
        else:
            out.append('    println!("Rust segment executed");')
        out.append("}")
        return "\n".join(out)

    def compile_and_run(self, source: str) -> Tuple[str, str, int]:
        """
        Compiles the provided Rust source using rustc (must be in PATH) and runs the produced exe.
        Returns (stdout, stderr, returncode).
        """
        if shutil.which("rustc") is None:
            return ("", "[ERROR] 'rustc' not found in PATH. Install Rust and add to PATH.", 127)

        with tempfile.TemporaryDirectory() as tmp:
            src_path = os.path.join(tmp, "segment.rs")
            exe_path = os.path.join(tmp, "segment.exe")

            with open(src_path, "w", encoding="utf-8") as f:
                f.write(source)

            # compile
            proc = subprocess.run(["rustc", src_path, "-o", exe_path], capture_output=True, text=True)
            if proc.returncode != 0:
                return ("", proc.stderr, proc.returncode)

            # run
            run = subprocess.run([exe_path], capture_output=True, text=True)
            return (run.stdout, run.stderr, run.returncode)
