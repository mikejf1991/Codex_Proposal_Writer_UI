# Codex Proposal Writer UI

A Python-first interface for assembling proposal inputs, running structured LLM interrogation, and iterating toward draft-ready proposal sections.

## Current Focus

This repository is currently centered on the generation workflow:

- import and organize proposal source materials by category
- capture concept notes and project configuration
- save and reload complete project state
- run interrogation prep and transcript management
- scaffold section-by-section drafting and review loops

## Run

1. Create a virtual environment.
2. Install dependencies with `python -m pip install -e .`
3. Start the app with `python -m streamlit run streamlit_app.py`

Set `OPENAI_API_KEY` if you want live LLM calls through the OpenAI Responses API adapter.

## Notes

- All LLM prompts in the app load and apply the local `AGENT.MD` rules.
- The first pass includes placeholders for literature scouting and Zotero-assisted flows so those integrations can be wired in without reshaping the project model.
