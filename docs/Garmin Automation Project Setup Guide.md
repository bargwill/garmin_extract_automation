This guide is intended to configure the Garmin Automation project so that you can hit the ground running with development. It synthesizes best‑practice advice from the AI‑Driven Personal Project Workflow and the Garmin Automation Project Blueprint and breaks it down into actionable project instructions, chat thread suggestions and GitHub repository preparations. It does not implement any code itself; rather, it lays out the scaffolding for efficient execution.
1. Project Instructions for ChatGPT

Add the following custom instructions to your Garmin Automation project in ChatGPT. These instructions explain how ChatGPT should behave when assisting with this project and embed key guidelines from the workflow document.

    Context ingestion: At the start of each new project session, provide ChatGPT with the latest Project Blueprint and this workflow guide. The AI should parse these documents and extract tasks, deadlines and a high‑level roadmap
    GitHub
    .

    Task decomposition: Instruct ChatGPT to break large goals into smaller actionable items. It should prioritize tasks based on urgency and dependencies, and suggest reasonable timelines
    GitHub
    .

    AI collaboration: Emphasize that ChatGPT is a collaborative partner. It may draft code, documentation, unit tests or research answers, but the developer must always review and approve outputs
    GitHub
    .

    Progress tracking: Ask ChatGPT to maintain a running task list (e.g., in a Markdown checklist). It should generate periodic status reports summarizing completed work, ongoing tasks and upcoming steps
    GitHub
    .

    Security and privacy: Remind ChatGPT not to request or expose secrets such as API keys or login credentials. Sensitive information should be stored in secure keychains or environment variables
    GitHub
    .

    Continuous improvement: Encourage ChatGPT to suggest refinements to the workflow after each major milestone. Lessons learned should be captured in retrospectives
    GitHub
    .

2. Project Chat Threads

Organize discussion by creating dedicated chat threads within the project. This keeps conversations focused and makes it easier to revisit decisions. Suggested threads include:
Chat thread	Purpose
General Discussion / Coordination	High‑level questions, clarifications and planning across all phases.
Phase 1 – Hardening & Backlog Cleanup	Discuss the dry‑run option, rate‑limit handling, idempotent writes, improved error logging and CI configuration
GitHub
.
Phase 2 – Analytics Integration	Plan the implementation of weekly totals, polarization metrics, taper readiness, ATL/CTL/TSB calculations, Slack message formatting and chart generation
GitHub
.
Phase 3 – CLI & UX Enhancements	Track work on colored output, --no‑color/--json flags, progress indicators and improved help text
GitHub
.
Phase 4 – Visualization & Reporting	Coordinate chart aesthetics, HTML report generation and performance optimizations
GitHub
.
Phase 5 – Documentation & Release Prep	Draft the README and CHANGELOG, finalize packaging metadata, cross‑platform testing and release notes
GitHub
.
Stretch Goals	Brainstorm and prioritize ideas beyond v1.0 such as a web dashboard, SQLite query interface or cloud deployment
GitHub
.

When starting a new thread, link or embed the relevant sections of the blueprint so ChatGPT has the necessary context.
3. GitHub Repository Preparation

Although ChatGPT cannot push changes directly to GitHub via this interface, you can prepare the repository locally and then commit/push manually. Suggested preparations include:

    Documentation folder: Ensure the docs/ directory contains both the AI‑Driven Personal Project Workflow and Garmin Automation Project Blueprint Markdown files. Keeping them versioned with the code makes it easy to reference them during development.

    Project task board: Consider using GitHub Projects (or Issues) to mirror the phases and tasks described below. Each task can be an issue linked to a project board column (Phase 1 to Phase 5). Copy the tasks verbatim from the blueprint so they are tracked in your issue tracker.

    CI configuration: Add or update .github/workflows/ to include pytest and linting with coverage requirements (≥90 %). This ensures that tasks related to reliability are enforced automatically
    GitHub
    .

    Packaging files: If distributing on PyPI, set up pyproject.toml or setup.cfg according to the blueprint’s release preparation guidelines
    GitHub
    .

    Placeholders for secrets: Remove any plaintext credentials. Use environment variables or the keyring library as the blueprint suggests
    GitHub
    . Update .env.example to guide users on required variables (e.g., Garmin username/password, Slack webhook).

4. Remaining Work Phases and Key Tasks

Use the following checklist (adapted from the blueprint) to populate your GitHub issues or ChatGPT task list. Check off each item as you proceed.
Phase 1 – Hardening & Backlog Cleanup

Add a --dry‑run option to the CLI that performs the fetch and transformation without writing files or sending Slack messages
GitHub
.

Implement robust rate‑limit handling in garmin_client.fetch_workouts: catch HTTP 429, read the Retry‑After header and apply exponential back‑off
GitHub
.

Replace plain .env secrets with secure storage (OS keyring or alternative)
GitHub
.

Enforce idempotent writes by skipping or overwriting duplicate entries when writing to CSV
GitHub
.

Improve error handling by wrapping network calls and logging failures to error.log
GitHub
.

    Configure GitHub Actions to run tests and linting on each push and raise coverage enforcement to 90 %
    GitHub
    .

Phase 2 – Advanced Analytics Integration

Extend analytics.py to compute weekly totals, long‑run per week, polarization metrics, taper readiness and ATL/CTL/TSB
GitHub
.

Create synthetic datasets for each metric and write unit tests to verify calculations
GitHub
.

Update Slack/console summaries to include new metrics (e.g., mileage change, monotony index, polarization percentage)
GitHub
.

    Write chart generation functions for each metric using Matplotlib and ensure charts are saved as PNGs
    GitHub
    .

Phase 3 – CLI & UX Enhancements

Add colored output with accessible palettes (WCAG‑AA compliant) using rich or Click styles, plus a --no‑color flag
GitHub
.

Introduce a --json flag to output summaries as machine‑readable JSON
GitHub
.

Implement a progress indicator (progress bar or spinner) when fetching data
GitHub
.

    Improve --help messages and user guidance for error scenarios
    GitHub
    .

Phase 4 – Visualization & Reporting

Finalize plotting functions and ensure they can run as part of the CLI or a separate sub‑command
GitHub
.

Evaluate generating an HTML report that embeds charts for a richer training overview
GitHub
.

Optimize performance of rolling calculations and chart generation for larger datasets
GitHub
.

    Update Slack messages (if used) to mention when charts are generated
    GitHub
    .

Phase 5 – Documentation & Release Preparation

Write a comprehensive README.md covering installation, configuration, usage examples and summary of outputs
GitHub
.

Keep CHANGELOG.md up to date with all changes since the initial version
GitHub
.

Finalize packaging metadata (pyproject.toml/setup.cfg) and ensure entry points for the CLI are correctly specified
GitHub
.

Test the tool on multiple operating systems (e.g. macOS, Linux, Windows) to ensure cross‑platform compatibility
GitHub
.

Provide scheduling examples (cron or Windows Task Scheduler) in the docs
GitHub
.

    Tag the repository as v1.0 and write release notes summarizing features and improvements
    GitHub
    .

5. Stretch Goals (Post‑v1.0)

After completing v1.0, consider expanding the project with additional capabilities outlined in the blueprint:

    Local Web Dashboard: Build a lightweight Flask app or static site to display the training log and analytics interactively
    GitHub
    .

    SQLite Query Interface: Provide a CLI or text‑based UI for running SQL queries against the optional SQLite mirror
    GitHub
    .

    Jupyter Notebook Integration: Refactor code to be importable and supply example notebooks for custom analysis
    GitHub
    .

    Cloud Integration & Alerts: Explore running the sync in the cloud (AWS Lambda or GitHub Actions cron) and sending notifications via email or other channels
    GitHub
    .

    Multi‑User Support: Generalize the tool for multiple Garmin accounts or additional data sources such as Strava or Fitbit
    GitHub
    .

These enhancements are optional but provide a roadmap for future development if you wish to take the project beyond its initial scope.