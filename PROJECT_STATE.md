# Project State

## Project Identity

- Repository Name: Codex_Proposal_Writer_UI
- Repository Root: C:\Users\mf1\Desktop\Codex Proposal Generator UI attempt
- Primary Remote: origin
- Remote URL: https://github.com/mikejf1991/Codex_Proposal_Writer_UI.git
- Default Branch: main
- Bootstrap Status: initialized 2026-03-24 09:14 America/Chicago

## Current State

- Active Objective: Build the first generation-stage proposal writer interface in Python.
- Open Issues: Literature-scout and Zotero integrations are represented as workflow hooks but not yet wired to external skills; the current app uses an OpenAI Responses adapter rather than a full Codex agent runtime.
- Next Recommended Step: Validate the UI scaffold, then deepen the interrogation and drafting loops.

## Active Session Handoff

- Current Branch: main
- Active Task: None.
- Last Meaningful Action: Fixed secondary and disabled button contrast, especially in the dark sidebar.
- Files In Flight: None.
- Verification Status: `python -m compileall src streamlit_app.py` and a headless Streamlit boot check passed.
- Resume From: Replace the current OpenAI adapter with the desired Codex-style backend or tool runner, then deepen interrogation and draft-evaluation loops.

## Open Loops

- Confirm the preferred backend for live Codex or OpenAI execution in production.
- Add deeper document viewing and annotation support beyond text previews and notes.
