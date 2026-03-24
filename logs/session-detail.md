# Session Detail Log

## 2026-03-24 09:28 America/Chicago
Entry ID: LOG-0001
Request
- Start the new proposal-writer repository and build a first-pass interface focused on proposal generation.

Context
- The prior workspace had been pointed at a testing repository and needed to be rebound to the new project remote.
- The user described a Python-controlled workflow that imports source materials, captures concept notes, interrogates the user through an LLM, and drafts proposal sections against FOA and evaluation materials.
- The first pass was intentionally scoped toward generation rather than full document revision tooling.

Actions
- Repointed `origin` to `https://github.com/mikejf1991/Codex_Proposal_Writer_UI.git` and moved the fresh project history onto `main`.
- Added a new `AGENT.MD` with proposal-specific LLM output rules and created a clean `PROJECT_STATE.md` for the new repository.
- Created a Streamlit app scaffold with tabs for intake, source corpus import, interrogation, and drafting.
- Implemented structured project models, JSON save/load, attachment storage, note fields for imported documents, section draft tracking, and output artifact writing.
- Added a pluggable LLM adapter that applies the local agent rules to every call and falls back to prompt previews when no API key is configured.

Files Changed
- `.gitignore`
- `AGENT.MD`
- `PROJECT_STATE.md`
- `README.md`
- `logs/session-summary.md`
- `logs/session-detail.md`
- `pyproject.toml`
- `streamlit_app.py`
- `src/proposal_writer_ui/__init__.py`
- `src/proposal_writer_ui/models.py`
- `src/proposal_writer_ui/storage.py`
- `src/proposal_writer_ui/llm.py`
- `src/proposal_writer_ui/orchestrator.py`
- `src/proposal_writer_ui/ui.py`

Change Scope
- Bootstrap a usable proposal-writer UI and repository identity for the new project.

Actual Change Scope
- Delivered a generation-stage Streamlit application with persistent project state, categorized uploads, interrogation transcript management, section drafting hooks, and proposal-specific LLM guardrails.

Verification
- `python -m pip install -e .`: passed.
- Import check for `proposal_writer_ui.ui` and `ProposalOrchestrator`: passed.
- Storage round-trip test with a temporary project and attachment import: passed.
- `python -m compileall src streamlit_app.py`: passed.
- Headless Streamlit startup on port `8518`: passed.

Open Items
- Literature-scout and Zotero integrations are not yet wired to external skills or plugins.
- Document preview is currently limited to text-friendly file types plus note fields.

## 2026-03-24 09:53 America/Chicago
Entry ID: LOG-0002
Request
- Fix the washed-out text contrast and confirm whether the current app is using a real Codex integration with logging behavior.

Context
- The first scaffold rendered poorly under the user's display settings because many labels were inheriting theme colors instead of explicit contrast-safe colors.
- The current runtime uses the OpenAI Responses API and passes `AGENT.MD` as the request instructions, but it does not host a full Codex agent runtime.
- The user specifically wanted assurance that the app would "log its shit" when generating through the LLM path.

Actions
- Strengthened the Streamlit CSS to force darker labels, tabs, widget text, and light input backgrounds regardless of theme.
- Added per-project LLM run logging in `projects/<project-id>/outputs/llm-runs.jsonl`.
- Logged the operation name, model, discovery mode, autonomy level, prompt preview, output preview, timestamp, and `AGENT.MD` SHA-256 hash for each generation call.
- Updated `AGENT.MD`, `README.md`, and `PROJECT_STATE.md` to reflect the current integration boundary and new logging behavior.

Files Changed
- `AGENT.MD`
- `PROJECT_STATE.md`
- `README.md`
- `logs/session-summary.md`
- `logs/session-detail.md`
- `src/proposal_writer_ui/storage.py`
- `src/proposal_writer_ui/orchestrator.py`
- `src/proposal_writer_ui/ui.py`

Change Scope
- Improve interface readability and add concrete logging to the current LLM execution path.

Actual Change Scope
- Fixed theme-dependent contrast issues, made LLM run logging persistent per project, and documented that the app currently uses an OpenAI adapter rather than an embedded Codex runtime.

Verification
- `python -m compileall src streamlit_app.py`: passed.
- Orchestrator generation call created `llm-runs.jsonl`: passed.
- Headless Streamlit startup on port `8519`: passed.

Open Items
- Replace the OpenAI Responses adapter with the intended Codex integration approach if direct Codex runtime behavior is required.
- Decide whether the full prompt and full output should be logged rather than previews only.
