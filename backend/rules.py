from __future__ import annotations

import re
from typing import Any, Dict


VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")
ASSIGN_PATTERN = re.compile(r"(?<![<>!=])=(?!=)")
NUMERIC_EQ_PATTERN = re.compile(r"==\s*(\d+)")


def _prepare_expression(expr: str) -> str:
    def replace_var(match: re.Match[str]) -> str:
        var_name = match.group(1)
        # Convert to string for comparison to handle both int and string values
        return f"str(context.get('{var_name}', ''))"

    prepared = VAR_PATTERN.sub(replace_var, expr)
    prepared = ASSIGN_PATTERN.sub("==", prepared)
    # No need for NUMERIC_EQ_PATTERN since we're now comparing strings
    return prepared


def evaluate_relevant(expr: str, context: Dict[str, Any]) -> bool:
    if not expr or expr.lower() == "nan":
        return True
    prepared = _prepare_expression(expr)
    try:
        # Include str and selected in locals for ODK expressions
        # selected(value, choice) returns True if value equals choice (used for single-select)
        return bool(eval(prepared, {"__builtins__": {}}, {
            "context": context, 
            "str": str,
            "selected": lambda v, k: str(v) == str(k)
        }))
    except Exception:
        return False


def satisfies_constraint(value: Any, expr: str) -> bool:
    if not expr or expr.lower() == "nan":
        return True
    
    # Replace . with value ensuring we match the dot variable only
    # Strategy: Replace . comparison operators with value comparison operators
    # Examples: .>= -> value>=, .< -> value<
    
    safe_expr = expr
    
    # Use regex to replace . followed by comparison operator
    # Pattern: dot, optional space, operator
    import re
    # Ops: >=, <=, >, <, =, !=
    # We replace ". op" with "value op"
    
    # Handle .>=, .<=, .>, .<, .=, .!= with flexible spacing
    safe_expr = re.sub(r'(?<!\w)\.\s*(>=|<=|>|<|!=|==|=)', r'value \1', safe_expr)
    
    # Also handle trailing dot if it's separate? (Not common in ODK)
    
    safe_expr = ASSIGN_PATTERN.sub("==", safe_expr)
    
    try:
        # Include regex search in eval context if needed for complex constraints (regex())
        # But for basics, just value
        return bool(eval(safe_expr, {"__builtins__": {}}, {"value": value, "selected": lambda v, k: str(k) == str(v)})) 
    except Exception:
        # If eval fails, assume True to generate data rather than failing simulation
        # Or False? Better False for strictness, but we want successful generation.
        # Given we generated the value with intent, let's log and pass?
        # No, better fix regex.
        return False
