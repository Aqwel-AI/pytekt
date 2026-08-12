import pytekt


SAMPLE_CODE = '''
"""Module docstring."""

import os
from typing import Any

CONSTANT_VALUE: int = 7
# TODO: improve cache policy

@decorator
def top_level(x: int, y: str = "a") -> str:
    """Top-level docstring."""
    local_value = x + 1
    return y


async def fetch_data(url: str) -> bytes:
    return b"ok"


class Base:
    pass


@dataclass
class Demo(Base):
    """Class docstring."""

    def method(self, flag: bool) -> None:
        """Method docstring."""
        if not flag:
            raise ValueError("bad flag")
        return None
'''


def test_extract_comments_and_todos():
    assert pytekt.snippets.extract_comments(SAMPLE_CODE) == ["# TODO: improve cache policy"]
    assert pytekt.snippets.extract_todo_comments(SAMPLE_CODE) == ["# TODO: improve cache policy"]


def test_extract_functions_classes_and_async_functions():
    assert pytekt.snippets.extract_functions(SAMPLE_CODE) == ["top_level", "method"]
    assert pytekt.snippets.extract_async_functions(SAMPLE_CODE) == ["fetch_data"]
    assert pytekt.snippets.extract_class_defs(SAMPLE_CODE) == ["Base", "Demo"]


def test_extract_docstrings_and_imports():
    docstrings = pytekt.snippets.extract_docstrings(SAMPLE_CODE)
    imports = pytekt.snippets.extract_imports(SAMPLE_CODE)
    assert "Module docstring." in docstrings
    assert "Top-level docstring." in docstrings
    assert imports == ["os", "typing"]


def test_extract_decorators_methods_and_bases():
    decorators = pytekt.snippets.extract_decorators(SAMPLE_CODE)
    methods = pytekt.snippets.extract_methods(SAMPLE_CODE)
    bases = pytekt.snippets.extract_class_bases(SAMPLE_CODE)
    assert decorators == ["decorator", "dataclass"]
    assert methods == {"Base": [], "Demo": ["method"]}
    assert bases == {"Base": [], "Demo": ["Base"]}


def test_extract_constants_assignments_and_type_hints():
    constants = pytekt.snippets.extract_constants(SAMPLE_CODE)
    assignments = pytekt.snippets.extract_assignments(SAMPLE_CODE)
    type_hints = pytekt.snippets.extract_type_hints(SAMPLE_CODE)
    assert constants == ["CONSTANT_VALUE"]
    assert "CONSTANT_VALUE" in assignments
    assert "local_value" in assignments
    assert type_hints["CONSTANT_VALUE"] == "int"
    assert type_hints["top_level:x"] == "int"
    assert type_hints["top_level:return"] == "str"


def test_extract_signatures_raises_and_returns():
    signatures = pytekt.snippets.extract_function_signatures(SAMPLE_CODE)
    raises = pytekt.snippets.extract_raise_statements(SAMPLE_CODE)
    returns = pytekt.snippets.extract_return_statements(SAMPLE_CODE)
    assert signatures["top_level"] == "top_level(x: int, y: str = 'a') -> str"
    assert signatures["fetch_data"] == "fetch_data(url: str) -> bytes"
    assert "raise ValueError('bad flag')" in raises
    assert "return y" in returns


def test_extract_code_blocks_and_formatting_helpers():
    markdown = """
Text

```python
print("hello")
```

```sql
SELECT 1;
```
"""
    assert pytekt.snippets.extract_code_blocks(markdown) == ['print("hello")', "SELECT 1;"]
    assert pytekt.snippets.extract_code_blocks(markdown, language="python") == ['print("hello")']
    assert pytekt.snippets.format_snippet("\n\tif True:\n\t\tprint('x')\n", indent=2) == "  if True:\n    print('x')"
    assert pytekt.snippets.truncate_snippet("a\nb\nc", max_lines=2) == "a\nb\n..."
    assert pytekt.snippets.snippet_line_count("a\n\nb\n") == 2


def test_validity_summary_and_entities():
    assert pytekt.snippets.is_valid_python_snippet(SAMPLE_CODE) is True
    assert pytekt.snippets.is_valid_python_snippet("def broken(") is False

    summary = pytekt.snippets.summarize_python_snippet(SAMPLE_CODE)
    entities = pytekt.snippets.extract_python_entities(SAMPLE_CODE)

    assert summary["function_count"] == 2
    assert summary["async_function_count"] == 1
    assert summary["class_count"] == 2
    assert entities["methods"]["Demo"] == ["method"]
    assert entities["constants"] == ["CONSTANT_VALUE"]
