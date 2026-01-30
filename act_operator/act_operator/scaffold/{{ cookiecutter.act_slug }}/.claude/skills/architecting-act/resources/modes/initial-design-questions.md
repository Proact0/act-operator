# Mode 1: Initial Act & Cast Design Questions

Use when CLAUDE.md doesn't exist (initial project setup after `act new`).

---

## Context Analysis (Before Asking)

**First, analyze available context:**
1. Read user's initial request for project description
2. Check cookiecutter template values (act name: {{ cookiecutter.act_name }}, cast name: {{ cookiecutter.cast_name }})
3. Identify what information is already provided vs. missing

**Decision Matrix:**
| Information | Source | If Found → Skip Question |
|-------------|--------|-------------------------|
| Act Purpose | User request | Q1 |
| Cast Name | {{ cookiecutter.cast_name }} | Q2 |
| Cast Goal | User request | Q3 |
| I/O Types | User request | Q4 |

---

## Questions (Ask Only If Needed)

### Q1: Act Purpose

**Condition**:
- Skip if: User's initial request clearly states project purpose
- Required when: Purpose unclear or too vague

**AskUserQuestion Format**:
```json
{
  "question": "What is the main purpose of this project?",
  "header": "Act Purpose",
  "options": [
    {"label": "Customer Support Automation", "description": "Handle inquiries, FAQ responses, ticket routing"},
    {"label": "Document Processing Pipeline", "description": "Parse documents, extract info, generate summaries"},
    {"label": "Data Analysis/Research", "description": "Collect data, analyze, derive insights"},
    {"label": "Content Generation", "description": "Auto-generate text, images, code, etc."}
  ],
  "multiSelect": false
}
```

**Follow-up**: If "Other" selected → Use provided text as Act purpose

---

### Q2: Initial Cast Identification

**Condition**:
- Skip if: Cast name already provided by cookiecutter template ({{ cookiecutter.cast_name }})
- Required when: Clarification needed about cast role

**Note**: This question is typically skipped as `act new` already prompts for cast name.

**AskUserQuestion Format** (if clarification needed):
```json
{
  "question": "I see you created a cast called '{{ cookiecutter.cast_name }}'. What should this cast accomplish?",
  "header": "Cast Role Clarification",
  "options": [
    {"label": "Process and transform data", "description": "Take input, apply logic, produce output"},
    {"label": "Coordinate multiple tasks", "description": "Orchestrate workflow between components"},
    {"label": "Interface with external systems", "description": "API calls, database operations, integrations"},
    {"label": "Make decisions/classifications", "description": "Route, categorize, or decide next actions"}
  ],
  "multiSelect": false
}
```

**Follow-up**: If "Other" selected → Use provided text as Cast role description

---

### Q3: Cast Goal

**Condition**:
- Skip if: Cast goal clear from Act purpose and cast name
- Required when: Multiple possible interpretations exist

**AskUserQuestion Format**:
```json
{
  "question": "What is the main goal of {{ cookiecutter.cast_name }} Cast?",
  "header": "Cast Goal",
  "options": [
    {"label": "Data Collection/Ingestion", "description": "Fetch and process data from external sources"},
    {"label": "Analysis/Processing", "description": "Analyze and transform input data"},
    {"label": "Generation/Output", "description": "Create new content or results"},
    {"label": "Routing/Coordination", "description": "Classify input and dispatch to appropriate handlers"}
  ],
  "multiSelect": false
}
```

**Follow-up**: If "Other" selected → Use provided text as Cast goal

---

### Q4: Input/Output Types

**Condition**:
- Skip if: I/O types inferable from cast goal
- Required when: Custom or complex I/O needed

**AskUserQuestion Format** (ask as two separate questions):

**Input Type:**
```json
{
  "question": "What is the input data type?",
  "header": "Input Type",
  "options": [
    {"label": "Text (str)", "description": "User questions, document content, etc."},
    {"label": "File/Document", "description": "PDF, Word, images, etc."},
    {"label": "Structured Data", "description": "JSON, dict, database records"},
    {"label": "Multimedia", "description": "Images, audio, video"}
  ],
  "multiSelect": true
}
```

**Output Type:**
```json
{
  "question": "What is the output data type?",
  "header": "Output Type",
  "options": [
    {"label": "Text Response", "description": "Generated text, summaries, answers"},
    {"label": "Structured Result", "description": "JSON, classification, metadata"},
    {"label": "File/Document", "description": "Generated documents, reports"},
    {"label": "Action/Command", "description": "Tasks to execute, API call results"}
  ],
  "multiSelect": true
}
```

**Note**: These can be asked together (up to 4 questions at once with AskUserQuestion).

---

### Q5: Constraints

**Condition**:
- Always ask: Performance constraints affect architecture decisions

**AskUserQuestion Format**:
```json
{
  "question": "Are there any performance constraints?",
  "header": "Constraints",
  "options": [
    {"label": "Low Latency (<10s)", "description": "Real-time response needed, user waiting"},
    {"label": "Normal (<60s)", "description": "Moderate response time, batch allowed"},
    {"label": "Long-running (>60s)", "description": "Complex processing, background jobs"},
    {"label": "Cost Optimization", "description": "Minimize API calls, prefer cheaper models"}
  ],
  "multiSelect": true
}
```

---

## After Questions: Summarize

**Template:**
```
"Got it. Here's what I understand:

**Act:**
- **Purpose:** [project goal]

**Cast: {{ cookiecutter.cast_snake }}**
- **Goal:** [cast goal]
- **Input:** [input]
- **Output:** [output]
- **Constraints:** [constraints]

Is this correct?"
```

**Wait for confirmation before proceeding to pattern selection.**