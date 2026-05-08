# DisciplineOS Development Plan

This document tracks the gap between the whitepaper and the current implementation, then turns that gap into an execution plan.

## Current Implementation Baseline

The current project is a local-first prototype with:

- Investor profile editing.
- Manual discipline card editing.
- Basic decision gate.
- Basic rule engine.
- Basic violation ledger.
- Basic monthly review.
- Local Web UI and CLI.

It is not yet a full implementation of `DisciplineOS Architecture Whitepaper v0.1`.

## Missing Or Partial Capabilities

| Whitepaper Module | Status | Missing Work |
|---|---:|---|
| Investor Discipline Profile | Partial | questionnaire, behavior diagnostics, versioning, stronger rule inheritance |
| Discipline Card Generator | Missing | six-question wizard, asset templates, generated card drafts |
| Discipline Card | Partial | structured valuation, buy/add/reduce/invalid conditions, review reminders |
| Rule Engine | Partial | configurable rule registry, rule strength, evidence-required state, full violation library |
| Decision Gate | Partial | automatic position calculation, position-aware checks, evidence completeness |
| Position Guard | Missing | position CRUD, single/sector/theme/market/currency exposure, loss concentration |
| Violation Ledger | Partial | linked trade impact, remediation, lifecycle state |
| Discipline Score | Partial | weighted scoring by position, buy, sell, earnings, review, emotion, evidence |
| Review Engine | Partial | market/security/portfolio/behavior attribution, rule revision suggestions |
| Unified Data Model | Partial | Asset, Position, Trade, Rule, ReviewReport |
| Data Adapter Layer | Missing | manual import, CSV, Excel, broker export adapters |
| AI Copilot Layer | Missing | card drafting, report summary, thesis drift detection, review drafting |
| Templates | Partial | value/growth/cyclical/trend/ETF templates, review templates |
| Compliance Boundary | Partial | stronger in-product notices and AI output restrictions |

## Execution Plan

### Phase 1: Make The MVP Operational

Goal: make the system useful without external data sources.

- Add `Asset`, `Position`, and portfolio exposure models.
- Add position CRUD in the service layer and Web UI.
- Implement Position Guard for single-position, sector, theme, market, and currency exposure.
- Upgrade Decision Gate so buy/add/reduce/sell amount can automatically calculate before/after position percentages.
- Show portfolio exposure warnings on the dashboard.

### Phase 2: Discipline Card Generator

Goal: help a user create discipline cards instead of facing a blank form.

- [x] Add a six-question wizard.
- [x] Generate discipline cards from answers.
- [x] Add value, growth, cyclical, trend, and ETF templates.
- [x] Store generated cards as editable drafts.

### Phase 3: Rule Engine And Violation Ledger

Goal: turn basic checks into auditable discipline governance.

- [x] Introduce a rule registry.
- [x] Implement violation types from the whitepaper.
- [x] Add severity weights and remediation suggestions.
- [x] Link violations to decisions and discipline cards.
- [x] Add remediation lifecycle state.
- [ ] Add full position linkage.

### Phase 4: Discipline Score And Review Engine

Goal: make monthly review meaningful.

- [x] Implement weighted score dimensions:
  position 25%, buy 20%, sell 15%, earnings 10%, review 10%, emotion 10%, evidence 10%.
- [x] Add market/security/portfolio/behavior attribution fields.
- [x] Generate rule revision suggestions from repeated violations.

### Phase 5: Data Adapter Layer

Goal: reduce manual entry.

- [x] Add CSV import for positions and trades.
- [x] Add Excel template import.
- [x] Add adapter interfaces for future broker/public data integrations.

### Phase 6: AI Copilot Layer

Goal: use AI as a copilot, not the final investment judge.

- [x] Generate discipline card drafts.
- [x] Summarize financial reports.
- [x] Detect thesis drift.
- [x] Draft monthly review text.
- [x] Enforce compliance boundaries in AI prompts and UI copy.
