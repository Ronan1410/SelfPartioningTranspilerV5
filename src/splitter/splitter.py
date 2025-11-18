# src/splitter/splitter.py

from src.comfort_model.comfort import comfort_value


class CodeSplitter:
    """
    Splits code into segments and assigns target languages
    based on comfort value thresholds.
    """

    def __init__(self, segment_size: int = 5):
        self.segment_size = segment_size

    def split_code(self, code: str):
        """
        NEW: Real splitting function.
        Splits by empty lines OR fixed-size chunks.
        """
        lines = code.strip().split("\n")
        segments = []
        current = []

        for line in lines:
            if line.strip() == "":
                if current:
                    segments.append("\n".join(current))
                    current = []
            else:
                current.append(line)

            if len(current) >= self.segment_size:
                segments.append("\n".join(current))
                current = []

        if current:
            segments.append("\n".join(current))

        return segments

    def select_language(self, comfort_score: float) -> str:
        """
        Maps comfort values → languages.
        Tune thresholds as needed.
        """

        if comfort_score < 0.9:
            return "cpp"
        elif comfort_score < 1.2:
            return "rust"
        elif comfort_score < 1.5:
            return "go"
        else:
            return "java"

    def split(self, code: str):
        """
        Main entry: split into (segment_code, language)
        """

        print("[Splitter] Splitting code...")

        raw_segments = self.split_code(code)
        final_segments = []

        for seg in raw_segments:
            score = comfort_value(seg)
            lang = self.select_language(score)

            final_segments.append({
                "code": seg,
                "comfort": score,
                "language": lang
            })

        print(f"[Splitter] Generated {len(final_segments)} segments.")
        return final_segments
