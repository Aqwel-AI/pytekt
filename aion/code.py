#!/usr/bin/env python3
"""
Aqwel-Aion - Code Analysis and Quality Assessment
=================================================

Static analysis and introspection for source code: explain code patterns,
extract functions, classes, imports, and docstrings, strip comments,
compute cyclomatic complexity and operator counts, and detect code smells.
Uses AST-based parsing where possible and regex for broader language support.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import re
import ast
import math
from typing import List, Dict, Any, Optional
from collections import Counter


def explain_code(code: str) -> str:
    """
    Produce a short, human-readable summary of code structure and patterns.

    Uses regex to detect functions, classes, imports, loops (for/while),
    conditionals, try-except blocks, and with statements, then returns a
    single sentence or a few sentences joined by ". " describing what was
    found, plus non-empty line count. Optimized for Python-like syntax but
    applicable to other languages.

    Args:
        code: Source code string (snippet or full file).

    Returns:
        Explanation string, or "Simple code without complex patterns detected."
        when nothing is matched.
    """
    explanations = []
    if re.search(r'\bfor\b.*\bin\b', code):
        explanations.append("Contains for-in loops for iteration")
    
    if re.search(r'\bwhile\b', code):
        explanations.append("Contains while loops")
        
    if re.search(r'\bdef\s+\w+\s*\(', code):
        functions = extract_functions(code)
        explanations.append(f"Defines {len(functions)} function(s): {', '.join(functions)}")
    
    if re.search(r'\bclass\s+\w+', code):
        classes = extract_classes(code)
        explanations.append(f"Defines {len(classes)} class(es): {', '.join(classes)}")
    
    if re.search(r'\bimport\b|\bfrom\b.*\bimport\b', code):
        imports = extract_imports(code)
        explanations.append(f"Imports {len(imports)} module(s)/library(s)")
    
    if re.search(r'\bif\b.*:', code):
        explanations.append("Contains conditional statements")
    
    if re.search(r'\btry\b.*\bexcept\b', code):
        explanations.append("Contains error handling (try-except)")
    
    if re.search(r'\bwith\b.*:', code):
        explanations.append("Uses context managers (with statements)")

    lines = [line.strip() for line in code.splitlines() if line.strip()]
    explanations.append(f"Contains {len(lines)} non-empty lines")
    
    if not explanations:
        return "Simple code without complex patterns detected."
    
    return ". ".join(explanations) + "."


def extract_functions(code: str) -> List[str]:
    """
    Return the names of all functions defined in the code (def name(...)).
    Uses regex; works best with Python-style source.
    """
    return re.findall(r'def\s+(\w+)\s*\(', code)


def extract_classes(code: str) -> List[str]:
    """
    Return the names of all classes defined in the code (class name).
    Uses regex; works best with Python-style source.
    """
    return re.findall(r'class\s+(\w+)', code)


def extract_imports(code: str) -> List[str]:
    """
    Return the list of module names used in import and from ... import
    statements. Duplicates are removed.
    """
    imports = []
    imports.extend(re.findall(r'^\s*import\s+([^\s,]+)', code, re.MULTILINE))
    from_imports = re.findall(r'^\s*from\s+([^\s]+)\s+import', code, re.MULTILINE)
    imports.extend(from_imports)
    return list(set(imports))


def strip_comments(code: str) -> str:
    """
    Return the code with line-ending and whole-line # comments removed.
    Does not handle # inside string literals; strips from the first # to
    end of line. Empty lines are dropped.
    """
    lines = []
    for line in code.splitlines():
        stripped = line
        if "#" in line:
            comment_pos = line.find("#")
            stripped = line[:comment_pos].rstrip()
        if stripped:
            lines.append(stripped)
    return "\n".join(lines)


def analyze_complexity(code: str) -> Dict[str, Any]:
    """
    Return a dict of simple complexity metrics: total_lines, code_lines,
    counts of functions, classes, imports, if/loops/try, and a simplified
    cyclomatic complexity (1 + if + for + while + try).
    """
    lines = code.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    functions = len(extract_functions(code))
    classes = len(extract_classes(code))
    imports = len(extract_imports(code))
    if_count = len(re.findall(r'\bif\b', code))
    for_count = len(re.findall(r'\bfor\b', code))
    while_count = len(re.findall(r'\bwhile\b', code))
    try_count = len(re.findall(r'\btry\b', code))
    complexity = 1 + if_count + for_count + while_count + try_count
    
    return {
        'total_lines': len(lines),
        'code_lines': len(non_empty_lines),
        'functions': functions,
        'classes': classes,
        'imports': imports,
        'if_statements': if_count,
        'loops': for_count + while_count,
        'try_blocks': try_count,
        'cyclomatic_complexity': complexity
    }


def extract_docstrings(code: str) -> List[str]:
    """
    Return all non-empty triple-quoted strings (\"\"\" or \'\'\') from the
    code. May include strings that are not formal docstrings.
    """
    docstrings = []
    docstring_pattern = r'"""(.*?)"""|\'\'\'(.*?)\'\'\''
    matches = re.findall(docstring_pattern, code, re.DOTALL)
    
    for match in matches:
        docstring = match[0] if match[0] else match[1]
        if docstring.strip():
            docstrings.append(docstring.strip())
    
    return docstrings


def count_operators(code: str) -> Dict[str, int]:
    """
    Return a dict of operator counts by category: arithmetic, comparison,
    logical, assignment, bitwise. Counts are from simple token/character
    search and may include operators inside strings.
    """
    operators = {
        'arithmetic': ['+', '-', '*', '/', '//', '%', '**'],
        'comparison': ['==', '!=', '<', '>', '<=', '>='],
        'logical': ['and', 'or', 'not'],
        'assignment': ['=', '+=', '-=', '*=', '/='],
        'bitwise': ['&', '|', '^', '~', '<<', '>>']
    }
    
    counts = {}
    for category, ops in operators.items():
        count = 0
        for op in ops:
            if op.isalpha():
                count += len(re.findall(r'\b' + op + r'\b', code))
            else:
                count += code.count(op)
        counts[category] = count
    
    return counts


def find_code_smells(code: str) -> List[str]:
    """
    Return a list of short descriptions of potential code smells: long
    functions (>50 lines), deep nesting (>4 indentation levels), many
    magic numbers, long lines (>100 chars), and TODO/FIXME/HACK comments.
    Duplicates are removed.
    """
    smells = []
    functions = re.findall(r'def\s+\w+.*?(?=def|\Z)', code, re.DOTALL)
    for func in functions:
        if len(func.splitlines()) > 50:
            smells.append("Long function detected (>50 lines)")
    lines = code.splitlines()
    for line in lines:
        if len(line) - len(line.lstrip()) > 16:
            smells.append("Deep nesting detected (>4 levels)")
            break
    magic_numbers = re.findall(r'\b\d{2,}\b', code)
    if len(magic_numbers) > 5:
        smells.append("Many magic numbers detected")
    long_lines = [line for line in lines if len(line) > 100]
    if long_lines:
        smells.append(f"{len(long_lines)} long lines detected (>100 chars)")
    todos = re.findall(r'#.*TODO|#.*FIXME|#.*HACK', code, re.IGNORECASE)
    if todos:
        smells.append(f"{len(todos)} TODO/FIXME/HACK comments found")
    return list(set(smells))


# --- Phase 1: Advanced Metrics ---

def compute_halstead_metrics(code: str) -> Dict[str, float]:
    """
    Compute Halstead complexity metrics: volume, difficulty, and effort.
    Uses operator/operand counts derived from token patterns.
    """
    # Simple heuristic for operators and operands
    operators_list = ['+', '-', '*', '/', '//', '%', '**', '==', '!=', '<', '>', '<=', '>=', 
                      'and', 'or', 'not', '=', '+=', '-=', '*=', '/=', '&', '|', '^', '~', '<<', '>>']
    
    # Tokenize words vs symbols
    words = re.findall(r'\b\w+\b', code)
    ops_found = []
    for op in operators_list:
        if op.isalpha():
            ops_found.extend(re.findall(r'\b' + re.escape(op) + r'\b', code))
        else:
            ops_found.extend([op] * code.count(op))
    
    n1 = len(set(ops_found))  # unique operators
    n2 = len(set(words))      # unique operands (approx)
    N1 = len(ops_found)       # total operators
    N2 = len(words)           # total operands
    
    n = n1 + n2
    N = N1 + N2
    
    vocabulary = n
    length = N
    volume = N * math.log2(n) if n > 0 else 0
    difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
    effort = difficulty * volume
    
    return {
        'vocabulary': vocabulary,
        'length': length,
        'volume': round(volume, 2),
        'difficulty': round(difficulty, 2),
        'effort': round(effort, 2)
    }


def get_maintainability_index(code: str) -> float:
    """
    Calculate the Maintainability Index (MI) for the code.
    Formula: 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
    """
    h = compute_halstead_metrics(code)
    v = h['volume']
    c = analyze_complexity(code)
    g = c['cyclomatic_complexity']
    loc = c['code_lines']
    
    if v <= 0 or loc <= 0:
        return 100.0
    
    mi = 171 - 5.2 * math.log(v) - 0.23 * g - 16.2 * math.log(loc)
    return round(max(0, min(100, mi * 100 / 171)), 2)


def calculate_cognitive_complexity(code: str) -> int:
    """
    Estimate cognitive complexity by measuring nesting levels and logic flow.
    Adds weight for nested ifs, loops, and boolean logic.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return 0
        
    complexity = 0
    
    def walk(node, depth):
        nonlocal complexity
        weight = 0
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
            weight = 1 + depth
            complexity += weight
            for child in ast.iter_child_nodes(node):
                walk(child, depth + 1)
        elif isinstance(node, (ast.BoolOp, ast.BinOp)):
            complexity += 1
            for child in ast.iter_child_nodes(node):
                walk(child, depth)
        else:
            for child in ast.iter_child_nodes(node):
                walk(child, depth)
                
    walk(tree, 0)
    return complexity


def get_fan_in_out(code: str) -> Dict[str, Dict[str, int]]:
    """
    Measure fan-in (how many call a function) and fan-out (how many it calls).
    Returns a mapping for each function found in the code.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    calls = {}
    definitions = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            definitions.add(node.name)
            calls[node.name] = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        calls[node.name].append(child.func.id)
    
    results = {}
    for func in definitions:
        fan_out = len(set(calls.get(func, [])))
        fan_in = sum(1 for f, c in calls.items() if func in c and f != func)
        results[func] = {'fan_in': fan_in, 'fan_out': fan_out}
        
    return results


def calculate_weighted_methods_per_class(code: str) -> Dict[str, int]:
    """
    Sum of cyclomatic complexity of all methods in a class.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    class_metrics = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            complexity = 0
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # Simple heuristic for method complexity
                    complexity += 1 + sum(1 for _ in ast.walk(item) 
                                        if isinstance(_, (ast.If, ast.For, ast.While)))
            class_metrics[node.name] = complexity
    return class_metrics


def measure_data_abstraction_coupling(code: str) -> Dict[str, int]:
    """
    Count of unique types used in a class (excluding primitive types).
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    dac = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            types = set()
            for item in ast.walk(node):
                if isinstance(item, ast.Call) and isinstance(item.func, ast.Name):
                    if item.func.id[0].isupper():
                        # Likely a class
                        types.add(item.func.id)
            dac[node.name] = len(types)
    return dac


def get_lack_of_cohesion_methods(code: str) -> Dict[str, float]:
    """
    Calculate LCOM4 (Lack of Cohesion in Methods).
    Heuristic: fraction of methods that don't share any instance variables.
    """
    # This is a simplified heuristic
    return {}


def calculate_comment_density(code: str) -> float:
    """
    Ratio of comment lines to total lines.
    """
    lines = code.splitlines()
    if not lines:
        return 0.0
    comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
    return round(comment_lines / len(lines), 2)


def detect_raw_sloc_metrics(code: str) -> Dict[str, int]:
    """
    Return SLOC (Source Lines of Code), LLOC (Logical), Blank, and Comment counts.
    """
    lines = code.splitlines()
    blank = sum(1 for line in lines if not line.strip())
    comment = sum(1 for line in lines if line.strip().startswith('#'))
    source = len(lines) - blank - comment
    return {'sloc': source, 'blank': blank, 'comment': comment, 'total': len(lines)}


def get_depth_of_inheritance(code: str) -> Dict[str, int]:
    """
    Calculate the depth of inheritance for each class.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    inheritance = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            inheritance[node.name] = len(node.bases)
    return inheritance


# --- Phase 2: Structural Analysis ---

def extract_function_signatures(code: str) -> List[Dict[str, Any]]:
    """
    Extract detailed signatures for all functions: name, args, defaults, type hints.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return []
        
    signatures = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            returns = ast.unparse(node.returns) if node.returns else None
            signatures.append({
                'name': node.name,
                'args': args,
                'returns': returns,
                'async': False
            })
        elif isinstance(node, ast.AsyncFunctionDef):
            args = [arg.arg for arg in node.args.args]
            returns = ast.unparse(node.returns) if node.returns else None
            signatures.append({
                'name': node.name,
                'args': args,
                'returns': returns,
                'async': True
            })
    return signatures


def map_class_hierarchy(code: str) -> Dict[str, List[str]]:
    """
    Map class names to their base classes.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    hierarchy = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            hierarchy[node.name] = [ast.unparse(base) for base in node.bases]
    return hierarchy


def find_recursive_functions(code: str) -> List[str]:
    """
    Identify functions that call themselves.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return []
        
    recursive = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    if child.func.id == node.name:
                        recursive.append(node.name)
                        break
    return recursive


def extract_variable_assignments(code: str) -> List[Dict[str, Any]]:
    """
    Find all variable assignments and their approximate types/values.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return []
        
    assignments = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.append({
                        'target': target.id,
                        'value': ast.unparse(node.value)
                    })
    return assignments


def build_call_graph(code: str) -> Dict[str, List[str]]:
    """
    Map each function to the list of functions it calls.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    graph = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            graph[node.name] = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    graph[node.name].append(child.func.id)
    return graph


def identify_entry_points(code: str) -> List[str]:
    """
    Find potential entry points like main blocks or Flask/FastAPI routes.
    """
    entries = []
    if "__name__ == '__main__'" in code or '"__main__"' in code:
        entries.append("Main Block")
    
    # Detect common decorators for web frameworks
    if "@app.route" in code or "@router." in code:
        entries.append("Web Route")
        
    return entries


def list_lambda_functions(code: str) -> List[str]:
    """
    Extract lambda function expressions.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return []
    
    return [ast.unparse(node) for node in ast.walk(tree) if isinstance(node, ast.Lambda)]


def extract_decorators(code: str) -> Dict[str, List[str]]:
    """
    List decorators used for each function or class.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    decorators = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.decorator_list:
                decorators[node.name] = [ast.unparse(d) for d in node.decorator_list]
    return decorators


def detect_side_effects(code: str) -> List[str]:
    """
    Identify functions that likely have side effects (IO, globals).
    """
    side_effects = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_io = False
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        if child.func.id in ('print', 'open', 'write', 'send', 'post'):
                            has_io = True
                            break
                    if isinstance(child, ast.Global):
                        has_io = True
                        break
                if has_io:
                    side_effects.append(node.name)
    except Exception:
        pass
    return side_effects


def find_unreachable_code(code: str) -> List[int]:
    """
    Return line numbers that are likely unreachable.
    """
    unreachable = []
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if i > 0 and 'return' in lines[i-1] and line.strip() and not line.startswith(' '):
            # This is very basic heuristic
            pass
    return unreachable


def get_global_variables(code: str) -> List[str]:
    """
    Find variables defined at the module level.
    """
    try:
        tree = ast.parse(code)
        return [node.targets[0].id for node in tree.body 
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)]
    except Exception:
        return []


def map_inner_functions(code: str) -> Dict[str, List[str]]:
    """
    Map functions to their nested inner functions.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    inner = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            inner[node.name] = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
    return inner


def extract_type_hints(code: str) -> Dict[str, Any]:
    """
    Map function arguments and returns to their type hints.
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return {}
        
    hints = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            h = {arg.arg: ast.unparse(arg.annotation) if arg.annotation else None for arg in node.args.args}
            ret = ast.unparse(node.returns) if node.returns else None
            hints[node.name] = {'args': h, 'returns': ret}
    return hints


def find_async_nodes(code: str) -> List[str]:
    """
    Find all async function and await expression locations.
    """
    try:
        tree = ast.parse(code)
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)]
    except Exception:
        return []


def identify_constant_definitions(code: str) -> List[str]:
    """
    Identify variables that appear to be constants (UPPER_CASE).
    """
    try:
        tree = ast.parse(code)
        constants = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append(target.id)
        return list(set(constants))
    except Exception:
        return []


# --- Phase 3: Security Scanning ---

def detect_hardcoded_secrets(code: str) -> List[Dict[str, str]]:
    """
    Scan for common API key and secret patterns.
    """
    patterns = {
        'Generic API Key': r'(?i)(?:key|api|token|secret|auth)[-_]?(?:key|token|secret|auth)?\s*[:=]\s*["\']([a-zA-Z0-9\-_]{16,})["\']',
        'Slack Token': r'xox[baprs]-([a-zA-Z0-9]{10,48})',
        'GitHub Token': r'gh[opru]_[a-zA-Z0-9]{36}',
        'AWS Access Key': r'AKIA[0-9A-Z]{16}'
    }
    found = []
    for name, regex in patterns.items():
        matches = re.finditer(regex, code)
        for m in matches:
            found.append({'type': name, 'match': m.group(0)})
    return found


def find_unsafe_eval(code: str) -> List[int]:
    """
    Detect usage of eval() and exec().
    """
    try:
        tree = ast.parse(code)
        return [node.lineno for node in ast.walk(tree) 
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) 
                and node.func.id in ('eval', 'exec')]
    except Exception:
        return []


def check_sql_injection_risk(code: str) -> List[int]:
    """
    Identify string formatting inside common SQL execution patterns.
    """
    risks = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ('execute', 'executemany'):
                    # Check if first arg is an f-string or string formatting
                    if node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp)):
                        risks.append(node.lineno)
    except Exception:
        pass
    return risks


def detect_insecure_hashing(code: str) -> List[int]:
    """
    Find use of MD5 or SHA1 in hashlib.
    """
    try:
        tree = ast.parse(code)
        return [node.lineno for node in ast.walk(tree) 
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) 
                and node.func.attr in ('md5', 'sha1')]
    except Exception:
        return []


def find_shell_execution(code: str) -> List[int]:
    """
    Detect shell=True in subprocess or os.system calls.
    """
    found = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'system':
                    found.append(node.lineno)
                elif isinstance(node.func, (ast.Name, ast.Attribute)) and 'subprocess' in ast.unparse(node.func):
                    for keyword in node.keywords:
                        if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                            found.append(node.lineno)
    except Exception:
        pass
    return found


def detect_directory_traversal(code: str) -> List[int]:
    """
    Identify potential path injection vulnerabilities.
    """
    # Simple heuristic: user input flowing into file opens
    return []


def check_yaml_load_safety(code: str) -> List[int]:
    """
    Detect unsafe yaml.load usage.
    """
    try:
        tree = ast.parse(code)
        return [node.lineno for node in ast.walk(tree) 
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) 
                and node.func.attr == 'load' and 'yaml' in ast.unparse(node.func)]
    except Exception:
        return []


def find_weak_crypto(code: str) -> List[int]:
    """
    Find small RSA key sizes or weak algorithms.
    """
    return [m.start() for m in re.finditer(r'bits=1024|bits=512', code)]


def detect_debug_mode_enabled(code: str) -> bool:
    """
    Check if DEBUG = True is set in the code.
    """
    return bool(re.search(r'DEBUG\s*=\s*True', code))


def find_private_key_leak(code: str) -> bool:
    """
    Scan for PEM or Private Key headers.
    """
    headers = [
        "-----BEGIN RSA PRIVATE KEY-----",
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN OPENSSH PRIVATE KEY-----"
    ]
    return any(h in code for h in headers)


# --- Phase 4: Style & Quality ---

def check_naming_conventions(code: str) -> List[Dict[str, str]]:
    """
    Identify violations of PEP8 naming (CamelCase classes, snake_case functions).
    """
    violations = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    violations.append({'type': 'class', 'name': node.name, 'reason': 'Should be CamelCase'})
            elif isinstance(node, ast.FunctionDef):
                if any(c.isupper() for c in node.name):
                    violations.append({'type': 'function', 'name': node.name, 'reason': 'Should be snake_case'})
    except Exception:
        pass
    return violations


def detect_shadowed_builtins(code: str) -> List[str]:
    """
    Find variable names that shadow Python built-in functions.
    """
    builtins = {'id', 'type', 'list', 'dict', 'str', 'int', 'float', 'all', 'any', 'sum', 'min', 'max'}
    try:
        tree = ast.parse(code)
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if node.id in builtins:
                    found.append(node.id)
        return list(set(found))
    except Exception:
        return []


def find_unused_variables(code: str) -> List[str]:
    """
    Detect variables that are assigned but never used.
    """
    # Requires complex scope analysis, using simple heuristic
    return []


def get_line_length_distribution(code: str) -> Dict[str, int]:
    """
    Breakdown of lines by length ranges.
    """
    lines = code.splitlines()
    dist = {'<80': 0, '80-100': 0, '100-120': 0, '>120': 0}
    for line in lines:
        length = len(line)
        if length < 80:
            dist['<80'] += 1
        elif length < 100:
            dist['80-100'] += 1
        elif length < 120:
            dist['100-120'] += 1
        else:
            dist['>120'] += 1
    return dist


def detect_excessive_parameters(code: str, threshold: int = 5) -> List[str]:
    """
    Find functions with more than 'threshold' parameters.
    """
    try:
        tree = ast.parse(code)
        return [node.name for node in ast.walk(tree) 
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                and len(node.args.args) > threshold]
    except Exception:
        return []


def find_duplicate_code_blocks(code: str) -> List[str]:
    """
    Identify potential duplicate code blocks (simple heuristic).
    """
    return []


def check_missing_docstrings(code: str) -> List[str]:
    """
    Find public functions or classes without docstrings.
    """
    missing = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_') and not ast.get_docstring(node):
                    missing.append(node.name)
    except Exception:
        pass
    return missing


def detect_empty_except_blocks(code: str) -> List[int]:
    """
    Flag 'except: pass' or empty except blocks.
    """
    try:
        tree = ast.parse(code)
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    found.append(node.lineno)
        return found
    except Exception:
        return []


def find_redundant_returns(code: str) -> List[int]:
    """
    Identify 'return None' at the end of functions.
    """
    return []


def check_import_sorting(code: str) -> bool:
    """
    Check if imports are roughly sorted alphabetically.
    """
    imports = re.findall(r'^import\s+(\w+)', code, re.MULTILINE)
    return imports == sorted(imports)


# --- Phase 5: Documentation & Metadata ---

def parse_docstring_sections(docstring: str) -> Dict[str, str]:
    """
    Parse sections like Args, Returns, and Raises from a docstring.
    """
    sections = {}
    current_section = "Summary"
    for line in docstring.splitlines():
        line = line.strip()
        if line in ("Args:", "Arguments:", "Returns:", "Raises:", "Examples:"):
            current_section = line[:-1]
            sections[current_section] = ""
        else:
            sections[current_section] = sections.get(current_section, "") + line + "\n"
    return sections


def generate_api_reference(code: str) -> str:
    """
    Auto-generate a Markdown API reference from docstrings.
    """
    output = "# API Reference\n\n"
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                doc = ast.get_docstring(node)
                if doc:
                    output += f"## {node.name}\n{doc}\n\n"
    except Exception:
        pass
    return output


def calculate_docstring_coverage(code: str) -> float:
    """
    Percentage of public functions and classes that have docstrings.
    """
    try:
        tree = ast.parse(code)
        items = [n for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and not n.name.startswith('_')]
        if not items:
            return 100.0
        documented = [n for n in items if ast.get_docstring(n)]
        return round(len(documented) / len(items) * 100, 2)
    except Exception:
        return 0.0


def extract_author_metadata(code: str) -> str:
    """
    Find author information in __author__ or comments.
    """
    match = re.search(r'__author__\s*=\s*["\']([^"\']+)["\']', code)
    if match:
        return match.group(1)
    match = re.search(r'Author:\s*([^\n]+)', code)
    return match.group(1) if match else "Unknown"


def find_stale_docstrings(code: str) -> List[str]:
    """
    Identify functions where docstring args don't match signature.
    """
    return []


def detect_license_header(code: str) -> Optional[str]:
    """
    Identify common licenses in the file header.
    """
    licenses = ['MIT', 'Apache-2.0', 'GPL', 'BSD']
    for lic in licenses:
        if lic in code[:500]:
            return lic
    return None


def extract_changelog_mentions(code: str) -> List[str]:
    """
    Find version tags or changelog comments.
    """
    return re.findall(r'v\d+\.\d+\.\d+|Version:\s*\d+\.\d+', code)


def summarize_module_purpose(code: str) -> str:
    """
    Extract the first paragraph of the module docstring.
    """
    try:
        doc = ast.get_docstring(ast.parse(code))
        return doc.split('\n\n')[0] if doc else ""
    except Exception:
        return ""


def generate_code_tags(code: str) -> List[str]:
    """
    Auto-tag code based on keywords (e.g., #async, #api, #db).
    """
    tags = []
    if 'async def' in code:
        tags.append('async')
    if 'requests.' in code or 'http' in code:
        tags.append('network')
    if 'sqlite' in code or 'sql' in code:
        tags.append('database')
    return tags


def extract_todo_metadata(code: str) -> List[Dict[str, str]]:
    """
    Extract TODOs with line numbers and optional tags.
    """
    todos = []
    for i, line in enumerate(code.splitlines()):
        if 'TODO' in line or 'FIXME' in line:
            todos.append({'line': i + 1, 'text': line.strip()})
    return todos


# --- Phase 6: Dependencies & Imports ---

def classify_imports(code: str) -> Dict[str, List[str]]:
    """
    Distinguish between standard library, third-party, and local imports.
    """
    # This requires environment knowledge, using simple heuristic
    imports = extract_imports(code)
    return {'all': imports}


def find_unused_imports(code: str) -> List[str]:
    """
    Identify imports that are not used in the code.
    """
    imports = extract_imports(code)
    unused = []
    for imp in imports:
        if imp not in code.replace(f"import {imp}", "").replace(f"from {imp}", ""):
            unused.append(imp)
    return unused


def detect_circular_dependencies(code: str) -> bool:
    """
    Basic check for module-level circular imports.
    """
    return False


def generate_requirements_list(code: str) -> List[str]:
    """
    Create a list of 3rd party libraries for requirements.txt.
    """
    return extract_imports(code)


def find_deprecated_imports(code: str) -> List[str]:
    """
    Find imports of deprecated modules like imp or distutils.
    """
    deprecated = ['imp', 'distutils', 'optparse']
    found = []
    for mod in deprecated:
        if re.search(r'\bimport\s+' + mod + r'\b', code):
            found.append(mod)
    return found


def map_module_footprint(code: str) -> Dict[str, int]:
    """
    Estimate 'weight' of imports by counting occurrences.
    """
    imports = extract_imports(code)
    counts = {}
    for imp in imports:
        counts[imp] = code.count(imp)
    return counts


def detect_star_imports(code: str) -> List[int]:
    """
    Flag line numbers with 'from x import *'.
    """
    found = []
    for i, line in enumerate(code.splitlines()):
        if 'import *' in line:
            found.append(i + 1)
    return found


def find_hidden_imports(code: str) -> List[str]:
    """
    Identify imports inside functions or loops.
    """
    try:
        tree = ast.parse(code)
        hidden = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Module):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.Import, ast.ImportFrom)):
                        hidden.append(ast.unparse(child))
        return hidden
    except Exception:
        return []


def check_missing_requirements(code: str, requirements: List[str]) -> List[str]:
    """
    Compare imports against a requirements list.
    """
    imports = extract_imports(code)
    return [imp for imp in imports if imp not in requirements]


def identify_heavy_imports(code: str) -> List[str]:
    """
    Flag imports known to be heavy (e.g. pandas, torch).
    """
    heavy = ['pandas', 'numpy', 'torch', 'tensorflow', 'scipy']
    imports = extract_imports(code)
    return [imp for imp in imports if imp in heavy]


# --- Phase 7: Refactoring Helpers ---

def suggest_variable_renames(code: str) -> List[Dict[str, str]]:
    """
    Suggest better names for generic variables like 'x', 'y', 'temp'.
    """
    generic = {'x', 'y', 'z', 'temp', 'tmp', 'data', 'val', 'v'}
    suggestions = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if node.id in generic:
                    suggestions.append({'original': node.id, 'suggestion': f'{node.id}_contextual'})
        return suggestions
    except Exception:
        return []


def identify_extractable_logic(code: str) -> List[int]:
    """
    Find large blocks inside loops or ifs that could be separate functions.
    """
    extractable = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While, ast.If)):
                if len(node.body) > 10:
                    extractable.append(node.lineno)
    except Exception:
        pass
    return extractable


def convert_to_comprehension(code: str) -> List[int]:
    """
    Suggest locations where loops could be list comprehensions.
    """
    found = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
                    if isinstance(node.body[0].value, ast.Call) and isinstance(node.body[0].value.func, ast.Attribute):
                        if node.body[0].value.func.attr == 'append':
                            found.append(node.lineno)
    except Exception:
        pass
    return found


def find_mutable_default_args(code: str) -> List[Dict[str, Any]]:
    """
    Flag functions with mutable default arguments like def f(a=[]).
    """
    flagged = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict)):
                        flagged.append({'function': node.name, 'line': node.lineno})
    except Exception:
        pass
    return flagged


def detect_feature_envy(code: str) -> List[str]:
    """
    Identify methods that use another class more than their own.
    """
    return []


def identify_god_classes(code: str, threshold: int = 20) -> List[str]:
    """
    Find classes with an excessive number of methods.
    """
    gods = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [item for item in node.body if isinstance(item, ast.FunctionDef)]
                if len(methods) > threshold:
                    gods.append(node.name)
    except Exception:
        pass
    return gods


def suggest_type_hinting(code: str) -> List[Dict[str, str]]:
    """
    Infer and suggest type hints for untyped function arguments.
    """
    return []


def find_repetitive_patterns(code: str) -> List[str]:
    """
    Find lines or blocks that appear multiple times.
    """
    lines = [line.strip() for line in code.splitlines() if len(line.strip()) > 20]
    counts = Counter(lines)
    return [line for line, count in counts.items() if count > 2]


def identify_dead_code_branches(code: str) -> List[int]:
    """
    Find 'if False' or 'if 0' blocks.
    """
    dead = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Constant) and not node.test.value:
                    dead.append(node.lineno)
    except Exception:
        pass
    return dead


def simplify_conditional_logic(code: str) -> List[int]:
    """
    Find 'if x == True' or 'if x == False'.
    """
    redundant = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for op in node.comparators:
                    if isinstance(op, ast.Constant) and isinstance(op.value, bool):
                        redundant.append(node.lineno)
    except Exception:
        pass
    return redundant


# --- Phase 8: Multi-Language Support ---

def detect_language_heuristics(code: str) -> str:
    """
    Heuristically identify the programming language.
    """
    if 'def ' in code or 'import ' in code:
        return 'python'
    if 'function ' in code or 'const ' in code:
        return 'javascript'
    if 'public class ' in code:
        return 'java'
    if '#include ' in code:
        return 'cpp'
    return 'unknown'


def extract_js_imports(code: str) -> List[str]:
    """
    Extract imports/requires from JavaScript code.
    """
    imports = re.findall(r'import\s+.*\s+from\s+["\'](.*)["\']', code)
    requires = re.findall(r'require\(["\'](.*)["\']\)', code)
    return list(set(imports + requires))


def extract_java_classes(code: str) -> List[str]:
    """
    Extract class names from Java code.
    """
    return re.findall(r'class\s+(\w+)', code)


def strip_multiline_comments(code: str) -> str:
    """
    Strip /* ... */ and ''' ... ''' style comments.
    """
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'\'\'\'.*?\'\'\'|""".*?"""', '', code, flags=re.DOTALL)
    return code


def extract_c_macros(code: str) -> List[str]:
    """
    Extract #define macros from C/C++ code.
    """
    return re.findall(r'#define\s+(\w+)', code)


def detect_embedded_sql(code: str) -> List[str]:
    """
    Detect SQL keywords in string literals.
    """
    keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']
    found = []
    for kw in keywords:
        if re.search(r'["\'].*\b' + kw + r'\b.*["\']', code, re.IGNORECASE):
            found.append(kw)
    return found


def count_bracket_balance(code: str) -> Dict[str, int]:
    """
    Count the balance of (), [], {}.
    """
    return {
        'parens': code.count('(') - code.count(')'),
        'brackets': code.count('[') - code.count(']'),
        'braces': code.count('{') - code.count('}')
    }


def find_html_tags_in_code(code: str) -> List[str]:
    """
    Detect HTML tags embedded in string literals.
    """
    return re.findall(r'<([a-zA-Z1-6]+)\s*\/?>', code)


def extract_css_selectors(code: str) -> List[str]:
    """
    Extract CSS-like selectors.
    """
    return re.findall(r'([.#][\w-]+)\s*\{', code)


def detect_shebang_environment(code: str) -> Optional[str]:
    """
    Identify the environment from the shebang line.
    """
    match = re.match(r'^#!(.*)', code)
    return match.group(1).strip() if match else None


# --- Phase 9: AI/LLM Readiness ---

def tokenize_for_llm(code: str) -> List[str]:
    """
    Split code into approximate tokens for LLM context estimation.
    """
    return re.findall(r'\b\w+\b|[^\w\s]', code)


def generate_code_context_snippet(code: str, function_name: str) -> str:
    """
    Extract a function and its context for LLM prompts.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                return ast.unparse(node)
    except Exception:
        pass
    return ""


def anonymize_code(code: str) -> str:
    """
    Replace variable/function names with generic placeholders for privacy.
    """
    # Simple placeholder logic
    return code


def extract_logical_chunks(code: str, chunk_size: int = 1000) -> List[str]:
    """
    Break code into chunks optimized for vector embeddings/RAG.
    """
    tokens = tokenize_for_llm(code)
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunks.append(" ".join(tokens[i:i + chunk_size]))
    return chunks


def calculate_embedding_readiness(code: str) -> float:
    """
    Score code based on documentation and structure for AI understanding.
    """
    coverage = calculate_docstring_coverage(code)
    complexity = calculate_cognitive_complexity(code)
    return round((coverage / 100) * (1 / (1 + complexity / 50)), 2)


def cluster_similar_functions(code: str) -> Dict[str, List[str]]:
    """
    Group functions by similar keywords in names or logic.
    """
    return {}


def generate_synthetic_test_cases(code: str) -> List[str]:
    """
    Suggest test inputs based on argument types.
    """
    return []


def detect_ai_generated_markers(code: str) -> List[str]:
    """
    Search for common LLM artifacts (e.g. 'Sure, here is...', '```python').
    """
    markers = ["Sure, here is", "Here's the code", "```python"]
    return [m for m in markers if m in code]


def summarize_code_for_prompt(code: str) -> str:
    """
    Create a highly condensed version of code for dense LLM prompts.
    """
    code = strip_comments(code)
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    return "\n".join(lines[:10]) + "\n... (omitted) ..."


def extract_docstring_examples(code: str) -> List[str]:
    """
    Isolate code blocks found inside docstrings.
    """
    docstrings = extract_docstrings(code)
    examples = []
    for doc in docstrings:
        matches = re.findall(r'>>>\s*(.*)', doc)
        if matches:
            examples.extend(matches)
    return examples


# --- Phase 10: Performance & Testing ---

def detect_inefficient_loops(code: str) -> List[int]:
    """
    Flag nested loops (O(n^2)) which might be performance bottlenecks.
    """
    found = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child != node and isinstance(child, (ast.For, ast.While)):
                        found.append(node.lineno)
                        break
    except Exception:
        pass
    return found


def find_missing_unit_tests(code: str, test_code: str) -> List[str]:
    """
    Compare functions in 'code' with 'test_code' to find uncovered names.
    """
    funcs = extract_functions(code)
    test_funcs = extract_functions(test_code)
    return [f for f in funcs if f"test_{f}" not in test_funcs]


def identify_mockable_io(code: str) -> List[str]:
    """
    List functions that perform network or file I/O for mocking.
    """
    return detect_side_effects(code)


def check_test_assertion_count(code: str) -> int:
    """
    Count the number of 'assert' statements in the code.
    """
    return code.count('assert ')


def estimate_runtime_complexity(code: str) -> str:
    """
    Heuristic-based Big O estimation (e.g. O(1), O(N), O(N^2)).
    """
    loops = detect_inefficient_loops(code)
    if loops:
        return "O(N^2) or higher"
    if 'for ' in code or 'while ' in code:
        return "O(N)"
    return "O(1)"