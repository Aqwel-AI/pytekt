"""Tests for the structured Aion CLI help catalog."""

import json
import sys

from aion.cli import (
    _build_parser,
    _command_rows,
    _completion_script,
    _format_help_json,
    _get_subparsers,
    main,
    shell_command,
)


def test_help_metadata_covers_every_command():
    parser, _ = _build_parser()
    subparsers = _get_subparsers(parser)

    rows = _command_rows(subparsers)

    assert {row["command"] for row in rows} == set(subparsers.choices)
    assert all(row["category"] for row in rows)
    assert all(row["requirements"] for row in rows)
    assert all(row["status"] for row in rows)
    assert all(row["example"] for row in rows)


def test_help_json_is_valid_and_searchable():
    parser, _ = _build_parser()
    subparsers = _get_subparsers(parser)

    all_rows = json.loads(_format_help_json(subparsers))
    physics_rows = json.loads(_format_help_json(subparsers, search="physics"))

    assert len(all_rows) == len(subparsers.choices)
    assert {row["command"] for row in physics_rows} == {"physics", "physics-dashboard"}


def test_completion_scripts_include_aion_commands():
    parser, _ = _build_parser()
    commands = _get_subparsers(parser).choices.keys()

    for shell in ("bash", "zsh", "fish", "powershell"):
        script = _completion_script(shell, commands)
        assert "aion" in script
        assert "physics" in script


def test_cli_handles_ctrl_c_without_traceback(monkeypatch, capsys):
    monkeypatch.setattr("aion.cli._main", lambda: (_ for _ in ()).throw(KeyboardInterrupt))

    assert main() == 130
    output = capsys.readouterr().out
    assert "Operation cancelled by user" in output
    assert "No changes were made" in output


def test_shell_runs_aion_command_without_a_system_shell():
    calls = []

    shell_command(
        "physics force --mass 2 --acceleration 3",
        runner=lambda args, check: calls.append((args, check)),
    )

    assert calls == [
        (
            [
                sys.executable,
                "-m",
                "aion",
                "physics",
                "force",
                "--mass",
                "2",
                "--acceleration",
                "3",
            ],
            False,
        )
    ]


def test_shell_rejects_nested_shells():
    output = []

    shell_command("shell", runner=lambda *_args, **_kwargs: None, output=output.append)

    assert output == ["Nested Aion shells are not supported."]
