from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from proposal_writer_ui.llm import TextGenerationClient, build_client
from proposal_writer_ui.models import (
    DiscoveryMode,
    DraftStatus,
    InterrogationTurn,
    ProposalProject,
    SectionDraft,
    now_iso,
)
from proposal_writer_ui.storage import append_llm_run_log, summarize_documents, write_output_artifact


class ProposalOrchestrator:
    def __init__(self, root_dir: Path, client: TextGenerationClient | None = None) -> None:
        self.root_dir = root_dir
        self.client = client or build_client()
        self.agent_rules = (root_dir / "AGENT.MD").read_text(encoding="utf-8")

    def log_llm_run(
        self,
        project: ProposalProject,
        operation: str,
        prompt: str,
        output: str,
    ) -> None:
        append_llm_run_log(
            self.root_dir,
            project,
            {
                "run_id": uuid4().hex,
                "timestamp": now_iso(),
                "operation": operation,
                "model": project.settings.llm_model,
                "agent_file": "AGENT.MD",
                "agent_sha256": hashlib.sha256(self.agent_rules.encode("utf-8")).hexdigest(),
                "discovery_mode": project.settings.discovery_mode.value,
                "autonomy_level": project.settings.autonomy_level.value,
                "prompt_preview": prompt[:3000],
                "output_preview": output[:3000],
            },
        )

    def readiness_notes(self, project: ProposalProject) -> list[str]:
        document_summary = summarize_documents(project.documents)
        notes = [
            f"Documents loaded: {sum(document_summary.values())}",
            f"Discovery mode: {project.settings.discovery_mode.label}",
            f"Autonomy level: {project.settings.autonomy_level.label}",
        ]
        if not project.concept_text.strip():
            notes.append("Concept text is still missing.")
        if document_summary.get("foa", 0) == 0:
            notes.append("No FOA / review materials imported yet.")
        if project.ready_for_interrogation:
            notes.append("Project is marked ready for interrogation.")
        else:
            notes.append("Project is not yet marked ready for interrogation.")
        return notes

    def build_context_snapshot(self, project: ProposalProject) -> str:
        document_lines = [
            f"- {document.category.label}: {document.name}"
            for document in project.documents
        ] or ["- No documents uploaded."]
        section_lines = [
            f"- {section.title}: {section.requirement_focus}"
            for section in project.sections
        ]
        transcript_lines = [
            f"{turn.speaker.title()}: {turn.content}"
            for turn in project.interrogation[-8:]
        ] or ["No interrogation turns yet."]
        return "\n".join(
            [
                f"Project title: {project.title}",
                f"Project summary: {project.summary or 'Not provided.'}",
                f"Concept text: {project.concept_text or 'Not provided.'}",
                "",
                "Imported materials:",
                *document_lines,
                "",
                "Section targets:",
                *section_lines,
                "",
                "Recent transcript:",
                *transcript_lines,
            ]
        )

    def interrogation_prompt(self, project: ProposalProject) -> str:
        mode_instructions = {
            DiscoveryMode.SUBJECT_MATTER_READY: (
                "Ask pointed proposal-development questions. Assume the user understands the field."
            ),
            DiscoveryMode.BACKGROUND_ASSIST: (
                "Ask questions that both develop the proposal and identify missing background context."
            ),
            DiscoveryMode.IDEA_DISCOVERY: (
                "Start earlier in the ideation process. Ask questions that help shape the concept before locking commitments."
            ),
        }[project.settings.discovery_mode]
        return "\n".join(
            [
                "Produce the next 5 interrogation questions for proposal development.",
                "Return a numbered list and keep each question specific and non-redundant.",
                mode_instructions,
                "",
                self.build_context_snapshot(project),
            ]
        )

    def generate_interrogation_questions(self, project: ProposalProject) -> str:
        prompt = self.interrogation_prompt(project)
        output = self.client.generate_text(
            instructions=self.agent_rules,
            prompt=prompt,
            model=project.settings.llm_model,
        )
        self.log_llm_run(project, "interrogation_questions", prompt, output)
        write_output_artifact(self.root_dir, project, "interrogation-question-set", output)
        return output

    def add_turn(self, project: ProposalProject, speaker: str, content: str) -> None:
        project.interrogation.append(InterrogationTurn(speaker=speaker, content=content.strip()))
        project.touch()

    def section_by_id(self, project: ProposalProject, section_id: str) -> SectionDraft:
        for section in project.sections:
            if section.section_id == section_id:
                return section
        raise KeyError(section_id)

    def draft_section(self, project: ProposalProject, section_id: str) -> str:
        section = self.section_by_id(project, section_id)
        prompt = "\n".join(
            [
                f"Draft the proposal section titled: {section.title}",
                f"Requirement focus: {section.requirement_focus}",
                "Write expansively. Do not compress for page limits unless the project settings explicitly require it.",
                "If evidence is missing, flag the assumption inline under a short 'Open Assumptions' subheading.",
                "",
                self.build_context_snapshot(project),
            ]
        )
        output = self.client.generate_text(
            instructions=self.agent_rules,
            prompt=prompt,
            model=project.settings.llm_model,
        )
        project.touch()
        section.content = output
        section.status = DraftStatus.READY_FOR_REVIEW
        section.revision_round += 1
        section.updated_at = project.updated_at
        self.log_llm_run(project, f"draft_section:{section.section_id}", prompt, output)
        write_output_artifact(self.root_dir, project, section.title, output)
        return output

    def evaluate_and_refine_section(self, project: ProposalProject, section_id: str) -> str:
        section = self.section_by_id(project, section_id)
        prompt = "\n".join(
            [
                f"Evaluate and improve the proposal section titled: {section.title}",
                "First identify any gaps against the imported evaluation materials and proposal-writing rules.",
                "Then provide a revised section draft.",
                "",
                "Current section draft:",
                section.content or "No content yet.",
                "",
                self.build_context_snapshot(project),
            ]
        )
        output = self.client.generate_text(
            instructions=self.agent_rules,
            prompt=prompt,
            model=project.settings.llm_model,
        )
        project.touch()
        section.content = output
        section.status = DraftStatus.REFINED
        section.revision_round += 1
        section.updated_at = project.updated_at
        self.log_llm_run(project, f"refine_section:{section.section_id}", prompt, output)
        write_output_artifact(self.root_dir, project, f"{section.title}-refined", output)
        return output
