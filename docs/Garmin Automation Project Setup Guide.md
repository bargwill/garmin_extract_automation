This guide configures the **Garmin Automation** project so you can hit the ground running.  
It merges best-practice advice from **AI-Driven Personal Project Workflow** and **Garmin Automation Project Blueprint**, turning them into actionable instructions, chat-thread suggestions, and GitHub prep steps.  
*It does **not** implement code; it lays the scaffolding for efficient execution.*

---

## 1  Project Instructions for ChatGPT

Add the **concise blurb** (≈ 6-10 lines) below to your project’s *Instructions* box.  
These rules steer ChatGPT’s behaviour for every chat:

Act as my Garmin-Automation project assistant.

• Treat docs/AI-Driven_Personal_Project_Workflow.md and docs/Garmin_Automation_Project_Blueprint.md as ground truth.  
• Default to step-by-step guidance, code scaffolds, short examples—let me write final code.  
• Cite blueprint line numbers when quoting requirements; cite external sources for sports-science formulas.  
• Keep replies concise unless I ask for deep dives; skip apologies & filler.  
• When a task is unclear, ask one clarifying question, then propose the next concrete action.  
• Use markdown headers, bullets, and checklists.  
• Never change repo state unless I say “commit/PR”.

*(Feel free to tweak wording—just keep it short.)*

---

## 2  Project Chat Threads

Create dedicated chat threads to keep discussion focused:

| Chat Thread | Purpose |
|-------------|---------|
| **General Discussion / Coordination** | High-level questions, clarifications, and planning. |
| **Phase 1 – Hardening & Backlog Cleanup** | `--dry-run`, rate-limit handling, idempotent writes, error logging, CI. |
| **Phase 2 – Analytics Integration** | Weekly totals, polarization, taper, ATL/CTL/TSB, Slack msgs, charts. |
| **Phase 3 – CLI & UX Enhancements** | Colorized output, `--no-color` / `--json`, progress bar, help text. |
| **Phase 4 – Visualization & Reporting** | Chart aesthetics, HTML report, performance tuning. |
| **Phase 5 – Documentation & Release Prep** | README, CHANGELOG, packaging, cross-platform tests, release notes. |
| **Stretch Goals** | Brainstorm web dashboard, SQLite queries, cloud deploy, multi-user, etc. |

When opening a new thread, **link or paste the relevant blueprint sections** so ChatGPT has context.

---

## 3  GitHub Repository Preparation

1. **Documentation folder**  
   *Keep both workflow & blueprint in* `docs/`.  
2. **Project task board**  
   Use **GitHub Projects / Issues** to mirror phases & tasks—copy them verbatim.  
3. **CI configuration**  
   Add `.github/workflows/` for **pytest + lint + ≥ 90 % coverage**.  
4. **Packaging files**  
   Prepare `pyproject.toml` or `setup.cfg` per blueprint release prep.  
5. **Secrets handling**  
   Remove plaintext creds; use **keyring** / env vars. Provide `.env.example`.

---

## 4  Remaining Work Phases & Key Tasks

### Phase 1 – Hardening & Backlog Cleanup
- [ ] `--dry-run` CLI flag (no write / no Slack)  
- [ ] Robust **HTTP 429** retry (parse `Retry-After`, exponential back-off)  
- [ ] Secure creds via **keyring**  
- [ ] Idempotent CSV writes (skip/overwrite duplicates)  
- [ ] Wrap network calls, log to `error.log`  
- [ ] **CI** with coverage ≥ 90 %  

### Phase 2 – Advanced Analytics Integration
- [ ] Extend `analytics.py` – weekly totals, long-run, polarization, taper, **ATL/CTL/TSB**  
- [ ] Synthetic datasets + unit tests  
- [ ] Update Slack/console summary with new metrics  
- [ ] Matplotlib PNG chart generation  

### Phase 3 – CLI & UX Enhancements
- [ ] Colorized output (WCAG-AA) with `rich` / `click`  
- [ ] `--no-color` and `--json` options  
- [ ] Progress indicator on fetch  
- [ ] Improved `--help` and friendly error messages  

### Phase 4 – Visualization & Reporting
- [ ] Finalize plotting funcs (`sync.py charts`)  
- [ ] Optional **HTML report** embedding charts  
- [ ] Performance tuning for large logs  
- [ ] Slack mention when charts generated  

### Phase 5 – Documentation & Release Prep
- [ ] Complete **README.md** (install, config, usage)  
- [ ] Update **CHANGELOG.md**  
- [ ] Finalize packaging metadata & entry points  
- [ ] Cross-platform tests (macOS / Linux / Windows)  
- [ ] Scheduling examples (cron / Task Scheduler)  
- [ ] Tag **v1.0** & write release notes  

---

## 5  Stretch Goals (Post-v1.0)

- **Local Web Dashboard** (Flask / static)  
- **SQLite Query Interface** (CLI or TUI)  
- **Jupyter Notebook Examples**  
- **Cloud Integration & Alerts** (AWS Lambda / GH Actions cron)  
- **Multi-User / Multi-Source Support** (Strava, Fitbit, etc.)

---
