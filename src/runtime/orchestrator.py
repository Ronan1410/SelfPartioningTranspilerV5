import os
import subprocess
import tempfile

class Orchestrator:
    """
    Coordinates:
    - receiving code segments
    - calling the correct transpiler
    - writing transpiled code to temp files
    - compiling + running
    """

    def __init__(self, transpilers: dict):
        self.transpilers = transpilers

    def process_segments(self, segments):
        print(f"[Orchestrator] Received {len(segments)} segments.")

        for i, segment in enumerate(segments):
            lang = segment.get("language")
            code  = segment.get("code")

            print(f"\n[Segment {i}] Using language: {lang}")
            print("[Original Code]")
            print(code)

            transpiler = self.transpilers.get(lang)
            if transpiler is None:
                print(f"[Error] No transpiler available for '{lang}'")
                continue

            transpiled = transpiler.transpile(code)
            print("[Transpiled Code]")
            print(transpiled)

            self._execute_transpiled(lang, transpiled, i)

    def _execute_transpiled(self, lang: str, code: str, index: int):
        """
        Writes transpiled code to a temp file,
        compiles it (if needed), and runs it.
        """

        print(f"[Execution] Running {lang} code for segment {index}")

        with tempfile.TemporaryDirectory() as tmp:
            if lang == "cpp":
                src = os.path.join(tmp, "main.cpp")
                exe = os.path.join(tmp, "main.exe")
                with open(src, "w") as f:
                    f.write(code)

                subprocess.run(["g++", src, "-o", exe], check=False)
                subprocess.run([exe], check=False)

            elif lang == "rust":
                src = os.path.join(tmp, "main.rs")
                exe = os.path.join(tmp, "main.exe")
                with open(src, "w") as f:
                    f.write(code)
                subprocess.run(["rustc", src, "-o", exe], check=False)
                subprocess.run([exe], check=False)

            elif lang == "go":
                src = os.path.join(tmp, "main.go")
                with open(src, "w") as f:
                    f.write(code)
                subprocess.run(["go", "run", src], check=False)

            elif lang == "java":
                src = os.path.join(tmp, "Main.java")
                with open(src, "w") as f:
                    f.write(code)
                subprocess.run(["javac", src], check=False)
                subprocess.run(["java", "-cp", tmp, "Main"], check=False)

            else:
                print(f"[ERROR] Unknown language: {lang}")
