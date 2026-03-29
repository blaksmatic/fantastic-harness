# Changelog

All notable changes to Fantastic Harness will be documented in this file.

## [0.1.0] - 2026-03-29

The self-governing AI builder is born.

### Added

- **Miles** — autonomous decision-maker that never executes, only decides and delegates
- **Shadow** — silent observer that watches every decision and takes over when Miles retires
- **Succession** — seamless leadership handoff triggered by context pressure, decision count, or Miles's judgment
- **Validators** — compress executor and hunter results into minimal summaries for Miles
- **Executors** — Data Mate, Router, and custom builders that do the actual work
- **Hunters** — intelligence gatherers that scout Twitter, GitHub, Google on a schedule
- **Auditor** — Miles's personal consultant with a direct line that bypasses validators
- **Adversaries** — Rimu (kind, every ~30 min) and Maurissa (harsh, every ~10 min) evaluate the system fresh each time
- **External Validator** — summarizes all adversarial feedback before it reaches Miles
- **Orchestrator** — asyncio scheduler managing all agent lifecycles and schedules
- **SQLite coordination** — single-file database with 8 tables, zero infrastructure
- **REST API** — 11 FastAPI endpoints for goals, agents, events, input, journal, succession, and adversary triggers
- **SSE streaming** — real-time event stream for the frontend
- **React frontend** — builder-game aesthetic with agent panels, timeline feed, goal tracker, and prompt area
- **LLM provider abstraction** — model-agnostic with Claude defaults (Opus for decisions, Sonnet for validation, Haiku for execution)
- **49 tests** covering database, models, agents, orchestrator, and API
