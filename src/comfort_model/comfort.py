# src/comfort_model/comfort.py

import re

def count_loops(code: str) -> int:
    """
    Count loop constructs: for, while.
    """
    return len(re.findall(r'\bfor\b|\bwhile\b', code))


def count_recursions_and_defs(code: str) -> int:
    """
    Count function definitions as a proxy for structural complexity.
    """
    return len(re.findall(r'\bdef\b', code))


def compute_familiarity(code: str) -> float:
    """
    Compute 'familiarity score' based on pythonic constructs.
    
    Math:
        F_f = 1 + Sum(pattern_weights)
    """
    patterns = {
        r'\blen\(': 0.3,
        r'\bin\b': 0.3,
        r'print\(': 0.3,
        r'\[.*for.*in.*\]': 0.3,  # list comprehension
        r'lambda': 0.3,
        r'\benumerate\(': 0.3,
        r'\bzip\(': 0.3,
        r'\bmap\(': 0.2,
        r'\bfilter\(': 0.2,
    }

    familiarity = 1.0
    for pattern, weight in patterns.items():
        if re.search(pattern, code):
            familiarity += weight

    return familiarity


def compute_runtime_cost(code: str) -> float:
    """
    Runtime cost estimates complexity.
    
    Math:
        C_r = 1 + 0.5*L + 0.25*R
    Where:
        L = loop count
        R = recursion/definition count
    """
    L = count_loops(code)
    R = count_recursions_and_defs(code)

    return 1 + 0.5 * L + 0.25 * R


def comfort_value(code: str) -> float:
    """
    Main function: computes the final comfort score.

    Math:
        V_c = F_f / C_r
    """
    F_f = compute_familiarity(code)
    C_r = compute_runtime_cost(code)

    if C_r == 0:
        return 1.0  # fallback safety

    return F_f / C_r


def comfort_report(code: str) -> dict:
    """
    Returns a structured breakdown for debugging or analysis.
    """
    F_f = compute_familiarity(code)
    C_r = compute_runtime_cost(code)
    V_c = comfort_value(code)

    return {
        "comfort_value": V_c,
        "familiarity_score": F_f,
        "runtime_cost": C_r,
    }
