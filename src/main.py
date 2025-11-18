from src.splitter.splitter import CodeSplitter
from src.transpilers.cpp_transpiler import CppTranspiler
from src.transpilers.rust_transpiler import RustTranspiler
from src.transpilers.go_transpiler import GoTranspiler
from src.transpilers.java_transpiler import JavaTranspiler
from src.runtime.orchestrator import Orchestrator

def main():
    print("Self-Partitioning Transpiler v5.0")

    with open("example/sample.py", "r") as f:
        input_code = f.read()

    splitter = CodeSplitter()
    segments = splitter.split(input_code)

    transpilers = {
        "cpp": CppTranspiler(),
        "rust": RustTranspiler(),
        "go": GoTranspiler(),
        "java": JavaTranspiler(),
    }

    orchestrator = Orchestrator(transpilers)
    orchestrator.process_segments(segments)

if __name__ == "__main__":
    main()
