"""Help catalogs for agent and global CLI."""

from __future__ import annotations

from .style import bold, cyan, dim, yellow


def print_startup_guide(*, workspace: str) -> None:
    """Removed — agent uses animation intro only."""
    del workspace


def print_agent_commands() -> None:
    """No-op — command list removed from agent UI."""
    pass


def print_help_catalog() -> None:
    print(f"\n  {bold(cyan('Aion CLI Command Catalog'))}")
    print(f"  {dim('Use ' + yellow('aion <command> --help') + ' for details on any command.')}")
    print(dim("  " + "─" * 60))

    groups = {
        "AGENT & UI": [
            ("agent", "Start the professional AI CLI agent"),
            ("usage / stats", "Token usage & cost dashboard in browser"),
            ("ui / start", "Open the Aion Hub dashboard in browser"),
            ("welcome", "Show the animated modules overview"),
        ],
        "🔐 AUTH & API": [
            ("api connect", "Connect to OpenAI, Gemini, Anthropic, etc."),
            ("api list", "Show all connected company APIs"),
            ("api disconnect", "Remove a company API connection"),
            ("auth login", "Cloud Sign-In (Coming Soon)"),
        ],
        "🛠️ TOOLS & RESEARCH": [
            ("embed", "Generate vector embeddings for files/text"),
            ("eval", "Evaluate model predictions vs ground truth"),
            ("prompt", "Manage and run prompt templates"),
            ("rag", "Simple RAG system for your documents"),
        ],
        "⚙️ SYSTEM": [
            ("config", "Manage CLI and agent settings"),
            ("info", "Show version and dependency status"),
            ("doctor", "Diagnose environment and dependencies"),
        ],
    }

    for group, commands in groups.items():
        print(f"\n  {bold(group)}")
        for cmd, desc in commands:
            print(f"    {cyan(cmd):20} {dim('»')} {desc}")
    print()


def print_interactive_help() -> int:
    from .menus import get_menu_choice

    print_help_catalog()
    options = ["Explore Agent", "Explore API", "Explore Research Tools", "Exit Help"]
    print(f"  {bold('Would you like to explore a category?')}")
    return get_menu_choice(options)
