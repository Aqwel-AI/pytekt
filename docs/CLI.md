# Aion CLI

The Aion CLI is available through the installed `aion` command or with
`python -m aion`.

```bash
aion --help
aion <command> --help
python -m aion info
```

## Installation and environment

```bash
aion install                 # Interactive feature installer
aion install --profile ai    # Install one profile
aion info                    # Show runtime and optional modules
aion doctor                  # Diagnose the environment
aion auth                    # Check provider API-key variables
aion config set theme minimal # Configure terminal output
aion config get theme         # Read a config value
aion config list              # Show non-secret settings
aion env init                 # Create a safe .env.example
aion env check --provider openai
```

Provider credentials are read from standard environment variables such as
`OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`,
and `NVIDIA_API_KEY`. Do not place secrets in project files or commit them.

## Core and AI commands

```bash
aion ask "Explain this result" --provider openai
aion chat
aion embed notes.txt --output notes.npy
aion eval predictions.json answers.json
aion prompt --list
aion watch notes.txt --output-dir embeddings
aion shell
aion shell --command "physics force --mass 2 --acceleration 3"
```

`ask` performs one provider request and exits. It requires the selected
provider's SDK/configuration and API key. `embed` can use the optional
sentence-transformers integration or its built-in fallback.

`shell` opens a small interactive Aion-only terminal: type commands such as
`info`, `help --search physics`, or `physics force --mass 2 --acceleration 3`.
It supports `history`, `help`, and `exit`, and intentionally does not execute
arbitrary operating-system commands.

## Project and research workflows

```bash
aion project init my-study --name climate-study
aion project info
aion project validate
aion project template create research my-study
aion project clean --yes
aion run train.py --experiment baseline --seed 42
aion experiment list --tracker-dir .aion_experiments
aion experiment compare --metric accuracy
aion experiment show RUN_ID
aion experiment export results.md
aion experiment diff RUN_A RUN_B
aion experiment tag RUN_ID baseline
aion experiment reproduce RUN_ID
aion experiment delete RUN_ID --yes
aion benchmark --seeds 5 --output leaderboard.md
aion pipeline run pipeline.json
aion pipeline validate pipeline.json
aion pipeline run pipeline.json --dry-run
```

`pipeline.json` or `pipeline.yaml` contains a list of shell commands:

```json
{
  "steps": [
    {"name": "train", "command": "python train.py"},
    {"name": "evaluate", "command": "python evaluate.py"}
  ]
}
```

Use pipelines only with files you trust because their commands are executed
by the local shell.

## Data, models, and operations

```bash
aion data inspect data.csv --json
aion data sample data.csv --rows 10
aion data validate data.csv --required id label
aion data convert data.csv data.json
aion data split data.json --output-dir splits --seed 42
aion model list
aion model test --provider ollama
aion model info saved_model
aion test tests/test_cli_help.py
aion logs --tail 80
aion cache status
aion cache clear
aion security .
aion upgrade
```

`data inspect` supports CSV, JSON, and JSONL, with YAML available when the
configuration extra is installed. `serve` and `api` require the serving
dependencies:

```bash
aion serve --provider openai --port 8080
```

## Workspace agent

The current `agent` command provides safe workspace inspection:

```bash
aion agent --root .
aion agent read aion/cli.py --root .
aion agent search "TODO" --root .
```

It does not autonomously edit files or run arbitrary model-driven actions.

## Git, database, science, and UI commands

```bash
aion git status
aion git log --limit 10
aion db status
aion start
aion ui --list
aion monitor
aion universe moon
aion universe sky --lat 40.18 --lon 44.51
aion physics force --mass 2 --acceleration 3
aion physics projectile --v0 20 --angle 45
aion vision --help
```

The monitor, serving, vision, universe, and physics commands may require
optional extras. Use `aion <command> --help` for ports and dependency details.

## Extended research and developer commands

```bash
aion notebook create research.ipynb
aion explain aion/cli.py
aion summarize README.md
aion rag index docs --output .aion_rag.json
aion rag query "experiment tracking"
aion visualize data.csv --kind scatter --output plot.png
aion model benchmark train.py --repeat 3
aion model evaluate saved_model data.json --target label
aion experiment report report.html
aion physics fit measurements.json --x time --y position
aion universe observe --lat 40.18 --lon 44.51
aion hardware info
aion performance profile train.py
aion lint --no-tests
aion dependency audit
aion snapshot create backup.zip
aion snapshot restore backup.zip --root restored
aion session list
aion session export default --output session.jsonl
aion release check
aion changelog generate --limit 20
aion serve --watch
aion completion install zsh
```

These commands are designed to be composable in research workflows. Commands
that execute files, pipelines, snapshots, or dependency tools should only be
run against trusted project content.

## Shell completion

```bash
aion completion bash
aion completion zsh
aion completion fish
aion completion powershell
```

The command prints a completion script; install it according to your shell's
startup-file conventions.
