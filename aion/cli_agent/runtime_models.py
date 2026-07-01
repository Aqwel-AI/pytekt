"""Shared runtime dataclasses for edit intents, validation, and artifact auditing."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    ok: bool
    checks: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EditIntent:
    task_id: str
    user_request: str
    paths: List[str] = field(default_factory=list)
    status: str = "pending"
    diffs: Dict[str, str] = field(default_factory=dict)
    file_summaries: List[str] = field(default_factory=list)
    validation: Optional[ValidationResult] = None
    rollback_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.validation is not None:
            data["validation"] = self.validation.to_dict()
        return data


@dataclass
class CommandRecord:
    command: str
    returncode: int
    output_preview: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArtifactRecord:
    kind: str
    path: str = ""
    command: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
