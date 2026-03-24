from __future__ import annotations

from pathlib import Path

import streamlit as st

from proposal_writer_ui.models import AutonomyLevel, DiscoveryMode, DocumentCategory, ProposalProject
from proposal_writer_ui.orchestrator import ProposalOrchestrator
from proposal_writer_ui.storage import (
    import_uploaded_file,
    list_saved_projects,
    load_project,
    resolve_document_path,
    save_project,
    update_document_notes,
)


ROOT_DIR = Path(__file__).resolve().parents[2]


def run_app() -> None:
    st.set_page_config(
        page_title="Codex Proposal Writer",
        page_icon="P",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()
    ensure_session_state()

    st.markdown(
        """
        <div class="hero-shell">
            <p class="eyebrow">Generation Studio</p>
            <h1>Codex Proposal Writer</h1>
            <p class="hero-copy">
                Build a proposal corpus, interrogate the concept until it is draft-ready,
                and iterate sections against the FOA and evaluation materials.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_project = sidebar_project_controls()
    if current_project is None:
        st.info("Create or load a project from the sidebar to start assembling materials.")
        return

    orchestrator = ProposalOrchestrator(ROOT_DIR)

    left, right = st.columns([2.2, 1.1])
    with left:
        tabs = st.tabs(["Intake", "Corpus", "Interrogation", "Drafting"])
        render_intake_tab(tabs[0], current_project)
        render_corpus_tab(tabs[1], current_project)
        render_interrogation_tab(tabs[2], current_project, orchestrator)
        render_drafting_tab(tabs[3], current_project, orchestrator)
    with right:
        render_status_panel(current_project, orchestrator)


def ensure_session_state() -> None:
    if "project" not in st.session_state:
        st.session_state.project = None
    if "status_message" not in st.session_state:
        st.session_state.status_message = ""


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Cormorant+Garamond:wght@500;600&display=swap');

            :root {
                --canvas: #f4efe5;
                --paper: rgba(255, 252, 246, 0.88);
                --ink: #1f2a2e;
                --accent: #8a4f2b;
                --leaf: #5c7666;
                --line: rgba(31, 42, 46, 0.12);
                --muted: rgba(31, 42, 46, 0.74);
                --field-bg: rgba(255, 250, 242, 0.9);
            }

            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(92, 118, 102, 0.14), transparent 32%),
                    radial-gradient(circle at bottom left, rgba(138, 79, 43, 0.14), transparent 26%),
                    linear-gradient(180deg, #f7f2e9 0%, #efe7db 100%);
                color: var(--ink);
                font-family: 'IBM Plex Sans', sans-serif;
            }

            .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {
                color: var(--ink);
            }

            h1, h2, h3 {
                font-family: 'Cormorant Garamond', serif;
                color: #203033;
                letter-spacing: 0.01em;
            }

            .hero-shell {
                padding: 1.2rem 1.5rem 1rem 1.5rem;
                border: 1px solid var(--line);
                background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(248, 238, 223, 0.94));
                border-radius: 24px;
                box-shadow: 0 18px 40px rgba(50, 42, 33, 0.08);
                margin-bottom: 1rem;
            }

            .eyebrow {
                color: var(--leaf);
                text-transform: uppercase;
                font-size: 0.75rem;
                letter-spacing: 0.16em;
                margin-bottom: 0.3rem;
            }

            .hero-copy {
                max-width: 56rem;
                color: var(--muted);
                margin-bottom: 0;
            }

            .status-card {
                border: 1px solid var(--line);
                background: var(--paper);
                border-radius: 22px;
                padding: 1rem 1rem 0.3rem 1rem;
                box-shadow: 0 14px 28px rgba(61, 48, 33, 0.07);
            }

            .pill {
                display: inline-block;
                padding: 0.26rem 0.6rem;
                border-radius: 999px;
                background: rgba(92, 118, 102, 0.12);
                color: var(--leaf);
                border: 1px solid rgba(92, 118, 102, 0.18);
                font-size: 0.78rem;
                margin-right: 0.35rem;
                margin-bottom: 0.35rem;
            }

            .stTabs [data-baseweb="tab-list"] button {
                color: var(--muted);
            }

            .stTabs [aria-selected="true"] {
                color: var(--accent);
            }

            .stTextInput label,
            .stTextArea label,
            .stSelectbox label,
            .stRadio label,
            .stCheckbox label,
            .stToggle label,
            .stFileUploader label,
            .stMultiSelect label {
                color: var(--ink) !important;
            }

            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"] > div {
                color: var(--ink) !important;
                background: var(--field-bg) !important;
                border-color: rgba(31, 42, 46, 0.18) !important;
            }

            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: rgba(31, 42, 46, 0.52) !important;
                -webkit-text-fill-color: rgba(31, 42, 46, 0.52) !important;
                opacity: 1 !important;
            }

            .stRadio div[role="radiogroup"] label,
            .stCheckbox label,
            .stToggle label {
                color: var(--ink) !important;
            }

            .stAlert {
                color: var(--ink);
            }

            code, pre {
                color: #1d2528 !important;
            }

            .stButton > button {
                color: var(--ink) !important;
                border: 1px solid rgba(31, 42, 46, 0.2) !important;
                background: rgba(255, 250, 242, 0.92) !important;
            }

            .stButton > button[kind="primary"] {
                color: #fff7f1 !important;
                background: #c4572b !important;
                border-color: #b24d24 !important;
            }

            .stButton > button:hover {
                color: var(--ink) !important;
                border-color: rgba(31, 42, 46, 0.34) !important;
                background: rgba(255, 248, 238, 1) !important;
            }

            .stButton > button[kind="primary"]:hover {
                color: #fff7f1 !important;
                background: #ae4822 !important;
                border-color: #9a3f1d !important;
            }

            section[data-testid="stSidebar"] .stButton > button {
                color: #f6efe6 !important;
                background: rgba(255, 255, 255, 0.06) !important;
                border: 1px solid rgba(255, 255, 255, 0.16) !important;
            }

            section[data-testid="stSidebar"] .stButton > button * {
                color: #f6efe6 !important;
            }

            section[data-testid="stSidebar"] .stButton > button:hover {
                color: #fff7f1 !important;
                background: rgba(255, 255, 255, 0.12) !important;
                border-color: rgba(255, 255, 255, 0.24) !important;
            }

            section[data-testid="stSidebar"] .stButton > button:hover * {
                color: #fff7f1 !important;
            }

            section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
                color: #fff7f1 !important;
                background: #ff5252 !important;
                border-color: #ff5252 !important;
            }

            section[data-testid="stSidebar"] .stButton > button[kind="primary"] * {
                color: #fff7f1 !important;
            }

            section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
                color: #fff7f1 !important;
                background: #f04a4a !important;
                border-color: #f04a4a !important;
            }

            section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover * {
                color: #fff7f1 !important;
            }

            .stButton > button:disabled,
            .stButton > button[disabled],
            section[data-testid="stSidebar"] .stButton > button:disabled,
            section[data-testid="stSidebar"] .stButton > button[disabled] {
                color: rgba(241, 232, 220, 0.78) !important;
                background: rgba(255, 255, 255, 0.08) !important;
                border-color: rgba(255, 255, 255, 0.18) !important;
                -webkit-text-fill-color: rgba(241, 232, 220, 0.78) !important;
                opacity: 1 !important;
            }

            .stButton > button:disabled *,
            .stButton > button[disabled] *,
            section[data-testid="stSidebar"] .stButton > button:disabled *,
            section[data-testid="stSidebar"] .stButton > button[disabled] * {
                color: rgba(241, 232, 220, 0.78) !important;
                -webkit-text-fill-color: rgba(241, 232, 220, 0.78) !important;
            }

            @media (prefers-color-scheme: dark) {
                .stApp {
                    color-scheme: light;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_project_controls() -> ProposalProject | None:
    with st.sidebar:
        st.header("Projects")
        project_title = st.text_input("New project title", placeholder="NSF Robotics Planning Proposal")
        if st.button("Create Project", use_container_width=True, type="primary"):
            if project_title.strip():
                project = ProposalProject.new(project_title)
                save_project(ROOT_DIR, project)
                st.session_state.project = project
                st.session_state.status_message = f"Created {project.title}."
            else:
                st.session_state.status_message = "Project title is required."

        saved_projects = list_saved_projects(ROOT_DIR)
        options = {path.name: path for path in saved_projects}
        selected_name = st.selectbox("Saved projects", options=[""] + list(options))
        if st.button("Load Selected", use_container_width=True):
            if selected_name:
                st.session_state.project = load_project(options[selected_name])
                st.session_state.status_message = f"Loaded {st.session_state.project.title}."

        if st.session_state.project is not None:
            if st.button("Save Project", use_container_width=True):
                save_project(ROOT_DIR, st.session_state.project)
                st.session_state.status_message = f"Saved {st.session_state.project.title}."

        if st.session_state.status_message:
            st.caption(st.session_state.status_message)

    return st.session_state.project


def render_intake_tab(tab: st.delta_generator.DeltaGenerator, project: ProposalProject) -> None:
    with tab:
        st.subheader("Project Intake")
        project.title = st.text_input("Working title", value=project.title)
        project.summary = st.text_area(
            "High-level summary",
            value=project.summary,
            placeholder="Short description of the funding target, problem, and the proposed core move.",
            height=120,
        )
        project.concept_text = st.text_area(
            "Concept notes",
            value=project.concept_text,
            placeholder="Rough concept notes are enough here. The interrogation loop will do the heavy lifting.",
            height=240,
        )

        discovery_labels = {mode.label: mode for mode in DiscoveryMode}
        autonomy_labels = {mode.label: mode for mode in AutonomyLevel}

        left, right = st.columns(2)
        with left:
            selected_discovery = st.radio(
                "Discovery mode",
                options=list(discovery_labels),
                index=list(discovery_labels.values()).index(project.settings.discovery_mode),
            )
            project.settings.discovery_mode = discovery_labels[selected_discovery]
        with right:
            selected_autonomy = st.radio(
                "User oversight",
                options=list(autonomy_labels),
                index=list(autonomy_labels.values()).index(project.settings.autonomy_level),
            )
            project.settings.autonomy_level = autonomy_labels[selected_autonomy]

        settings_left, settings_right = st.columns(2)
        with settings_left:
            project.settings.use_lit_scout = st.checkbox(
                "Enable literature-scout hook",
                value=project.settings.use_lit_scout,
            )
            project.settings.enable_web_search = st.checkbox(
                "Allow web-grounded exploration",
                value=project.settings.enable_web_search,
            )
        with settings_right:
            project.settings.use_zotero = st.checkbox(
                "Enable Zotero hook",
                value=project.settings.use_zotero,
            )
            project.settings.respect_page_limits = st.checkbox(
                "Enforce page-conscious drafting",
                value=project.settings.respect_page_limits,
            )

        project.settings.require_section_review = st.toggle(
            "Require human review before moving section status forward",
            value=project.settings.require_section_review,
        )
        project.ready_for_interrogation = st.toggle(
            "Ready to move into interrogation",
            value=project.ready_for_interrogation,
        )

        if st.button("Save Intake Changes", type="primary"):
            save_project(ROOT_DIR, project)
            st.session_state.status_message = "Saved intake settings."


def render_corpus_tab(tab: st.delta_generator.DeltaGenerator, project: ProposalProject) -> None:
    with tab:
        st.subheader("Source Corpus")
        st.caption("Import files by category. Each upload is copied into the project save state.")

        for category in DocumentCategory:
            st.markdown(f"### {category.label}")
            uploaded_files = st.file_uploader(
                f"Upload {category.label}",
                accept_multiple_files=True,
                key=f"upload-{category.value}",
            )
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    existing_names = {
                        document.name for document in project.documents if document.category == category
                    }
                    if uploaded_file.name in existing_names:
                        continue
                    import_uploaded_file(
                        ROOT_DIR,
                        project,
                        category,
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                    )
                save_project(ROOT_DIR, project)
                st.session_state.status_message = f"Imported files for {category.label}."

            category_documents = [document for document in project.documents if document.category == category]
            if not category_documents:
                st.info(f"No files imported for {category.label} yet.")
                continue

            for document in category_documents:
                path = resolve_document_path(ROOT_DIR, project, document)
                with st.expander(document.name):
                    notes = st.text_area(
                        "Notes / markup",
                        value=document.notes,
                        key=f"notes-{document.document_id}",
                        height=100,
                    )
                    if notes != document.notes:
                        update_document_notes(project, document.document_id, notes)
                    if path.suffix.lower() in {".txt", ".md", ".json", ".csv"} and path.exists():
                        st.code(path.read_text(encoding="utf-8")[:4000], language="text")
                    else:
                        st.caption(f"Preview not yet supported for {path.suffix or 'this file type'}.")

        if st.button("Save Corpus State"):
            save_project(ROOT_DIR, project)
            st.session_state.status_message = "Saved corpus changes."


def render_interrogation_tab(
    tab: st.delta_generator.DeltaGenerator,
    project: ProposalProject,
    orchestrator: ProposalOrchestrator,
) -> None:
    with tab:
        st.subheader("Interrogation Loop")
        st.caption("Use this stage to develop enough specificity that drafting can proceed with limited extra prompting.")

        if st.button("Generate Next Question Set", type="primary"):
            questions = orchestrator.generate_interrogation_questions(project)
            orchestrator.add_turn(project, "assistant", questions)
            save_project(ROOT_DIR, project)
            st.session_state.status_message = "Generated a new interrogation question set."

        answer = st.text_area(
            "Add user answer or manual clarification",
            placeholder="Paste the user's answer or your own working notes here.",
            height=160,
            key="interrogation-answer",
        )
        transcript_left, transcript_right = st.columns(2)
        with transcript_left:
            if st.button("Add User Turn"):
                if answer.strip():
                    orchestrator.add_turn(project, "user", answer)
                    save_project(ROOT_DIR, project)
                    st.session_state.status_message = "Added a user interrogation turn."
        with transcript_right:
            if st.button("Add Analyst Note"):
                if answer.strip():
                    orchestrator.add_turn(project, "analyst", answer)
                    save_project(ROOT_DIR, project)
                    st.session_state.status_message = "Added an analyst note."

        if not project.interrogation:
            st.info("No interrogation turns yet.")
        else:
            for turn in reversed(project.interrogation[-10:]):
                st.markdown(f"**{turn.speaker.title()}**")
                st.write(turn.content)
                st.caption(turn.created_at)


def render_drafting_tab(
    tab: st.delta_generator.DeltaGenerator,
    project: ProposalProject,
    orchestrator: ProposalOrchestrator,
) -> None:
    with tab:
        st.subheader("Drafting and Refinement")
        section_options = {section.title: section.section_id for section in project.sections}
        selected_title = st.selectbox("Section", options=list(section_options))
        section = orchestrator.section_by_id(project, section_options[selected_title])

        st.caption(section.requirement_focus)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Draft Section", type="primary"):
                orchestrator.draft_section(project, section.section_id)
                st.session_state[f"section-content-{section.section_id}"] = section.content
                st.session_state[f"section-notes-{section.section_id}"] = section.review_notes
                save_project(ROOT_DIR, project)
                st.session_state.status_message = f"Drafted {section.title}."
        with col2:
            if st.button("Run Review Cycle"):
                orchestrator.evaluate_and_refine_section(project, section.section_id)
                st.session_state[f"section-content-{section.section_id}"] = section.content
                st.session_state[f"section-notes-{section.section_id}"] = section.review_notes
                save_project(ROOT_DIR, project)
                st.session_state.status_message = f"Refined {section.title}."

        section.content = st.text_area(
            "Section content",
            value=section.content,
            height=420,
            key=f"section-content-{section.section_id}",
        )
        section.review_notes = st.text_area(
            "Review notes / markup",
            value=section.review_notes,
            height=120,
            key=f"section-notes-{section.section_id}",
        )

        if st.button("Save Section Edits"):
            project.touch()
            save_project(ROOT_DIR, project)
            st.session_state.status_message = f"Saved edits for {section.title}."


def render_status_panel(project: ProposalProject, orchestrator: ProposalOrchestrator) -> None:
    st.markdown('<div class="status-card">', unsafe_allow_html=True)
    st.subheader("Workflow Snapshot")
    st.markdown(f'<span class="pill">{project.settings.discovery_mode.label}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="pill">{project.settings.autonomy_level.label}</span>', unsafe_allow_html=True)
    if project.settings.use_lit_scout:
        st.markdown('<span class="pill">Lit scout hook</span>', unsafe_allow_html=True)
    if project.settings.use_zotero:
        st.markdown('<span class="pill">Zotero hook</span>', unsafe_allow_html=True)
    if project.settings.enable_web_search:
        st.markdown('<span class="pill">Web search enabled</span>', unsafe_allow_html=True)

    for note in orchestrator.readiness_notes(project):
        st.write(f"- {note}")

    st.markdown("### Draft Progress")
    for section in project.sections:
        st.write(f"{section.title}: {section.status.value} (round {section.revision_round})")
    output_dir = ROOT_DIR / "projects" / project.project_id / "outputs" / "llm-runs.jsonl"
    if output_dir.exists():
        st.caption(f"LLM run log: {output_dir}")
    st.markdown("</div>", unsafe_allow_html=True)
