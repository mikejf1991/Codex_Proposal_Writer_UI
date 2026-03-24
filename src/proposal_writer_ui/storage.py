from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from proposal_writer_ui.models import DocumentCategory, DocumentRecord, ProposalProject, slugify


PROJECT_FILE_NAME = "project.json"
ATTACHMENTS_DIR_NAME = "attachments"
OUTPUTS_DIR_NAME = "outputs"


def projects_root(root_dir: Path) -> Path:
    path = root_dir / "projects"
    path.mkdir(parents=True, exist_ok=True)
    return path


def project_dir(root_dir: Path, project: ProposalProject) -> Path:
    path = projects_root(root_dir) / project.project_id
    path.mkdir(parents=True, exist_ok=True)
    (path / ATTACHMENTS_DIR_NAME).mkdir(exist_ok=True)
    (path / OUTPUTS_DIR_NAME).mkdir(exist_ok=True)
    return path


def list_saved_projects(root_dir: Path) -> list[Path]:
    root = projects_root(root_dir)
    candidates = sorted(root.glob(f"*/{PROJECT_FILE_NAME}"))
    return [candidate.parent for candidate in candidates]


def save_project(root_dir: Path, project: ProposalProject) -> Path:
    target_dir = project_dir(root_dir, project)
    project.touch()
    target_file = target_dir / PROJECT_FILE_NAME
    target_file.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
    return target_file


def load_project(project_path: Path) -> ProposalProject:
    target_file = project_path / PROJECT_FILE_NAME
    return ProposalProject.from_dict(json.loads(target_file.read_text(encoding="utf-8")))


def import_uploaded_file(
    root_dir: Path,
    project: ProposalProject,
    category: DocumentCategory,
    original_name: str,
    payload: bytes,
) -> DocumentRecord:
    safe_name = Path(original_name).name
    suffix = Path(safe_name).suffix
    stored_name = f"{uuid4().hex}{suffix}"
    project_path = project_dir(root_dir, project)
    attachment_dir = project_path / ATTACHMENTS_DIR_NAME / category.value
    attachment_dir.mkdir(parents=True, exist_ok=True)
    stored_file = attachment_dir / stored_name
    stored_file.write_bytes(payload)
    record = DocumentRecord(
        document_id=uuid4().hex,
        category=category,
        name=safe_name,
        stored_path=str(stored_file.relative_to(project_path)),
    )
    project.documents.append(record)
    project.touch()
    return record


def update_document_notes(project: ProposalProject, document_id: str, notes: str) -> None:
    for document in project.documents:
        if document.document_id == document_id:
            document.notes = notes
            project.touch()
            return


def write_output_artifact(root_dir: Path, project: ProposalProject, name: str, content: str) -> Path:
    output_dir = project_dir(root_dir, project) / OUTPUTS_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{slugify(name)}.md"
    target = output_dir / file_name
    target.write_text(content, encoding="utf-8")
    return target


def resolve_document_path(root_dir: Path, project: ProposalProject, document: DocumentRecord) -> Path:
    return project_dir(root_dir, project) / document.stored_path


def summarize_documents(documents: Iterable[DocumentRecord]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for document in documents:
        summary[document.category.value] = summary.get(document.category.value, 0) + 1
    return summary
