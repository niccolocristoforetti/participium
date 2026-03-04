# Task 1 — Project Management Artifacts (PBS, WBS, Gantt, Risk Management)

## Deliverable to produce
Complete the template file located at:

**`../doc/01_ProjectManagement.md`**

The file already contains the required sections and tables. You must **fill in the missing content** by adding rows to the tables and, where appropriate, adding short explanatory text that motivates and justifies your planning choices.

You may add additional paragraphs, but **do not remove or rename** the existing section headings and tables.

## General guidance

### Avoid low-effort AI output
You are free to use any tools and technologies you want (including AI assistants), or even produce additional deliverables in other more graphical formats.  
However, you must use these tools **properly**: review and verify the generated outputs, refine prompts with intent, and ensure the final result reflects your own reasoning. Do **not** blindly copy and paste unchecked content.

### Motivate your choices
Beyond filling in the tables, you are explicitly allowed—and encouraged—to add short explanatory sections (e.g., **Rationale**, **Assumptions**, **Notes**) to justify:
- scope decisions,
- decomposition structure,
- scheduling strategy and dependencies,
- probability/impact ratings and mitigation actions.

### Be coherent
If you introduce assumptions that affect your work, you must carry them consistently through the entire document. Assumptions must be reflected in the whole deliverable.

### Make estimates plausible and grounded
When you provide durations and milestones, your estimates must be **realistic** and consistent with the baseline assumptions you declare (e.g., scope boundaries, team size, parallelism, external dependencies). If an assumption changes, revisit the schedule and update it accordingly.

Where your level of detail allows it, you may reference **real technologies** (frameworks, architectural patterns, infrastructure and deployment options, storage solutions, third-party services) to justify choices and timelines. Using current, widely adopted technologies as concrete examples is appreciated, especially when it helps explain trade-offs, constraints, and impacts on effort and schedule.

---

## 1) Product Breakdown Structure (PBS)

### What you must provide
Populate the PBS table by defining a hierarchical set of **deliverables** for Participium.

A PBS entry must represent an **observable output** (something that can be reviewed or accepted), not an activity. Each deliverable must:
- have a **unique ID**,
- have a clear **name/description**,
- be classified by **Type**,
- optionally include **Notes** to clarify scope or boundaries.

### Expectations
Your PBS must cover the full baseline scope of Participium at the level of deliverables. Deliverables should be decomposed until the leaves are specific enough to be assessed.

You are encouraged to add a short paragraph after the table explaining:
- how you interpreted the scope,
- the rationale behind your decomposition,
- any assumptions that influenced what you included/excluded.

---

## 2) Work Breakdown Structure (WBS)

### What you must provide
Populate the WBS table by defining a set of **work packages** required to produce the PBS deliverables.

Each WBS row must:
- have a unique WBS identifier (e.g., `1.0`, `1.1`, `2.0`),
- describe a coherent work package,
- explicitly list the **PBS output IDs** produced by that work package in the “Traced PBS outputs (IDs)” column.

### Expectations
Your WBS must provide complete coverage of the PBS: every PBS deliverable must be produced by at least one work package. Work packages should remain at a **project-management** granularity (not a fine-grained list of micro-tasks), and should be structured to enable scheduling and risk reasoning.

You are encouraged to add a short paragraph after the table explaining:
- why you grouped work the way you did,
- major architectural/organizational assumptions affecting the work split,
- key dependencies you already anticipate from this decomposition.

---

## 3) Gantt Schedule, Dependencies, and Critical Path

### What you must provide
Populate the “Activity table” by listing schedule-level activities derived from the WBS, including:
- **Duration** (choose a consistent unit and keep it consistent),
- **Dependencies** (IDs of predecessor activities),
- **Start** and **End** (dates or time periods consistent with your chosen unit),
- whether the activity is **Critical**,
- whether the activity is a **Milestone**

Then fill the “Critical path” line with the sequence of activity IDs that forms the critical path.

### Expectations
Your schedule must be internally consistent:
- dependencies must reference existing activity IDs,
- the dependency graph must be coherent (no circular dependencies),
- start/end values must respect dependencies,
- the declared critical path must align with your slack/critical markings.

You are encouraged to add a graphical representation of the Gantt schedule as defined in the table and a short explanatory text describing:
- the main scheduling strategy (phases, parallelization),
- why certain activities are on the critical path,
- any constraints/assumptions affecting the timeline (availability, external dependencies, integration complexity).

---

## 4) Risk Management

### What you must provide
Use the provided probability and impact scales (1–5) and compute exposure as `P × I` (range 1–25).

Use **exactly** the following exposure thresholds to assign the risk level:
- **Low**: 1–5
- **Medium**: 6–10
- **High**: 11–16
- **Very High**: >16

Populate the “Risks table” with a set of relevant project risks. Each risk must include:
- a concise risk statement,
- a category (e.g., Technical, Requirements/Scope, Security/Privacy, Operational, External/Third-party, Organizational),
- **P**, **I**, **P×I**, and the corresponding **Level**,
- a concrete **Mitigation / Response strategy** (specific actions, not generic statements).

### Expectations
Risks should be consistent with your PBS/WBS and schedule assumptions. 

Include risks that can materially affect:
- delivery of key deliverables,
- the critical path,
- integration points (e.g., map services, email delivery, optional Telegram integration),
- data handling and privacy/security constraints.

You are encouraged to add a short paragraph summarizing:
- the most critical risks and why,
- how mitigation actions influence the plan (e.g., adding buffer, prototyping, early validation).
