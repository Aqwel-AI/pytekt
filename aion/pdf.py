#!/usr/bin/env python3
"""
Aqwel-Aion - Professional Documentation Generation Module
=================================================================

This module provides automated documentation generation for the Aion library:
publication-ready API references, user guides, and changelogs derived from
source code and metadata.

Module contents
---------------
- PDFDocumentGenerator: PDF creation via ReportLab with configurable styles,
  optional logo, and custom branding (colors, fonts).
- create_api_documentation: Full API reference in PDF for all discovered modules.
- create_text_documentation: Plain-text API documentation when ReportLab is unavailable.
- create_api_documentation_md: API documentation in Markdown with table of contents.
- create_user_guide_pdf / create_user_guide_text: User guide with installation,
  examples, and advanced features.
- generate_complete_documentation: Single entry point to produce API docs, user guide,
  README, API index, and module dependency doc in a target directory.
- generate_module_documentation: Introspection-based docs for one module (docstring,
  function list, signatures).
- create_function_documentation: Focused documentation for a single function or class.
- create_changelog_pdf / create_changelog_text: Changelog from structured data or
  Keep a Changelog-style Markdown.
- create_module_dependency_doc: Report of inter-module imports (aion-only) in PDF or TXT.
- export_api_index: Machine-readable index (JSON, CSV, or Markdown) of public functions.
- search_public_api: Find functions (and optionally classes) whose names contain a query string.
- create_api_documentation_html: Full API reference as a static HTML page (no extra deps).
- create_module_reference_doc: Markdown, text, or PDF reference for a single submodule.
- export_function_list: Text listing of functions for a given module.
- create_pdf_report: Simple PDF (or TXT fallback) from a title and list of paragraphs.
- get_documentation_statistics: Return module/function counts and per-module stats.
- create_installation_guide: Installation and setup guide (TXT or PDF).
- create_quick_reference: Compact function names by module (TXT or PDF).
- validate_documentation: Report which public functions lack docstrings.
- create_documentation_index: Write INDEX.md in a directory listing generated docs.

Technical notes
---------------
- PDF output requires the optional dependency ReportLab; all PDF entry points
  fall back to text (or Markdown where applicable) when ReportLab is not installed.
- Module discovery uses pkgutil over the aion package path; test and private
  modules are excluded. The pdf module is always included so it can document itself.
- Styling (title, headings, code, function signatures) is centralized in
  PDFDocumentGenerator._setup_custom_styles and can be overridden via branding options.

Author: Aksel Aghajanyan
Developed by: Aqwel AI Team
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import os
import json
import html
import inspect
import importlib
import pkgutil
import ast
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import re

# ReportLab is optional; when missing, PDF entry points emit text or Markdown instead.
try:
    from reportlab.lib.pagesizes import A4  # pyright: ignore [reportMissingModuleSource]
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # pyright: ignore [reportMissingModuleSource]
    from reportlab.lib.units import inch  # pyright: ignore [reportMissingModuleSource]
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image  # pyright: ignore [reportMissingModuleSource]
    from reportlab.lib import colors  # pyright: ignore [reportMissingModuleSource]
    from reportlab.lib.colors import HexColor  # pyright: ignore [reportMissingModuleSource]
    from reportlab.lib.enums import TA_CENTER  # pyright: ignore [reportMissingModuleSource]
    _HAS_REPORTLAB = True

    def _resolve_reportlab_color(s):
        """Convert hex string or ReportLab color name to a Color instance, or None."""
        if not s or not s.strip():
            return None
        s = s.strip()
        if s.startswith("#"):
            try:
                return HexColor(s)
            except Exception:
                return None
        return getattr(colors, s, None)
except ImportError:
    _HAS_REPORTLAB = False

    def _resolve_reportlab_color(s):
        return None

# Matplotlib is optional; used only when plotting support is required.
try:
    import matplotlib  # pyright: ignore [reportMissingImports]
    matplotlib.use("Agg")
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False


def get_documentable_modules() -> List[str]:
    """
    Return the list of aion submodule names that should be included in generated docs.
    Uses pkgutil.walk_packages on the aion package path. Skips modules whose name
    contains 'test_files' or whose last path component starts with an underscore.
    The 'pdf' module is always included so this module can document itself.
    On failure or when __path__ is missing, returns a fixed fallback list.
    """
    try:
        import aion
        path = getattr(aion, "__path__", None)
        if not path:
            return sorted([
                "text", "files", "parser", "utils", "maths", "code",
                "snippets", "prompt", "embed", "evaluate", "git", "watcher", "pdf"
            ])
        seen = set()
        for _importer, modname, _ispkg in pkgutil.walk_packages(path, prefix="aion."):
            if "test_files" in modname:
                continue
            parts = modname.split(".")
            if parts[-1].startswith("_"):
                continue
            short = modname.replace("aion.", "", 1)
            if short:
                seen.add(short)
        result = sorted(seen)
        if "pdf" not in result:
            result = sorted(result + ["pdf"])
        return result
    except Exception:
        return sorted([
            "text", "files", "parser", "utils", "maths", "code",
            "snippets", "prompt", "embed", "evaluate", "git", "watcher", "pdf"
        ])


class PDFDocumentGenerator:
    """
    Builds PDF documents from flowable content (paragraphs, tables, images).
    Supports a configurable title page (with optional logo), custom colors and
    fonts for headings, and a set of named styles for body text, code, and
    function signatures.
    """

    def __init__(
        self,
        title: str = "Aion Documentation",
        author: str = "Aqwel AI Team",
        logo_path: Optional[str] = None,
        primary_color: Optional[str] = None,
        font_name: Optional[str] = None,
    ):
        """
        Initialize the generator. ReportLab must be installed.
        Args:
            title: Shown on the first page.
            author: Shown on the title page as "Generated by {author}".
            logo_path: If set and the file exists, the image is drawn above the title.
            primary_color: Hex (e.g. "#1a1a2e") or ReportLab color name for title and Heading1.
            font_name: ReportLab font name for title and Heading1 (e.g. Helvetica-Bold).
        """
        if not _HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
        
        self.title = title
        self.author = author
        self.logo_path = logo_path if logo_path and os.path.isfile(logo_path) else None
        resolved = _resolve_reportlab_color(primary_color) if primary_color else None
        self.primary_color = resolved or colors.darkblue
        self.heading_color = resolved or colors.darkgreen
        self.font_name = font_name or "Helvetica-Bold"
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """
        Register custom paragraph styles used by create_document.

        ReportLab's sample stylesheet already defines ``Title``, ``Heading1``,
        and ``Heading2``. Re-adding styles with those names raises a
        ``KeyError``, so we customize the existing heading styles in place and
        only add truly new style names.
        """
        def add_or_update_style(name: str, parent_name: str, **overrides):
            """Create a style when missing, otherwise update the existing one."""
            if name in self.styles.byName:
                style = self.styles[name]
                for attr, value in overrides.items():
                    setattr(style, attr, value)
                return style

            style = ParagraphStyle(name=name, parent=self.styles[parent_name], **overrides)
            self.styles.add(style)
            return style

        title_color = self.primary_color if isinstance(self.primary_color, colors.Color) else colors.darkblue
        heading_color = self.heading_color if isinstance(self.heading_color, colors.Color) else colors.darkgreen
        font = self.font_name
        add_or_update_style(
            "CustomTitle",
            "Title",
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=title_color,
            fontName=font,
        )

        heading1 = self.styles["Heading1"]
        heading1.fontSize = 18
        heading1.spaceAfter = 12
        heading1.spaceBefore = 20
        heading1.textColor = title_color
        heading1.fontName = font

        heading2 = self.styles["Heading2"]
        heading2.fontSize = 14
        heading2.spaceAfter = 10
        heading2.spaceBefore = 15
        heading2.textColor = heading_color

        add_or_update_style(
            "Code",
            "Normal",
            fontName="Courier",
            fontSize=10,
            leftIndent=20,
            backgroundColor=colors.lightgrey,
            borderColor=colors.grey,
            borderWidth=1,
        )
        add_or_update_style(
            "FunctionSignature",
            "Normal",
            fontName="Courier-Bold",
            fontSize=12,
            textColor=colors.darkred,
            leftIndent=10,
        )
    
    def create_document(self, filename: str, content: List[Any]) -> str:
        """
        Write a PDF to filename with a title page (and optional logo) followed by content.
        Args:
            filename: Output path for the PDF.
            content: Sequence of ReportLab flowables (Paragraph, Table, Spacer, PageBreak, etc.).
        Returns:
            The same filename (path to the generated file).
        """
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        if self.logo_path:
            try:
                img = Image(self.logo_path, width=2*inch, height=2*inch)
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception:
                pass
        story.append(Paragraph(self.title, self.styles["CustomTitle"]))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated by {self.author}", self.styles["Normal"]))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles["Normal"]))
        story.append(PageBreak())
        story.extend(content)
        doc.build(story)
        return filename


def generate_module_documentation(
    module_name: str,
    include_classes: bool = False,
) -> List[Dict[str, Any]]:
    """
    Introspect a single aion submodule and return a structure with its docstring
    and all public function names, signatures, docstrings, and source file paths.
    Args:
        module_name: Either "name" (resolved as aion.name) or "aion.name".
        include_classes: When True, the module dict also has a ``classes`` list of
            public classes defined in that module (name, signature, docstring,
            source_file, and public methods with signatures).
    Returns:
        A one-element list containing a dict with keys: type, name, doc, functions
        (and optionally classes). On import error, the single element has type
        "error" and key "error" with the message.
    """
    try:
        if module_name.startswith("aion."):
            module = importlib.import_module(module_name)
        else:
            module = importlib.import_module(f"aion.{module_name}")
        docs = []
        module_doc = inspect.getdoc(module) or f"Documentation for {module_name} module"
        entry: Dict[str, Any] = {
            "type": "module",
            "name": module_name,
            "doc": module_doc,
            "functions": [],
        }
        if include_classes:
            entry["classes"] = []
        docs.append(entry)

        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("_"):
                try:
                    src = inspect.getfile(obj)
                except (TypeError, OSError):
                    src = "Unknown"
                func_doc = {
                    "name": name,
                    "signature": str(inspect.signature(obj)),
                    "docstring": inspect.getdoc(obj) or "No documentation available",
                    "source_file": src,
                }
                docs[0]["functions"].append(func_doc)

        if include_classes:
            mod_name = getattr(module, "__name__", "")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.startswith("_"):
                    continue
                if getattr(obj, "__module__", None) != mod_name:
                    continue
                try:
                    sig = str(inspect.signature(obj))
                except (ValueError, TypeError):
                    sig = "(...)"
                try:
                    src = inspect.getfile(obj)
                except (TypeError, OSError):
                    src = "Unknown"
                methods: List[Dict[str, str]] = []
                for mname, member in inspect.getmembers(obj, inspect.isfunction):
                    if mname.startswith("_"):
                        continue
                    try:
                        msig = str(inspect.signature(member))
                    except (ValueError, TypeError):
                        msig = "()"
                    methods.append({
                        "name": mname,
                        "signature": msig,
                        "docstring": inspect.getdoc(member) or "No documentation available",
                    })
                docs[0]["classes"].append({
                    "name": name,
                    "signature": sig,
                    "docstring": inspect.getdoc(obj) or "No documentation available",
                    "source_file": src,
                    "methods": methods,
                })

        return docs

    except Exception as e:
        err: Dict[str, Any] = {
            "type": "error",
            "name": module_name,
            "error": str(e),
            "functions": [],
        }
        if include_classes:
            err["classes"] = []
        return [err]


def create_api_documentation(output_file: str = "aion_api_documentation.pdf") -> str:
    """
    Produce API documentation for all documentable aion modules as a single PDF.
    Includes a table of contents (module, short description, function count) and
    per-module sections with description and function signatures plus docstrings.
    If ReportLab is not installed, delegates to create_text_documentation and
    returns the path to the text file.
    """
    if not _HAS_REPORTLAB:
        print("reportlab not available; generating text documentation instead.")
        return create_text_documentation(output_file.replace(".pdf", ".txt"))
    generator = PDFDocumentGenerator("Aion AI/ML Library - API Documentation", "LinkAI Team")
    modules = get_documentable_modules()
    content = []
    content.append(Paragraph("Table of Contents", generator.styles["Heading1"]))
    toc_data = [["Module", "Description", "Functions"]]
    all_docs = {}
    total_functions = 0
    
    for module_name in modules:
        print(f"Generating documentation for {module_name}...")
        module_docs = generate_module_documentation(module_name)
        all_docs[module_name] = module_docs
        if module_docs and module_docs[0]["type"] != "error":
            func_count = len(module_docs[0]["functions"])
            total_functions += func_count
            first_line = module_docs[0]["doc"].split("\n")[0]
            description = first_line[:60] + "..." if len(first_line) > 60 else first_line
            toc_data.append([module_name.title(), description, str(func_count)])
    toc_data.append(["TOTAL", f"{len(modules)} modules", str(total_functions)])
    toc_table = Table(toc_data)
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(toc_table)
    content.append(PageBreak())
    for module_name, module_docs in all_docs.items():
        content.append(Paragraph(f"{module_name.title()} Module", generator.styles["Heading1"]))
        if module_docs and module_docs[0]["type"] != "error":
            doc_data = module_docs[0]
            content.append(Paragraph("Description", generator.styles["Heading2"]))
            content.append(Paragraph(doc_data["doc"], generator.styles["Normal"]))
            content.append(Spacer(1, 12))
            if doc_data["functions"]:
                content.append(Paragraph("Functions", generator.styles["Heading2"]))
                for func in doc_data["functions"]:
                    content.append(Paragraph(f"{func['name']}{func['signature']}", generator.styles["FunctionSignature"]))
                    content.append(Paragraph(func["docstring"], generator.styles["Normal"]))
                    content.append(Spacer(1, 8))
        else:
            content.append(Paragraph(f"Error documenting module: {module_docs[0].get('error', 'Unknown error')}", generator.styles["Normal"]))
        content.append(PageBreak())
    pdf_path = generator.create_document(output_file, content)
    print(f"API documentation generated: {pdf_path}")
    return pdf_path


def create_text_documentation(output_file: str = "aion_documentation.txt") -> str:
    """
    Write plain-text API documentation for all documentable modules. Does not
    require ReportLab. Output includes a short table of contents (module names
    and function counts) followed by per-module description and function list.
    """
    modules = get_documentable_modules()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("AION AI/ML LIBRARY - COMPREHENSIVE DOCUMENTATION\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Author: Aksel Aghajanyan | Developed by: Aqwel AI Team\n\n")
        f.write("TABLE OF CONTENTS\n")
        f.write("-" * 20 + "\n\n")
        total_functions = 0
        for module_name in modules:
            module_docs = generate_module_documentation(module_name)
            if module_docs and module_docs[0]['type'] != 'error':
                func_count = len(module_docs[0]['functions'])
                total_functions += func_count
                f.write(f"{module_name.upper()}: {func_count} functions\n")
        
        f.write(f"\nTOTAL: {total_functions} functions across {len(modules)} modules\n\n")
        f.write("=" * 60 + "\n\n")
        for module_name in modules:
            f.write(f"{module_name.upper()} MODULE\n")
            f.write("=" * (len(module_name) + 7) + "\n\n")
            module_docs = generate_module_documentation(module_name)
            if module_docs and module_docs[0]["type"] != "error":
                doc_data = module_docs[0]
                f.write("DESCRIPTION:\n")
                f.write("-" * 12 + "\n")
                f.write(f"{doc_data['doc']}\n\n")
                if doc_data["functions"]:
                    f.write("FUNCTIONS:\n")
                    f.write("-" * 10 + "\n\n")
                    
                    for func in doc_data['functions']:
                        f.write(f"• {func['name']}{func['signature']}\n")
                        f.write(f"  {func['docstring']}\n\n")
            else:
                f.write(f"Error documenting module: {module_docs[0].get('error', 'Unknown error')}\n\n")
            f.write("-" * 60 + "\n\n")
    print(f"Text documentation generated: {output_file}")
    return output_file


def create_api_documentation_md(output_file: str = "aion_api_documentation.md") -> str:
    """
    Write API documentation in Markdown: title, table of contents with anchors,
    then one level-2 section per module (description and level-3 function subsections).
    """
    modules = get_documentable_modules()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Aion AI/ML Library - API Documentation\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Table of Contents\n\n")
        for mod in modules:
            anchor = mod.replace(".", "-").lower() + "-module"
            f.write(f"- [{mod}](#{anchor})\n")
        f.write("\n---\n\n")
        for module_name in modules:
            f.write(f"## {module_name} Module\n\n")
            module_docs = generate_module_documentation(module_name)
            if module_docs and module_docs[0]["type"] != "error":
                doc_data = module_docs[0]
                f.write("### Description\n\n")
                f.write(doc_data["doc"])
                f.write("\n\n")
                if doc_data["functions"]:
                    f.write("### Functions\n\n")
                    for func in doc_data["functions"]:
                        f.write(f"#### `{func['name']}{func['signature']}`\n\n")
                        f.write(f"{func['docstring']}\n\n")
            else:
                err = module_docs[0].get("error", "Unknown error") if module_docs else "Unknown error"
                f.write(f"*Error documenting module: {err}*\n\n")
    print(f"Markdown API documentation generated: {output_file}")
    return output_file


def create_api_documentation_html(output_file: str = "aion_api_documentation.html") -> str:
    """
    Write a self-contained HTML API reference for all documentable modules.
    Escapes text for safe display; does not require ReportLab or any extra packages.
    """
    modules = get_documentable_modules()
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8"/>',
        "<title>Aion API Documentation</title>",
        "<style>",
        "body{font-family:system-ui,Segoe UI,Helvetica,Arial,sans-serif;max-width:52rem;margin:2rem auto;line-height:1.45;}",
        "h1,h2,h3{color:#1a1a2e;}",
        "code,pre{background:#f4f4f6;padding:0.15em 0.35em;border-radius:4px;font-size:0.92em;}",
        "pre{padding:1rem;overflow:auto;}",
        "nav ul{list-style:none;padding-left:0;}",
        "nav li{margin:0.25rem 0;}",
        ".sig{color:#6b1a1a;font-weight:600;}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Aion AI/ML Library &mdash; API Documentation</h1>",
        f"<p><em>Generated {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</em></p>",
        "<nav><h2>Contents</h2><ul>",
    ]
    for mod in modules:
        aid = html.escape(mod.replace(".", "-").lower() + "-module")
        parts.append(f'<li><a href="#{aid}">{html.escape(mod)}</a></li>')
    parts.extend(["</ul></nav>", "<hr/>"])

    for module_name in modules:
        aid = html.escape(module_name.replace(".", "-").lower() + "-module")
        parts.append(f'<section id="{aid}">')
        parts.append(f"<h2>{html.escape(module_name)}</h2>")
        module_docs = generate_module_documentation(module_name)
        if module_docs and module_docs[0]["type"] != "error":
            doc_data = module_docs[0]
            parts.append("<h3>Description</h3>")
            parts.append(f"<pre>{html.escape(doc_data['doc'])}</pre>")
            if doc_data["functions"]:
                parts.append("<h3>Functions</h3><ul>")
                for func in doc_data["functions"]:
                    sig = html.escape(f"{func['name']}{func['signature']}")
                    ds = html.escape(func["docstring"])
                    parts.append(f"<li><p class=\"sig\">{sig}</p><p>{ds}</p></li>")
                parts.append("</ul>")
        else:
            err = module_docs[0].get("error", "Unknown error") if module_docs else "Unknown error"
            parts.append(f"<p><em>Error: {html.escape(str(err))}</em></p>")
        parts.append("</section><hr/>")

    parts.extend(["</body>", "</html>"])
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"HTML API documentation generated: {output_file}")
    return output_file


def search_public_api(
    query: str,
    *,
    case_sensitive: bool = False,
    include_classes: bool = True,
) -> List[Dict[str, str]]:
    """
    Search documentable modules for public functions (and optionally classes)
    whose names contain ``query``. Returns sorted dicts with keys module, kind
    (``function`` or ``class``), and name.
    """
    if not query:
        return []
    needle = query if case_sensitive else query.casefold()
    results: List[Dict[str, str]] = []
    for mod in get_documentable_modules():
        docs = generate_module_documentation(mod, include_classes=include_classes)
        if not docs or docs[0].get("type") == "error":
            continue
        for func in docs[0].get("functions", []):
            n = func.get("name", "")
            hay = n if case_sensitive else n.casefold()
            if needle in hay:
                results.append({"module": mod, "kind": "function", "name": n})
        if include_classes:
            for cls in docs[0].get("classes", []):
                n = cls.get("name", "")
                hay = n if case_sensitive else n.casefold()
                if needle in hay:
                    results.append({"module": mod, "kind": "class", "name": n})
    return sorted(results, key=lambda x: (x["module"], x["kind"], x["name"]))


def create_module_reference_doc(
    module_name: str,
    output_file: Optional[str] = None,
    format: str = "md",
    include_classes: bool = True,
) -> str:
    """
    Write reference documentation for a single ``aion`` submodule as Markdown,
    plain text, or PDF. Default output is ``{module}_reference.md`` (or .txt / .pdf).
    PDF requires ReportLab; if unavailable, text is written instead.
    """
    docs = generate_module_documentation(module_name, include_classes=include_classes)
    safe = module_name.replace(".", "_")
    if output_file is None:
        if format == "pdf" and _HAS_REPORTLAB:
            output_file = f"{safe}_reference.pdf"
        elif format == "txt":
            output_file = f"{safe}_reference.txt"
        else:
            output_file = f"{safe}_reference.md"

    if docs and docs[0].get("type") == "error":
        err = docs[0].get("error", "Unknown error")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Error documenting {module_name}: {err}\n")
        return output_file

    doc_data = docs[0]

    if format == "txt":
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{module_name.upper()} MODULE REFERENCE\n")
            f.write("=" * (len(module_name) + 20) + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("DESCRIPTION\n-----------\n")
            f.write(f"{doc_data['doc']}\n\n")
            if doc_data.get("functions"):
                f.write("FUNCTIONS\n---------\n\n")
                for func in doc_data["functions"]:
                    f.write(f"• {func['name']}{func['signature']}\n")
                    f.write(f"  {func['docstring']}\n\n")
            if include_classes and doc_data.get("classes"):
                f.write("CLASSES\n-------\n\n")
                for cls in doc_data["classes"]:
                    f.write(f"• class {cls['name']}{cls['signature']}\n")
                    f.write(f"  {cls['docstring']}\n")
                    for m in cls.get("methods", []):
                        f.write(f"    - {m['name']}{m['signature']}\n")
                        f.write(f"      {m['docstring'].split(chr(10))[0]}\n")
                    f.write("\n")
        print(f"Module reference generated: {output_file}")
        return output_file

    if format == "pdf" and _HAS_REPORTLAB:
        generator = PDFDocumentGenerator(
            f"Aion — {module_name} reference",
            "Aqwel AI Team",
        )
        content: List[Any] = []
        content.append(Paragraph("Description", generator.styles["Heading2"]))
        content.append(Paragraph(doc_data["doc"].replace("\n", "<br/>"), generator.styles["Normal"]))
        content.append(Spacer(1, 12))
        if doc_data.get("functions"):
            content.append(Paragraph("Functions", generator.styles["Heading2"]))
            for func in doc_data["functions"]:
                content.append(Paragraph(f"{func['name']}{func['signature']}", generator.styles["FunctionSignature"]))
                content.append(Paragraph(func["docstring"].replace("\n", "<br/>"), generator.styles["Normal"]))
                content.append(Spacer(1, 8))
        if include_classes and doc_data.get("classes"):
            content.append(Paragraph("Classes", generator.styles["Heading2"]))
            for cls in doc_data["classes"]:
                content.append(Paragraph(f"class {cls['name']}{cls['signature']}", generator.styles["FunctionSignature"]))
                content.append(Paragraph(cls["docstring"].replace("\n", "<br/>"), generator.styles["Normal"]))
                for m in cls.get("methods", []):
                    content.append(Paragraph(f"  {m['name']}{m['signature']}", generator.styles["FunctionSignature"]))
                    first = (m.get("docstring") or "").split("\n")[0]
                    content.append(Paragraph(first, generator.styles["Normal"]))
                content.append(Spacer(1, 8))
        generator.create_document(output_file, content)
        print(f"Module reference generated: {output_file}")
        return output_file

    if format == "pdf" and not _HAS_REPORTLAB:
        output_file = output_file.replace(".pdf", ".txt")
        return create_module_reference_doc(module_name, output_file, "txt", include_classes=include_classes)

    # Markdown (default)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# `{module_name}` module reference\n\n")
        f.write(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write("## Description\n\n")
        f.write(doc_data["doc"])
        f.write("\n\n")
        if doc_data.get("functions"):
            f.write("## Functions\n\n")
            for func in doc_data["functions"]:
                f.write(f"### `{func['name']}{func['signature']}`\n\n")
                f.write(f"{func['docstring']}\n\n")
        if include_classes and doc_data.get("classes"):
            f.write("## Classes\n\n")
            for cls in doc_data["classes"]:
                f.write(f"### `class {cls['name']}{cls['signature']}`\n\n")
                f.write(f"{cls['docstring']}\n\n")
                if cls.get("methods"):
                    f.write("#### Methods\n\n")
                    for m in cls["methods"]:
                        f.write(f"- `{m['name']}{m['signature']}` — {(m.get('docstring') or '').split(chr(10))[0]}\n")
                    f.write("\n")
    print(f"Module reference generated: {output_file}")
    return output_file


def _get_aion_imports_from_source(filepath: str) -> List[str]:
    """
    Parse the Python source at filepath with ast and collect the top-level aion
    submodule names used in "import aion.xxx" and "from aion.xxx import ...".
    Returns a sorted list of unique names (e.g. ["files", "text"]).
    """
    imported = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (OSError, SyntaxError):
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "aion":
                    continue
                if alias.name.startswith("aion."):
                    sub = alias.name.replace("aion.", "", 1).split(".")[0]
                    imported.add(sub)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module == "aion":
                imported.add("aion")
            elif node.module and node.module.startswith("aion."):
                top = node.module.replace("aion.", "", 1).split(".")[0]
                imported.add(top)
    return sorted(imported)


def create_module_dependency_doc(
    output_file: str = "aion_module_dependencies.pdf",
    format: str = "pdf",
) -> str:
    """
    Build a report of intra-package imports: for each documentable module, list
    which other aion submodules it imports. Output is PDF (with ReportLab) or
    TXT; the text version includes a Mermaid flowchart snippet.
    """
    modules = get_documentable_modules()
    dep_map: Dict[str, List[str]] = {}
    mermaid_lines = []
    for mod in modules:
        try:
            if mod.startswith("aion."):
                m = importlib.import_module(mod)
            else:
                m = importlib.import_module(f"aion.{mod}")
            path = inspect.getfile(m)
        except Exception:
            dep_map[mod] = []
            continue
        deps = _get_aion_imports_from_source(path)
        dep_map[mod] = deps
        for d in deps:
            if d != mod:
                mermaid_lines.append(f"    {mod.replace('.', '_')} --> {d.replace('.', '_')}")

    if format == "txt" or not _HAS_REPORTLAB:
        out = output_file.replace(".pdf", ".txt") if output_file.endswith(".pdf") else output_file
        if not out.endswith(".txt"):
            out = out + ".txt"
        with open(out, "w", encoding="utf-8") as f:
            f.write("Aion Module Dependencies (aion-only imports)\n")
            f.write("=" * 50 + "\n\n")
            for mod in sorted(dep_map.keys()):
                deps = dep_map[mod]
                f.write(f"{mod}\n")
                f.write(f"  Imports: {', '.join(deps) if deps else '(none)'}\n\n")
            f.write("\nModule dependency graph (Mermaid):\n")
            f.write("```mermaid\nflowchart LR\n")
            if mermaid_lines:
                f.write("\n".join(mermaid_lines) + "\n")
            f.write("```\n")
        print(f"Module dependency doc generated: {out}")
        return out

    generator = PDFDocumentGenerator("Aion Module Dependencies", "LinkAI Team")
    content = []
    content.append(Paragraph("Module | Imports (aion only)", generator.styles["Heading1"]))
    table_data = [["Module", "Imports"]]
    for mod in sorted(dep_map.keys()):
        deps = dep_map[mod]
        table_data.append([mod, ", ".join(deps) if deps else "(none)"])
    tbl = Table(table_data)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(tbl)
    content.append(Spacer(1, 20))
    content.append(Paragraph("Mermaid diagram (flowchart)", generator.styles["Heading2"]))
    mermaid = "flowchart LR\n" + "\n".join(mermaid_lines) if mermaid_lines else "flowchart LR\n  (no cross-module imports)"
    content.append(Paragraph(mermaid.replace("\n", "<br/>"), generator.styles["Code"]))
    path_out = generator.create_document(output_file, content)
    print(f"Module dependency doc generated: {path_out}")
    return path_out


def export_api_index(
    output_file: Optional[str] = None,
    format: str = "json",
    include_classes: bool = False,
) -> str:
    """
    Build a flat index of public callables across documentable modules and write
    it to a file. Each row has module, function (symbol name), signature, and
    docstring_one_line. When ``include_classes`` is True, public classes defined
    in each module are appended as rows with the same shape (signature is the
    class constructor signature). format may be ``json``, ``csv``, or ``md``
    (Markdown table). Default filenames: aion_api_index.json, .csv, or .md.
    """
    modules = get_documentable_modules()
    rows: List[Dict[str, str]] = []
    for mod in modules:
        docs = generate_module_documentation(mod, include_classes=include_classes)
        if not docs or docs[0].get("type") == "error":
            continue
        for func in docs[0].get("functions", []):
            one_line = (func.get("docstring") or "").split(".")[0].strip()
            if one_line and not one_line.endswith("."):
                one_line += "."
            rows.append({
                "module": mod,
                "function": func.get("name", ""),
                "signature": func.get("signature", ""),
                "docstring_one_line": one_line or "No description.",
            })
        if include_classes:
            for cls in docs[0].get("classes", []):
                one_line = (cls.get("docstring") or "").split(".")[0].strip()
                if one_line and not one_line.endswith("."):
                    one_line += "."
                rows.append({
                    "module": mod,
                    "function": cls.get("name", ""),
                    "signature": cls.get("signature", ""),
                    "docstring_one_line": one_line or "No description.",
                })
    if output_file is None:
        if format == "csv":
            output_file = "aion_api_index.csv"
        elif format == "md":
            output_file = "aion_api_index.md"
        else:
            output_file = "aion_api_index.json"
    if format == "csv":
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["module", "function", "signature", "docstring_one_line"])
            w.writeheader()
            w.writerows(rows)
    elif format == "md":

        def _md_cell(s: str) -> str:
            t = (s or "").replace("|", "\\|").replace("\n", " ")
            return t

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Aion API index\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("| Module | Symbol | Signature | Summary |\n")
            f.write("|--------|--------|-----------|--------|\n")
            for r in rows:
                f.write(
                    f"| {_md_cell(r['module'])} | `{_md_cell(r['function'])}` "
                    f"| `{_md_cell(r['signature'])}` | {_md_cell(r['docstring_one_line'])} |\n"
                )
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
    print(f"API index generated: {output_file}")
    return output_file


def _parse_changelog_md(filepath: str) -> List[Dict[str, Any]]:
    """
    Read a Keep a Changelog-style Markdown file and return a list of version
    dicts. Each dict has keys: version, date, and optionally added, changed,
    fixed, enhanced, removed, security, deprecated (each a list of strings).
    """
    version_history = []
    current = None
    current_section = None
    section_keys = ("added", "changed", "fixed", "enhanced", "removed", "security", "deprecated")
    version_re = re.compile(r"^##\s*\[([^\]]+)\]\s*-\s*(\d{4}-\d{2}-\d{2})")
    heading_re = re.compile(r"^#{2,4}\s+(Added|Changed|Fixed|Enhanced|Removed|Security|Deprecated)", re.I)
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            m = version_re.match(line)
            if m:
                if current and (current.get("added") or current.get("changed") or current.get("fixed") or current.get("enhanced") or current.get("removed")):
                    version_history.append(current)
                current = {"version": m.group(1), "date": m.group(2)}
                for k in section_keys:
                    current[k] = []
                current_section = None
                continue
            if current is None:
                continue
            hm = heading_re.match(line)
            if hm:
                current_section = hm.group(1).lower()
                if current_section not in current:
                    current[current_section] = []
                continue
            if current_section and line.strip():
                text = line.strip()
                if text.startswith("- ") or text.startswith("* "):
                    text = text[2:].strip()
                if text and current_section in current:
                    current[current_section].append(text)
        if current:
            version_history.append(current)
    return version_history


def create_changelog_text(
    version_history: Union[List[Dict[str, Any]], str],
    output_file: str = "aion_changelog.txt",
    title: Optional[str] = None,
) -> str:
    """
    Write a plain-text changelog. version_history may be a list of version
    dicts (with keys version, date, and optionally added, changed, fixed, etc.)
    or a path to a Markdown file in Keep a Changelog format.
    """
    if isinstance(version_history, str):
        version_history = _parse_changelog_md(version_history)
    title = title or "Aion Changelog"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for entry in version_history:
            f.write(f"Version {entry.get('version', '')} ({entry.get('date', '')})\n")
            f.write("-" * 40 + "\n")
            for key in ("added", "changed", "fixed", "enhanced", "removed", "security", "deprecated"):
                items = entry.get(key) or []
                if items:
                    f.write(f"\n{key.upper()}:\n")
                    for item in items:
                        f.write(f"  - {item}\n")
            f.write("\n")
    print(f"Changelog text generated: {output_file}")
    return output_file


def create_changelog_pdf(
    version_history: Union[List[Dict[str, Any]], str],
    output_file: str = "aion_changelog.pdf",
    title: Optional[str] = None,
) -> str:
    """
    Produce a PDF changelog from structured version data or from a Keep a Changelog
    Markdown file. If ReportLab is not available, writes text via create_changelog_text
    and returns the text file path.
    """
    if isinstance(version_history, str):
        version_history = _parse_changelog_md(version_history)
    title = title or "Aion Changelog"
    if not _HAS_REPORTLAB:
        txt_file = output_file.replace(".pdf", ".txt")
        return create_changelog_text(version_history, txt_file, title)
    generator = PDFDocumentGenerator(title, "LinkAI Team")
    content = []
    for entry in version_history:
        ver = entry.get("version", "")
        date = entry.get("date", "")
        content.append(Paragraph(f"Version {ver} ({date})", generator.styles["Heading1"]))
        for key in ("added", "changed", "fixed", "enhanced", "removed", "security", "deprecated"):
            items = entry.get(key) or []
            if items:
                content.append(Paragraph(key.upper(), generator.styles["Heading2"]))
                for item in items:
                    content.append(Paragraph(f"• {item}", generator.styles["Normal"]))
                content.append(Spacer(1, 8))
        content.append(Spacer(1, 12))
    pdf_path = generator.create_document(output_file, content)
    print(f"Changelog PDF generated: {pdf_path}")
    return pdf_path


def create_function_documentation(
    module_name: str,
    function_name: str,
    output_file: Optional[str] = None,
    format: str = "pdf",
) -> str:
    """
    Generate focused documentation for one callable (function or class) in a
    documentable module. For classes, includes the class docstring and a list
    of public methods with signatures and first-line docstrings. Output is PDF
    (when ReportLab is available) or TXT. Default output filename is
    {module_name}_{function_name}_doc.pdf or .txt.
    """
    try:
        if module_name.startswith("aion."):
            module = importlib.import_module(module_name)
        else:
            module = importlib.import_module(f"aion.{module_name}")
        obj = getattr(module, function_name, None)
        if obj is None:
            raise ValueError(f"'{function_name}' not found in module {module_name}")
    except Exception as e:
        if output_file is None:
            safe_mod = module_name.replace(".", "_")
            output_file = f"{safe_mod}_{function_name}_doc.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Error documenting {module_name}.{function_name}: {e}\n")
        return output_file

    is_class = inspect.isclass(obj)
    docstring = inspect.getdoc(obj) or "No documentation available."
    try:
        sig = str(inspect.signature(obj))
    except (ValueError, TypeError):
        sig = "()"
    try:
        source_file = inspect.getfile(obj)
    except (TypeError, OSError):
        source_file = "Unknown"

    safe_mod = module_name.replace(".", "_")
    if output_file is None:
        ext = ".pdf" if format == "pdf" and _HAS_REPORTLAB else ".txt"
        output_file = f"{safe_mod}_{function_name}_doc{ext}"

    if format == "txt" or not _HAS_REPORTLAB:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Module: {module_name}\n")
            f.write(f"{'Class' if is_class else 'Function'}: {function_name}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Signature: {function_name}{sig}\n\n")
            f.write(f"Source: {source_file}\n\n")
            f.write("Documentation:\n")
            f.write("-" * 20 + "\n")
            f.write(docstring)
            f.write("\n\n")
            if is_class:
                f.write("Public methods:\n")
                f.write("-" * 20 + "\n")
                for name, member in inspect.getmembers(obj, inspect.isfunction):
                    if name.startswith("_"):
                        continue
                    try:
                        msig = str(inspect.signature(member))
                    except (ValueError, TypeError):
                        msig = "()"
                    mdoc = (inspect.getdoc(member) or "No docstring").split("\n")[0].strip()
                    f.write(f"  {name}{msig}\n    {mdoc}\n\n")
        print(f"Function documentation generated: {output_file}")
        return output_file
    generator = PDFDocumentGenerator("Function Documentation", "LinkAI Team")
    content = []
    content.append(Paragraph(f"Module: {module_name}", generator.styles["Normal"]))
    content.append(Paragraph(f"{'Class' if is_class else 'Function'}: {function_name}", generator.styles["Heading1"]))
    content.append(Paragraph(f"Signature: {function_name}{sig}", generator.styles["FunctionSignature"]))
    content.append(Paragraph(f"Source: {source_file}", generator.styles["Normal"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Documentation", generator.styles["Heading2"]))
    content.append(Paragraph(docstring.replace("\n", "<br/>"), generator.styles["Normal"]))
    if is_class:
        content.append(Spacer(1, 12))
        content.append(Paragraph("Public methods", generator.styles["Heading2"]))
        for name, member in inspect.getmembers(obj, inspect.isfunction):
            if name.startswith("_"):
                continue
            try:
                msig = str(inspect.signature(member))
            except (ValueError, TypeError):
                msig = "()"
            mdoc = (inspect.getdoc(member) or "No docstring").split("\n")[0].strip()
            content.append(Paragraph(f"{name}{msig}", generator.styles["FunctionSignature"]))
            content.append(Paragraph(mdoc, generator.styles["Normal"]))
            content.append(Spacer(1, 6))
    pdf_path = generator.create_document(output_file, content)
    print(f"Function documentation generated: {pdf_path}")
    return pdf_path


def create_user_guide_pdf(output_file: str = "aion_user_guide.pdf") -> str:
    """
    Build a user guide PDF with introduction, installation, usage examples for
    major modules, and an advanced features section. Falls back to
    create_user_guide_text if ReportLab is not installed.
    """
    if not _HAS_REPORTLAB:
        return create_user_guide_text(output_file.replace('.pdf', '.txt'))
    
    generator = PDFDocumentGenerator("Aion AI/ML Library - User Guide", "LinkAI Team")
    content = []
    content.append(Paragraph("Introduction", generator.styles["Heading1"]))
    intro_text = """
    Welcome to the Aion AI/ML Library! This comprehensive toolkit provides everything you need for 
    AI research, machine learning development, and data science projects. With over 175 functions 
    across 12 modules, Aion offers a complete solution for modern AI development.
    """
    content.append(Paragraph(intro_text, generator.styles["Normal"]))
    content.append(Spacer(1, 20))
    content.append(Paragraph("Quick Start", generator.styles["Heading1"]))
    content.append(Paragraph("Installation", generator.styles["Heading2"]))
    install_text = """
    Install Aion using pip:
    
    pip install linkai-aion
    
    For full AI/ML capabilities, install with optional dependencies:
    
    pip install linkai-aion[ai]
    """
    content.append(Paragraph(install_text, generator.styles["Code"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Basic Usage Examples", generator.styles["Heading2"]))
    
    examples = [
        ("Mathematics and Statistics", """
import aion.maths as math

# Basic operations
result = math.addition([1, 2, 3], [4, 5, 6])  # [5, 7, 9]

# Statistical analysis
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean_val = math.mean(data)  # 5.5
correlation = math.correlation([1,2,3,4], [2,4,6,8])  # 1.0

# Machine learning functions
probabilities = math.softmax([1, 2, 3])  # [0.09, 0.245, 0.665]
loss = math.mse_loss([1, 2, 3], [1.1, 2.1, 2.9])  # 0.01
        """),
        
        ("Text Processing", """
import aion.text as text

# Text analysis
word_count = text.count_words("Hello world from Aion")  # 4
emails = text.extract_emails("Contact us at support@linkaiapps.com")
urls = text.extract_urls("Visit https://linkaiapps.com for more info")

# Text cleaning
clean_text = text.clean_text("  Hello   World!  ")  # "Hello World!"
is_palindrome = text.is_palindrome("racecar")  # True
        """),
        
        ("File Management", """
import aion.files as files

# File operations
exists = files.file_exists("data.txt")
info = files.get_file_info("document.pdf")
files.copy_file("source.txt", "backup.txt")

# Batch operations
files.batch_rename_files("/path/to/files", "prefix_", ".txt")
file_list = files.list_files("/data", recursive=True)
        """),
        
        ("Code Analysis", """
import aion.code as code

sample_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

# Analyze code
explanation = code.explain_code(sample_code)
complexity = code.analyze_complexity(sample_code)
functions = code.extract_functions(sample_code)  # ['fibonacci']
smells = code.find_code_smells(sample_code)
        """),
        
        ("Embeddings and AI", """
import aion.embed as embed

# Generate text embeddings
embedding = embed.embed_text("Machine learning is awesome")
file_embedding = embed.embed_file("document.txt")

# Similarity analysis
similarity = embed.cosine_similarity(embedding, file_embedding)

# Find similar texts
corpus = ["AI research", "Machine learning", "Data science"]
similar = embed.find_similar_texts("Artificial intelligence", corpus)
        """),
        
        ("Model Evaluation", """
import aion.evaluate as evaluate

# Classification metrics
y_true = ["cat", "dog", "cat", "bird", "dog"]
y_pred = ["cat", "dog", "bird", "bird", "dog"]
metrics = evaluate.calculate_classification_metrics(y_pred, y_true)

# Regression metrics
y_true_reg = [1.0, 2.0, 3.0, 4.0, 5.0]
y_pred_reg = [1.1, 2.1, 2.9, 4.2, 4.8]
reg_metrics = evaluate.calculate_regression_metrics(y_pred_reg, y_true_reg)

# Text similarity
similarity_metrics = evaluate.evaluate_text_similarity(
    ["hello world", "hi there"], 
    ["hello world", "hello there"]
)
        """)
    ]
    
    for title, example_code in examples:
        content.append(Paragraph(title, generator.styles["Heading2"]))
        content.append(Paragraph(example_code, generator.styles["Code"]))
        content.append(Spacer(1, 15))
    content.append(PageBreak())
    content.append(Paragraph("Advanced Features", generator.styles["Heading1"]))
    
    advanced_sections = [
        ("Linear Algebra Operations", """
The maths module provides comprehensive linear algebra capabilities:

• Matrix operations (multiplication, transpose, inverse)
• Eigenvalue and eigenvector computation
• Singular Value Decomposition (SVD)
• Vector operations (dot product, cross product, normalization)
• Matrix decompositions and factorizations
        """),
        
        ("Machine Learning Utilities", """
Built-in support for common ML tasks:

• Activation functions (sigmoid, ReLU, tanh, softmax)
• Loss functions (MSE, MAE, cross-entropy)
• Distance metrics (Euclidean, Manhattan, cosine)
• Data preprocessing (normalization, scaling)
• Train/test splitting and sampling
        """),
        
        ("Signal Processing", """
Advanced signal processing capabilities:

• Fast Fourier Transform (FFT) and inverse FFT
• Convolution operations
• Frequency domain analysis
• Digital signal filtering
        """),
        
        ("Prompt Engineering", """
Professional prompt management system:

• 11+ specialized prompt templates
• Custom prompt creation with variables
• Conversation-style prompt building
• Prompt optimization for AI models
• Code extraction from prompts
        """)
    ]
    
    for title, description in advanced_sections:
        content.append(Paragraph(title, generator.styles["Heading2"]))
        content.append(Paragraph(description, generator.styles["Normal"]))
        content.append(Spacer(1, 12))
    pdf_path = generator.create_document(output_file, content)
    print(f"User guide generated: {pdf_path}")
    return pdf_path


def create_user_guide_text(output_file: str = "aion_user_guide.txt") -> str:
    """
    Write a plain-text user guide with introduction, installation, quick start
    examples, and advanced features. Used when ReportLab is not available.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("AION AI/ML LIBRARY - USER GUIDE\n")
        f.write("=" * 35 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Author: Aksel Aghajanyan | Developed by: Aqwel AI Team\n\n")
        
        f.write("INTRODUCTION\n")
        f.write("-" * 12 + "\n")
        f.write("""
Welcome to the Aion AI/ML Library! This comprehensive toolkit provides everything 
you need for AI research, machine learning development, and data science projects. 
With over 175 functions across 12 modules, Aion offers a complete solution for 
modern AI development.

INSTALLATION
------------
pip install linkai-aion

For full AI/ML capabilities:
pip install linkai-aion[ai]

QUICK START EXAMPLES
-------------------

1. MATHEMATICS AND STATISTICS:
   import aion.maths as math
   result = math.addition([1, 2, 3], [4, 5, 6])  # [5, 7, 9]
   mean_val = math.mean([1, 2, 3, 4, 5])  # 3.0
   
2. TEXT PROCESSING:
   import aion.text as text
   word_count = text.count_words("Hello world")  # 2
   clean_text = text.clean_text("  Hello!  ")  # "Hello!"

3. FILE MANAGEMENT:
   import aion.files as files
   exists = files.file_exists("data.txt")
   files.copy_file("source.txt", "backup.txt")

4. CODE ANALYSIS:
   import aion.code as code
   explanation = code.explain_code("def hello(): pass")
   complexity = code.analyze_complexity(code_string)

5. EMBEDDINGS:
   import aion.embed as embed
   embedding = embed.embed_text("Machine learning")
   similarity = embed.cosine_similarity(vec1, vec2)

6. MODEL EVALUATION:
   import aion.evaluate as evaluate
   metrics = evaluate.calculate_classification_metrics(y_pred, y_true)

ADVANCED FEATURES
----------------
• Linear algebra operations (matrices, eigenvalues, SVD)
• Machine learning utilities (activations, losses, metrics)
• Signal processing (FFT, convolution)
• Prompt engineering templates
• Code quality analysis
• Statistical computing
• Data preprocessing pipelines

For complete API documentation, see aion_api_documentation.pdf
        """)
    print(f"Text user guide generated: {output_file}")
    return output_file


def generate_complete_documentation(output_dir: str = "docs") -> Dict[str, str]:
    """
    Generate a full documentation package under output_dir: API docs (PDF and TXT),
    user guide (PDF and TXT), and a README index. Creates output_dir if missing.
    PDFs are produced only when ReportLab is installed; otherwise only text
    artifacts are written. Exceptions during individual steps are caught and
    reported; missing ReportLab does not raise.

    Args:
        output_dir: Directory in which to write all files. Default is "docs".

    Returns:
        A dict mapping logical names to absolute paths: api_pdf, api_txt,
        guide_pdf, guide_txt, readme. Keys for failed steps may be absent.

    Generated artifacts:
        - API documentation: full function reference by module (PDF and TXT).
        - User guide: introduction, installation, examples, advanced topics (PDF and TXT).
        - README: overview, list of files, library stats, and quick links.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}
    print("Generating complete Aion documentation package...")
    api_pdf = os.path.join(output_dir, "aion_api_documentation.pdf")
    api_txt = os.path.join(output_dir, "aion_api_documentation.txt")
    
    try:
        if _HAS_REPORTLAB:
            generated_files["api_pdf"] = create_api_documentation(api_pdf)
        generated_files["api_txt"] = create_text_documentation(api_txt)
    except Exception as e:
        print(f"Error generating API docs: {e}")
    guide_pdf = os.path.join(output_dir, "aion_user_guide.pdf")
    guide_txt = os.path.join(output_dir, "aion_user_guide.txt")
    
    try:
        if _HAS_REPORTLAB:
            generated_files["guide_pdf"] = create_user_guide_pdf(guide_pdf)
        generated_files["guide_txt"] = create_user_guide_text(guide_txt)
    except Exception as e:
        print(f"Error generating user guide: {e}")
    summary_file = os.path.join(output_dir, "README.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("""# Aion AI/ML Library Documentation

## Overview
Complete documentation package for the Aion AI/ML Library - a comprehensive toolkit for AI research and development.

## Files Generated
- `aion_api_documentation.pdf` - Complete API reference (PDF format)
- `aion_api_documentation.txt` - Complete API reference (Text format)
- `aion_user_guide.pdf` - User guide with examples (PDF format)
- `aion_user_guide.txt` - User guide with examples (Text format)

## Library Statistics
- **175+ Functions** across 12 modules
- **Complete AI/ML Pipeline** support
- **Production-ready** code quality
- **Extensive documentation** and examples

## Quick Links
- [Installation Guide](aion_user_guide.pdf#installation)
- [API Reference](aion_api_documentation.pdf)
- [Examples](aion_user_guide.pdf#examples)

## Support
For questions and support, visit: https://linkaiapps.com/#linkai-aion

Generated: {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    generated_files["readme"] = summary_file
    print(f"Complete documentation package generated in: {output_dir}")
    print(f"Files created: {len(generated_files)}")
    for file_type, file_path in generated_files.items():
        print(f"  {file_type}: {file_path}")
    
    return generated_files


def create_pdf_report(title: str, content: List[str], output_file: str = "report.pdf") -> str:
    """
    Produce a short report with a title and a list of paragraphs. If ReportLab
    is available, output is PDF; otherwise a plain-text file with the same
    base name and extension .txt is written. Returns the path to the created file.
    """
    if not _HAS_REPORTLAB:
        text_file = output_file.replace(".pdf", ".txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n{'=' * len(title)}\n\n")
            for item in content:
                f.write(f"{item}\n\n")
        return text_file
    generator = PDFDocumentGenerator(title)
    pdf_content = []
    for item in content:
        pdf_content.append(Paragraph(item, generator.styles["Normal"]))
        pdf_content.append(Spacer(1, 12))
    
    return generator.create_document(output_file, pdf_content)


def export_function_list(module_name: str, output_file: Optional[str] = None) -> str:
    """
    Write a plain-text listing of all public functions in the given module:
    numbered lines with function name, signature, and the first sentence of
    the docstring. output_file defaults to "{module_name}_functions.txt".
    """
    if output_file is None:
        output_file = f"{module_name}_functions.txt"
    docs = generate_module_documentation(module_name)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"FUNCTION LIST: {module_name.upper()}\n")
        f.write("=" * (15 + len(module_name)) + "\n\n")
        if docs and docs[0]["type"] != "error":
            functions = docs[0]["functions"]
            f.write(f"Total functions: {len(functions)}\n\n")
            for i, func in enumerate(functions, 1):
                f.write(f"{i:2d}. {func['name']}{func['signature']}\n")
                f.write(f"     {func['docstring'].split('.')[0]}.\n\n")
        else:
            f.write(f"Error: {docs[0].get('error', 'Unknown error')}\n")
    
    return output_file


def get_documentation_statistics() -> Dict[str, Any]:
    """
    Compute documentation statistics for all documentable aion modules.
    Returns a dict with: module_count, total_functions, modules (list of
    {name, function_count}), and modules_with_errors (list of module names that failed).
    """
    modules = get_documentable_modules()
    total_functions = 0
    module_stats = []
    modules_with_errors = []
    for mod in modules:
        docs = generate_module_documentation(mod)
        if not docs or docs[0].get("type") == "error":
            modules_with_errors.append(mod)
            continue
        count = len(docs[0].get("functions", []))
        total_functions += count
        module_stats.append({"name": mod, "function_count": count})
    return {
        "module_count": len(modules),
        "total_functions": total_functions,
        "modules": module_stats,
        "modules_with_errors": modules_with_errors,
    }


def create_installation_guide(
    output_file: str = "aion_installation_guide.txt",
    format: str = "txt",
) -> str:
    """
    Generate an installation and setup guide for the Aion library. Covers pip
    install, optional dependencies (ai, full, dev, docs), and a quick verification
    snippet. format may be "txt" or "pdf" (PDF requires ReportLab).
    """
    content_lines = [
        "Aion AI/ML Library - Installation Guide",
        "=" * 45,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Author: Aksel Aghajanyan | Developed by: Aqwel AI Team",
        "",
        "INSTALLATION",
        "-" * 12,
        "Core package:",
        "  pip install aqwel-aion",
        "",
        "With optional AI/ML dependencies:",
        "  pip install aqwel-aion[ai]",
        "",
        "Full stack (AI, seaborn, faiss, reportlab, pillow):",
        "  pip install aqwel-aion[full]",
        "",
        "Development (pytest, black, flake8):",
        "  pip install aqwel-aion[dev]",
        "",
        "Documentation generation (reportlab, pillow):",
        "  pip install aqwel-aion[docs]",
        "",
        "VERIFICATION",
        "-" * 12,
        "  python -c \"import aion; print(aion.__version__)\"",
        "",
        "SUPPORT",
        "-" * 7,
        "  https://aqwelai.xyz/",
    ]
    text_content = "\n".join(content_lines)
    if format == "pdf" and _HAS_REPORTLAB:
        generator = PDFDocumentGenerator("Aion Installation Guide", "Aqwel AI Team")
        story = []
        for line in content_lines:
            if not line or line.startswith("=") or line.startswith("-"):
                continue
            if line in ("INSTALLATION", "VERIFICATION", "SUPPORT"):
                story.append(Paragraph(line, generator.styles["Heading2"]))
            elif line.strip():
                story.append(Paragraph(line.replace("  ", "&nbsp;&nbsp;") if line.startswith(" ") else line, generator.styles["Normal"]))
        out = output_file if output_file.endswith(".pdf") else output_file.replace(".txt", ".pdf")
        generator.create_document(out, story)
        print(f"Installation guide generated: {out}")
        return out
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text_content)
    print(f"Installation guide generated: {output_file}")
    return output_file


def create_quick_reference(
    output_file: str = "aion_quick_reference.txt",
    format: str = "txt",
) -> str:
    """
    Generate a compact quick reference listing each documentable module and
    its public function names (no signatures or docstrings). format may be
    "txt" or "pdf" (PDF requires ReportLab).
    """
    modules = get_documentable_modules()
    ref_data = []
    for mod in modules:
        docs = generate_module_documentation(mod)
        if docs and docs[0].get("type") != "error":
            names = [f["name"] for f in docs[0].get("functions", [])]
            ref_data.append((mod, names))
    if format == "pdf" and _HAS_REPORTLAB:
        generator = PDFDocumentGenerator("Aion Quick Reference", "Aqwel AI Team")
        content = []
        content.append(Paragraph("Quick Reference - Functions by Module", generator.styles["Heading1"]))
        for mod, names in ref_data:
            content.append(Paragraph(mod, generator.styles["Heading2"]))
            content.append(Paragraph(", ".join(names) if names else "(none)", generator.styles["Normal"]))
            content.append(Spacer(1, 8))
        out = output_file.replace(".txt", ".pdf") if output_file.endswith(".txt") else output_file
        generator.create_document(out, content)
        print(f"Quick reference generated: {out}")
        return out
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("AION QUICK REFERENCE - FUNCTIONS BY MODULE\n")
        f.write("=" * 50 + "\n\n")
        for mod, names in ref_data:
            f.write(f"{mod}\n")
            f.write("-" * len(mod) + "\n")
            f.write(", ".join(names) if names else "(none)")
            f.write("\n\n")
    print(f"Quick reference generated: {output_file}")
    return output_file


def validate_documentation(module_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Check which public functions in the given module (or all documentable
    modules if module_name is None) lack docstrings. Returns a dict with
    keys: modules (list of module names checked), missing_docstrings
    (dict mapping module name to list of function names with no docstring),
    and summary (total_missing, total_functions).
    """
    modules = [module_name] if module_name else get_documentable_modules()
    missing = {}
    total_functions = 0
    total_missing = 0
    for mod in modules:
        docs = generate_module_documentation(mod)
        if not docs or docs[0].get("type") == "error":
            continue
        no_doc = []
        for func in docs[0].get("functions", []):
            total_functions += 1
            ds = (func.get("docstring") or "").strip()
            if not ds or ds.lower() == "no documentation available":
                no_doc.append(func.get("name", ""))
                total_missing += 1
        if no_doc:
            missing[mod] = no_doc
    return {
        "modules": modules,
        "missing_docstrings": missing,
        "summary": {"total_functions": total_functions, "total_missing": total_missing},
    }


def create_documentation_index(
    output_dir: str = "docs",
    output_file: Optional[str] = None,
) -> str:
    """
    Create an index file (INDEX.md) in output_dir that lists expected or
    generated documentation files with short descriptions. Creates
    output_dir if missing. output_file defaults to output_dir/INDEX.md.
    """
    os.makedirs(output_dir, exist_ok=True)
    if output_file is None:
        output_file = os.path.join(output_dir, "INDEX.md")
    entries = [
        ("aion_api_documentation.pdf", "Full API reference (PDF)."),
        ("aion_api_documentation.txt", "Full API reference (plain text)."),
        ("aion_api_documentation.md", "Full API reference (Markdown)."),
        ("aion_api_documentation.html", "Full API reference (static HTML)."),
        ("aion_api_index.md", "API index as a Markdown table."),
        ("aion_user_guide.pdf", "User guide with examples (PDF)."),
        ("aion_user_guide.txt", "User guide with examples (plain text)."),
        ("aion_installation_guide.txt", "Installation and setup guide."),
        ("aion_quick_reference.txt", "Quick reference - functions by module."),
        ("aion_changelog.pdf", "Changelog (PDF)."),
        ("aion_changelog.txt", "Changelog (plain text)."),
        ("aion_module_dependencies.pdf", "Module dependency report (PDF)."),
        ("aion_module_dependencies.txt", "Module dependency report (plain text)."),
    ]
    lines = [
        "# Aion Documentation Index",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| File | Description |",
        "|------|-------------|",
    ]
    for filename, desc in entries:
        lines.append(f"| {filename} | {desc} |")
    lines.extend(["", "For more information, visit https://aqwelai.xyz/"])
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Documentation index generated: {output_file}")
    return output_file
