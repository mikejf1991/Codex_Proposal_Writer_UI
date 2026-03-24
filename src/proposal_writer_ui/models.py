from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class DocumentCategory(str, Enum):
    FOA = "foa"
    EXEMPLAR = "exemplar"
    TEMPLATE = "template"
    ADDITIONAL = "additional"
    CONCEPT = "concept"

    @property
    def label(self) -> str:
        labels = {
            DocumentCategory.FOA: "FOA / NOFO / Review Materials",
            DocumentCategory.EXEMPLAR: "Exemplars / Prior Proposals",
            DocumentCategory.TEMPLATE: "Templates",
            DocumentCategory.ADDITIONAL: "Additional Documentation",
            DocumentCategory.CONCEPT: "Concept Materials",
        }
        return labels[self]


class DiscoveryMode(str, Enum):
    SUBJECT_MATTER_READY = "subject_matter_ready"
    BACKGROUND_ASSIST = "background_assist"
    IDEA_DISCOVERY = "idea_discovery"

    @property
    def label(self) -> str:
        return {
            DiscoveryMode.SUBJECT_MATTER_READY: "I know the background and the core idea",
            DiscoveryMode.BACKGROUND_ASSIST: "I have the idea and need background support",
            DiscoveryMode.IDEA_DISCOVERY: "I need help shaping the idea and context",
        }[self]


class AutonomyLevel(str, Enum):
    HIGH_AUTOMATION = "high_automation"
    BALANCED = "balanced"
    REVIEW_HEAVY = "review_heavy"

    @property
    def label(self) -> str:
        return {
            AutonomyLevel.HIGH_AUTOMATION: "Nearly full auto",
            AutonomyLevel.BALANCED: "Limited user input",
            AutonomyLevel.REVIEW_HEAVY: "Significant user review",
        }[self]


class DraftStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    READY_FOR_REVIEW = "ready_for_review"
    REFINED = "refined"


@dataclass
class DocumentRecord:
    document_id: str
    category: DocumentCategory
    name: str
    stored_path: str
    notes: str = ""
    imported_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "category": self.category.value,
            "name": self.name,
            "stored_path": self.stored_path,
            "notes": self.notes,
            "imported_at": self.imported_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentRecord":
        return cls(
            document_id=data["document_id"],
            category=DocumentCategory(data["category"]),
            name=data["name"],
            stored_path=data["stored_path"],
            notes=data.get("notes", ""),
            imported_at=data.get("imported_at", now_iso()),
        )


@dataclass
class InterrogationTurn:
    speaker: str
    content: str
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "speaker": self.speaker,
            "content": self.content,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InterrogationTurn":
        return cls(
            speaker=data["speaker"],
            content=data["content"],
            created_at=data.get("created_at", now_iso()),
        )


@dataclass
class SectionDraft:
    section_id: str
    title: str
    requirement_focus: str
    content: str = ""
    review_notes: str = ""
    status: DraftStatus = DraftStatus.NOT_STARTED
    revision_round: int = 0
    updated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "requirement_focus": self.requirement_focus,
            "content": self.content,
            "review_notes": self.review_notes,
            "status": self.status.value,
            "revision_round": self.revision_round,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SectionDraft":
        return cls(
            section_id=data["section_id"],
            title=data["title"],
            requirement_focus=data["requirement_focus"],
            content=data.get("content", ""),
            review_notes=data.get("review_notes", ""),
            status=DraftStatus(data.get("status", DraftStatus.NOT_STARTED.value)),
            revision_round=data.get("revision_round", 0),
            updated_at=data.get("updated_at", now_iso()),
        )


@dataclass
class ProjectSettings:
    discovery_mode: DiscoveryMode = DiscoveryMode.SUBJECT_MATTER_READY
    autonomy_level: AutonomyLevel = AutonomyLevel.BALANCED
    use_lit_scout: bool = True
    use_zotero: bool = True
    enable_web_search: bool = False
    respect_page_limits: bool = False
    require_section_review: bool = True
    llm_model: str = "gpt-5"
    max_refinement_rounds: int = 3

    def to_dict(self) -> dict[str, Any]:
        return {
            "discovery_mode": self.discovery_mode.value,
            "autonomy_level": self.autonomy_level.value,
            "use_lit_scout": self.use_lit_scout,
            "use_zotero": self.use_zotero,
            "enable_web_search": self.enable_web_search,
            "respect_page_limits": self.respect_page_limits,
            "require_section_review": self.require_section_review,
            "llm_model": self.llm_model,
            "max_refinement_rounds": self.max_refinement_rounds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectSettings":
        return cls(
            discovery_mode=DiscoveryMode(data.get("discovery_mode", DiscoveryMode.SUBJECT_MATTER_READY.value)),
            autonomy_level=AutonomyLevel(data.get("autonomy_level", AutonomyLevel.BALANCED.value)),
            use_lit_scout=data.get("use_lit_scout", True),
            use_zotero=data.get("use_zotero", True),
            enable_web_search=data.get("enable_web_search", False),
            respect_page_limits=data.get("respect_page_limits", False),
            require_section_review=data.get("require_section_review", True),
            llm_model=data.get("llm_model", "gpt-5"),
            max_refinement_rounds=data.get("max_refinement_rounds", 3),
        )


def default_sections() -> list[SectionDraft]:
    return [
        SectionDraft(
            section_id="problem-significance",
            title="Problem Statement and Significance",
            requirement_focus="Why the problem matters, why now, and what strategic gap the proposal addresses.",
        ),
        SectionDraft(
            section_id="state-of-the-art",
            title="State of the Art and Differentiation",
            requirement_focus="Current state of the field, competing approaches, and why this project is distinct.",
        ),
        SectionDraft(
            section_id="objectives",
            title="Objectives and Aims",
            requirement_focus="Clear objectives, hypotheses or design targets, and measurable outcomes.",
        ),
        SectionDraft(
            section_id="workplan",
            title="Technical Workplan",
            requirement_focus="Methods, tasks, sequencing, dependencies, and technical execution details.",
        ),
        SectionDraft(
            section_id="milestones",
            title="Milestones, Deliverables, and Go / No-Go Logic",
            requirement_focus="Milestones, deliverables, success criteria, and go/no-go thresholds when required.",
        ),
        SectionDraft(
            section_id="evaluation",
            title="Evaluation Alignment",
            requirement_focus="Explicit alignment to review criteria and instructional materials.",
        ),
        SectionDraft(
            section_id="broader-impacts",
            title="Broader Impacts and Outputs",
            requirement_focus="Wider benefits, dissemination, adoption, and stakeholder value.",
        ),
    ]


@dataclass
class ProposalProject:
    project_id: str
    title: str
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    summary: str = ""
    concept_text: str = ""
    ready_for_interrogation: bool = False
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    documents: list[DocumentRecord] = field(default_factory=list)
    interrogation: list[InterrogationTurn] = field(default_factory=list)
    sections: list[SectionDraft] = field(default_factory=default_sections)

    @classmethod
    def new(cls, title: str) -> "ProposalProject":
        project_id = f"{slugify(title)}-{uuid4().hex[:8]}"
        return cls(project_id=project_id, title=title.strip())

    def touch(self) -> None:
        self.updated_at = now_iso()

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "summary": self.summary,
            "concept_text": self.concept_text,
            "ready_for_interrogation": self.ready_for_interrogation,
            "settings": self.settings.to_dict(),
            "documents": [document.to_dict() for document in self.documents],
            "interrogation": [turn.to_dict() for turn in self.interrogation],
            "sections": [section.to_dict() for section in self.sections],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProposalProject":
        return cls(
            project_id=data["project_id"],
            title=data["title"],
            created_at=data.get("created_at", now_iso()),
            updated_at=data.get("updated_at", now_iso()),
            summary=data.get("summary", ""),
            concept_text=data.get("concept_text", ""),
            ready_for_interrogation=data.get("ready_for_interrogation", False),
            settings=ProjectSettings.from_dict(data.get("settings", {})),
            documents=[DocumentRecord.from_dict(item) for item in data.get("documents", [])],
            interrogation=[InterrogationTurn.from_dict(item) for item in data.get("interrogation", [])],
            sections=[SectionDraft.from_dict(item) for item in data.get("sections", [])] or default_sections(),
        )


def slugify(value: str) -> str:
    stripped = value.strip().lower()
    chunks = ["".join(character for character in part if character.isalnum()) for part in stripped.split()]
    filtered = [chunk for chunk in chunks if chunk]
    return "-".join(filtered) or "proposal-project"
