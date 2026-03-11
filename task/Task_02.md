# Task 2 — Requirements Engineering (Stakeholders, Context, Interfaces, Personas, User Stories, Requirements)

## Deliverables to produce
Complete the template file located at:

**`../doc/02_RequirementsEngineering.md`**

The file contains the required sections and tables. You must fill in all missing content by adding rows to the tables and, where appropriate, adding short explanatory text that motivates your modelling choices.

You may add additional paragraphs, but **do not remove or rename** the existing section headings and tables.

## Baseline scope reference
All work must be consistent with the current baseline system description:

- **`../doc/Participium.md`**

Do not assume additional features that are not supported by the baseline unless you clearly state them as **assumptions** (and then use them consistently across the whole document).

## General guidance

### Avoid low-effort AI output
You are free to use any tools and technologies you want (including AI assistants), or even produce additional deliverables in other more graphical formats.  
However, you must use these tools **properly**: review and verify the generated outputs, refine prompts with intent, and ensure the final result reflects your own reasoning. Do **not** blindly copy and paste unchecked content.

### Motivate your choices
Beyond filling in the tables, you are explicitly allowed—and encouraged—to add short explanatory sections to justify:
- scope decisions,
- modelling choices,
- priorities and trade-offs,
- wording and verification strategies for requirements.

### Be coherent
If you introduce assumptions that affect your work, you must carry them consistently through the entire document. Assumptions must be carried consistently across the entire deliverable and must remain consistent with the other project documents.

---

## 1) Stakeholders

### What you must provide
Create a stakeholder register capturing the relevant actors and organizations surrounding Participium. For each stakeholder, describe:
- role in the system,
- goals and expected value,
- main concerns (e.g., usability, transparency, workload, privacy),
- relative influence/priority.

### Expectations
A stakeholder analysis should:
- identify all parties that can **affect** the system or are **affected** by it,
- distinguish clearly between different stakeholder categories avoiding duplication and ambiguity,
- express stakeholder goals and concerns in a way that can later drive user stories and requirements,

You are encouraged to add short notes to justify why each stakeholder matters and what decisions it may influence.


---

## 2) Context Diagram

### What you must provide
Draw the system context diagram, showing:
- the system boundary (Participium),
- primary external actors,
- external systems/services that exchange data with Participium,
- high-level interaction flows (what information crosses the boundary).

### Expectations
The diagram must be consistent with:
- the stakeholder list,
- the interface list,
- the baseline system description.

---

## 3) Interfaces

### What you must provide
List the system interfaces, including:
- user-facing interfaces (web UI and any role-specific dashboards),
- external system interfaces (e.g., map services, email delivery, file storage for attachments),
- the physical channel (device/network) and the logical interface (UI/API/protocol).

### Expectations
Interfaces must be consistent with the context diagram. Clarify what each interface exchanges (data/events) and why it is needed.

---

## 4) Personas

### What you must provide
Define personas representing the key user groups of Participium. For each persona:
- background and context of use,
- goals,
- constraints,
- typical device and usage setting.

### Expectations
Personas must:
- represent distinct user types with different goals/constraints,
- be realistic and grounded in the intended system context,
- support user story writing by clarifying motivations and limitations,
- avoid being a restatement of requirements (personas are descriptive, not prescriptive)

Personas are not requirements: they are useful to make user stories and requirements realistic and coherent.

### Example persona

**Persona ID:** PER-01  
**Name:** Marco R.  
**Role:** Registered citizen (occasional reporter)

**Background / context**  
Marco is a 38-year-old office worker who commutes daily across the city using public transport and walking. He is comfortable with basic mobile apps but does not enjoy long forms or complex workflows. He typically notices issues while moving (e.g., broken streetlights, road obstacles) and wants to report them quickly without spending much time.

**Goals**
- Submit a report in less than 2 minutes from a smartphone.
- Attach one photo and select the location with minimal effort.
- Receive clear updates on what happens next and when the issue is resolved.
- Avoid sharing personal details publicly.

**Constraints**
- Limited time and attention while commuting; frequent interruptions.
- Uncertainty about which category to choose.
- Low tolerance for repeated data entry and unclear error messages.
- Concern about privacy and being identified in public views.

**Devices / usage setting**  
Mostly a smartphone on mobile data, often outdoors with variable connectivity; sometimes uses a laptop at home to check updates.

**Accessibility / additional needs**  
Prefers large tap targets and readable text; benefits from concise language and a clear “next step” indication after submission.

---

## 5) User Stories

### What you must provide
Write a set of user stories that describe how different personas interact with Participium.

Each user story should:
- identify the persona/role,
- use the standard form: **As a … I want … so that …**

### Expectations
User stories should:
- be consistent with persona goals and constraints,
- collectively cover the main system capabilities within scope,
- avoid overlapping duplicates; if similar, they should be merged or differentiated

---

## 6) Functional Requirements (FR)

### What you must provide
Derive functional requirements from the user stories and baseline scope.

Each functional requirement must:
- use a clear “**The system shall …**” statement,
- include a priority,
- reference the user stories it supports (traceability).

### Expectations
Functional requirements must be:
- non-duplicated and unambiguous,
- consistent with the interfaces and context diagram,
- implementable in principle (even if implementation is not requested at this stage).

---

## 7) Non-Functional Requirements (NFR)

### What you must provide
Define non-functional requirements that are relevant for Participium.

Each NFR should include:
- a clear statement,
- a measurable target or proxy metric when possible,
- a verification method (test/inspection/analysis),
- priority.

### Expectations
Non-functional requirements should:
- avoid vague terms (“fast”, “secure”, “user-friendly”) without measurable clarification,
- are stated in a way that supports verification,
- are consistent with the assumed operational context and constraints,
- highlight key trade-offs when multiple quality attributes compete
