"""Load experiments/config.yaml and print keys (no network, no training)."""
from __future__ import annotations

import os

import yaml


def main() -> None:
    parent = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent, "config.yaml")
    if not os.path.isfile(path):
        print("demo_config: no config.yaml at", path)
        return
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    print("demo_config ok — sections:", list(cfg.keys()))


if __name__ == "__main__":
    main()
