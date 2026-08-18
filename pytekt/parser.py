#!/usr/bin/env python3
"""
PyTekt - Code Parser
=========================

Language detection, code parsing (Python AST and regex for other languages),
snippet extraction, basic syntax highlighting, token count, and code summary.
"""

import re
import ast
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

def detect_language(code: str) -> str:
    """Detect programming language from code using keywords and syntax patterns."""
    code_lower = code.lower()
    if any(k in code for k in ["def ", "import ", "from ", "class ", "if __name__"]):
        return "python"
    if any(k in code for k in ["function ", "const ", "let ", "var ", "console.log", "export ", "import "]):
        return "javascript" if "interface " not in code and "type " not in code else "typescript"
    if any(k in code for k in ["public class", "private ", "public ", "static void", "System.out"]):
        return "java"
    if any(k in code for k in ["#include", "int main", "printf", "cout", "namespace", "std::"]):
        return "cpp" if "cout" in code or "std::" in code else "c"
    if any(k in code for k in ["using System", "namespace ", "public class", "Console.WriteLine"]):
        return "csharp"
    if any(k in code for k in ["<?php", "echo ", "function ", "$_GET", "$_POST"]):
        return "php"
    if any(k in code for k in ["def ", "puts ", "require ", "class ", "attr_accessor"]):
        return "ruby"
    if any(k in code for k in ["package ", "func ", "import ", "fmt.Println", "var "]):
        return "go"
    if any(k in code for k in ["fn ", "let ", "mut ", "println!", "use ", "struct "]):
        return "rust"
    if any(k in code for k in ["import ", "func ", "var ", "let ", "print(", "class "]):
        return "swift"
    if any(k in code for k in ["fun ", "val ", "var ", "println(", "class ", "package "]):
        return "kotlin"
    if any(k in code for k in ["def ", "val ", "var ", "object ", "trait ", "case class"]):
        return "scala"
    if any(k in code for k in ["module ", "import ", "data ", "type ", "where", "let "]):
        return "haskell"
    if any(k in code for k in ["(defn ", "(def ", "(ns ", "(println ", "(let "]):
        return "clojure"
    if any(k in code for k in ["<-", "function(", "print(", "library(", "data.frame"]):
        return "r"
    if any(k in code for k in ["function ", "end", "disp(", "fprintf(", "plot("]):
        return "matlab"
    if any(k in code for k in ["function ", "println(", "using ", "import ", "struct "]):
        return "julia"
    if any(k in code for k in ["function ", "local ", "print(", "require ", "end"]):
        return "lua"
    if any(k in code for k in ["#!/usr/bin/perl", "my ", "print ", "use ", "sub "]):
        return "perl"
    if any(k in code for k in ["#!/bin/bash", "#!/bin/sh", "echo ", "export ", "source "]):
        return "bash"
    if any(k in code for k in ["Write-Host", "Get-", "Set-", "New-", "$env:"]):
        return "powershell"
    if "<html" in code_lower or "<!DOCTYPE" in code_lower:
        return "html"
    if "{" in code and ":" in code and (";" in code or "}" in code):
        return "css"
    if any(k in code_lower for k in ["select ", "insert ", "update ", "delete ", "create table"]):
        return "sql"
    if ":" in code and ("---" in code or "- " in code):
        return "yaml"
    if code.strip().startswith("{") or code.strip().startswith("["):
        return "json"
    if code.strip().startswith("<") and ">" in code:
        return "xml"
    if any(k in code for k in ["# ", "## ", "### ", "**", "*", "```"]):
        return "markdown"
    if any(k in code_lower for k in ["from ", "run ", "cmd ", "entrypoint ", "expose "]):
        return "dockerfile"
    if any(k in code for k in ["resource ", "data ", "variable ", "output ", "provider "]):
        return "terraform"
    if any(k in code for k in ["- hosts:", "tasks:", "handlers:", "vars:", "roles:"]):
        return "ansible"
    return "unknown"

def parse_code(code: str, language: str) -> Dict[str, Any]:
    """Parse code by language; returns dict with language, lines, characters, functions, classes, imports, complexity."""
    result = {
        "language": language,
        "lines": len(code.splitlines()),
        "characters": len(code),
        "functions": [],
        "classes": [],
        "imports": [],
        "comments": [],
        "complexity": 0,
    }
    if language == "python":
        result.update(parse_python_code(code))
    elif language == "javascript":
        result.update(parse_javascript_code(code))
    elif language == "java":
        result.update(parse_java_code(code))
    elif language == "cpp":
        result.update(parse_cpp_code(code))
    elif language == "csharp":
        result.update(parse_csharp_code(code))
    elif language == "go":
        result.update(parse_go_code(code))
    elif language == "rust":
        result.update(parse_rust_code(code))
    elif language == "swift":
        result.update(parse_swift_code(code))
    elif language == "kotlin":
        result.update(parse_kotlin_code(code))
    elif language == "php":
        result.update(parse_php_code(code))
    elif language == "ruby":
        result.update(parse_ruby_code(code))
    elif language == "sql":
        result.update(parse_sql_code(code))
    elif language == "html":
        result.update(parse_html_code(code))
    elif language == "css":
        result.update(parse_css_code(code))
    else:
        result.update(parse_generic_code(code))
    return result

def parse_python_code(code: str) -> Dict[str, Any]:
    """Parse Python code via AST; return functions, classes, imports, complexity."""
    try:
        tree = ast.parse(code)
        functions = []
        classes = []
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": len(node.args.args),
                    "decorators": len(node.decorator_list),
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append({
                    "module": getattr(node, "module", ""),
                    "names": [alias.name for alias in node.names],
                })
        complexity = len(functions) + len(classes) * 2
        return {"functions": functions, "classes": classes, "imports": imports, "complexity": complexity}
    except Exception:
        return {"error": "Failed to parse Python code"}

def parse_javascript_code(code: str) -> Dict[str, Any]:
    """Parse JavaScript via regex; return functions, classes, imports, complexity."""
    functions = re.findall(r'function\s+(\w+)|(\w+)\s*[:=]\s*function|(\w+)\s*[:=]\s*\([^)]*\)\s*=>', code)
    classes = re.findall(r'class\s+(\w+)', code)
    imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f[0] or f[1] or f[2], "type": "function"} for f in functions if any(f)],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": imp, "type": "import"} for imp in imports],
        "complexity": complexity,
    }

def parse_java_code(code: str) -> Dict[str, Any]:
    """Parse Java via regex; return methods, classes, imports, complexity."""
    functions = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*\{', code)
    classes = re.findall(r'class\s+(\w+)', code)
    imports = re.findall(r'import\s+([^;]+);', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f, "type": "method"} for f in functions],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": imp.strip(), "type": "import"} for imp in imports],
        "complexity": complexity,
    }

def parse_cpp_code(code: str) -> Dict[str, Any]:
    """Parse C++ via regex; return functions, classes, includes, complexity."""
    functions = re.findall(r'(?:void|int|string|double|float|bool|auto)\s+(\w+)\s*\([^)]*\)\s*\{', code)
    classes = re.findall(r'class\s+(\w+)', code)
    includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f, "type": "function"} for f in functions],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": inc, "type": "include"} for inc in includes],
        "complexity": complexity,
    }

def parse_csharp_code(code: str) -> Dict[str, Any]:
    """Parse C# via regex; return methods, classes, usings, complexity."""
    functions = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?(?:void|int|string|double|float|bool)\s+(\w+)\s*\([^)]*\)\s*\{', code)
    classes = re.findall(r'class\s+(\w+)', code)
    usings = re.findall(r'using\s+([^;]+);', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f, "type": "method"} for f in functions],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": use.strip(), "type": "using"} for use in usings],
        "complexity": complexity,
    }

def parse_go_code(code: str) -> Dict[str, Any]:
    """Parse Go via regex; return functions, packages, imports, complexity."""
    functions = re.findall(r'func\s+(\w+)\s*\([^)]*\)', code)
    packages = re.findall(r'package\s+(\w+)', code)
    imports = re.findall(r'import\s+[\'"]([^\'"]+)[\'"]', code)
    complexity = len(functions) + len(packages) * 2
    return {
        "functions": [{"name": f, "type": "function"} for f in functions],
        "packages": [{"name": p, "type": "package"} for p in packages],
        "imports": [{"module": imp, "type": "import"} for imp in imports],
        "complexity": complexity,
    }

def parse_rust_code(code: str) -> Dict[str, Any]:
    """Parse Rust via regex; return functions, structs, use statements, complexity."""
    functions = re.findall(r'fn\s+(\w+)\s*\([^)]*\)', code)
    structs = re.findall(r'struct\s+(\w+)', code)
    uses = re.findall(r'use\s+([^;]+);', code)
    complexity = len(functions) + len(structs) * 2
    return {
        "functions": [{"name": f, "type": "function"} for f in functions],
        "structs": [{"name": s, "type": "struct"} for s in structs],
        "imports": [{"module": use.strip(), "type": "use"} for use in uses],
        "complexity": complexity,
    }

def parse_swift_code(code: str) -> Dict[str, Any]:
    """Parse Swift via regex; return functions, classes, imports, complexity."""
    functions = re.findall(r'func\s+(\w+)\s*\([^)]*\)', code)
    classes = re.findall(r'class\s+(\w+)', code)
    imports = re.findall(r'import\s+(\w+)', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f, "type": "function"} for f in functions],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": imp, "type": "import"} for imp in imports],
        "complexity": complexity,
    }

def parse_kotlin_code(code: str) -> Dict[str, Any]:
    """Parse Kotlin via regex; return functions, classes, imports, complexity."""
    functions = re.findall(r'fun\s+(\w+)\s*\([^)]*\)', code)
    classes = re.findall(r'class\s+(\w+)', code)
    imports = re.findall(r'import\s+([^\s]+)', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f, "type": "function"} for f in functions],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": imp, "type": "import"} for imp in imports],
        "complexity": complexity,
    }

def parse_php_code(code: str) -> Dict[str, Any]:
    """Parse PHP via regex; return functions, classes, includes, complexity."""
    functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)', code)
    classes = re.findall(r'class\s+(\w+)', code)
    includes = re.findall(r'(?:include|require)(?:_once)?\s*[\'"]([^\'"]+)[\'"]', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f, "type": "function"} for f in functions],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": inc, "type": "include"} for inc in includes],
        "complexity": complexity,
    }

def parse_ruby_code(code: str) -> Dict[str, Any]:
    """Parse Ruby via regex; return methods, classes, requires, complexity."""
    functions = re.findall(r'def\s+(\w+)', code)
    classes = re.findall(r'class\s+(\w+)', code)
    requires = re.findall(r'require\s+[\'"]([^\'"]+)[\'"]', code)
    complexity = len(functions) + len(classes) * 2
    return {
        "functions": [{"name": f, "type": "method"} for f in functions],
        "classes": [{"name": c, "type": "class"} for c in classes],
        "imports": [{"module": req, "type": "require"} for req in requires],
        "complexity": complexity,
    }

def parse_sql_code(code: str) -> Dict[str, Any]:
    """Parse SQL via regex; return tables, selects, inserts, complexity."""
    tables = re.findall(r'CREATE\s+TABLE\s+(\w+)', code, re.IGNORECASE)
    selects = re.findall(r'SELECT\s+.*?FROM\s+(\w+)', code, re.IGNORECASE)
    inserts = re.findall(r'INSERT\s+INTO\s+(\w+)', code, re.IGNORECASE)
    complexity = len(tables) + len(selects) + len(inserts)
    return {
        "tables": [{"name": t, "type": "table"} for t in tables],
        "queries": [{"name": s, "type": "select"} for s in selects],
        "operations": [{"name": i, "type": "insert"} for i in inserts],
        "complexity": complexity,
    }

def parse_html_code(code: str) -> Dict[str, Any]:
    """Parse HTML via regex; return tags, div count, form count, complexity."""
    tags = re.findall(r'<(\w+)', code)
    divs = re.findall(r'<div[^>]*>', code)
    forms = re.findall(r'<form[^>]*>', code)
    complexity = len(tags) + len(divs) + len(forms)
    return {
        "tags": [{"name": tag, "type": "tag"} for tag in tags],
        "divs": len(divs),
        "forms": len(forms),
        "complexity": complexity,
    }

def parse_css_code(code: str) -> Dict[str, Any]:
    """Parse CSS via regex; return selectors, properties, complexity."""
    selectors = re.findall(r'([.#]?\w+)\s*\{', code)
    properties = re.findall(r'(\w+)\s*:', code)
    complexity = len(selectors) + len(properties)
    return {
        "selectors": [{"name": sel, "type": "selector"} for sel in selectors],
        "properties": [{"name": prop, "type": "property"} for prop in properties],
        "complexity": complexity,
    }

def parse_generic_code(code: str) -> Dict[str, Any]:
    """Basic parse for unknown languages: comment count and simple complexity."""
    lines = code.splitlines()
    comments = [line for line in lines if line.strip().startswith(("#", "//", "/*", "*", "*/"))]
    complexity = len(lines) // 10
    return {"comments": len(comments), "complexity": complexity}

def extract_snippets(code: str) -> Dict[str, str]:
    """Extract snippets marked with '# @snippet name'; returns dict name -> content."""
    snippets = {}
    lines = code.splitlines()
    current_snippet = None
    snippet_content = []
    for line in lines:
        if line.strip().startswith("# @snippet"):
            if current_snippet:
                snippets[current_snippet] = "\n".join(snippet_content)
            current_snippet = line.strip().split("@snippet")[1].strip()
            snippet_content = []
        elif current_snippet:
            snippet_content.append(line)
    if current_snippet:
        snippets[current_snippet] = "\n".join(snippet_content)
    return snippets

def highlight_syntax(code: str, language: str) -> str:
    """Apply basic keyword/tag highlighting for python, javascript, or html; else return code unchanged."""
    if language == "python":
        return highlight_python(code)
    if language == "javascript":
        return highlight_javascript(code)
    if language == "html":
        return highlight_html(code)
    return code

def highlight_python(code: str) -> str:
    """Wrap Python keywords in **bold** markdown."""
    keywords = ["def", "class", "import", "from", "if", "else", "elif", "for", "while", "try", "except", "finally", "with", "as", "return", "yield", "True", "False", "None"]
    highlighted = code
    for keyword in keywords:
        highlighted = re.sub(r"\b" + keyword + r"\b", f"**{keyword}**", highlighted)
    return highlighted

def highlight_javascript(code: str) -> str:
    """Wrap JavaScript keywords in **bold** markdown."""
    keywords = ["function", "var", "let", "const", "if", "else", "for", "while", "try", "catch", "finally", "return", "class", "import", "export"]
    highlighted = code
    for keyword in keywords:
        highlighted = re.sub(r"\b" + keyword + r"\b", f"**{keyword}**", highlighted)
    return highlighted

def highlight_html(code: str) -> str:
    """Wrap HTML tags in **bold** markdown."""
    highlighted = re.sub(r"<(\w+)", r"**<\1**", code)
    return re.sub(r"</(\w+)>", r"**</\1>**", highlighted)

def count_tokens(code: str) -> int:
    """Rough token count by splitting on whitespace."""
    return len(code.split())

def summarize_code(code: str) -> str:
    """Return one-line summary: lines, characters, function count, class count."""
    lines = len(code.splitlines())
    chars = len(code)
    functions = len(re.findall(r"def\s+\w+|function\s+\w+|func\s+\w+", code))
    classes = len(re.findall(r"class\s+\w+", code))
    return f"Code summary: {lines} lines, {chars} characters, {functions} functions, {classes} classes"