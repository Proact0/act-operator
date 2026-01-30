# Mode 2: Add New Cast Questions

Use when CLAUDE.md files exist (distributed structure) and adding a new cast to the Act.

---

## Step 1: Read Existing Context

**First, read CLAUDE.md files** to understand:
- **Root `/CLAUDE.md`**: Act Overview, purpose, and Casts table
- **Existing cast CLAUDE.md files** (`/casts/{cast_snake_name}/CLAUDE.md`): Each cast's architecture and responsibilities

---

## Context Analysis (Before Asking)

**Analyze available context:**
1. Read user's request for the new cast
2. Check existing casts from CLAUDE.md Casts table
3. Identify what information is already provided vs. missing

**Decision Matrix:**
| Information | Source | If Found → Skip Question |
|-------------|--------|-------------------------|
| New Cast Purpose | User request | Q1 |
| Cast Goal | User request | Q2 |
| Relationship | User request context | Q3 |
| I/O Types | Inferable from goal | Q4 |

---

## Questions (Ask Only If Needed)

### Q1: New Cast Purpose

**Condition**:
- Skip if: User's request clearly states new cast purpose
- Required when: Purpose unclear or multiple interpretations possible

**Context to include**: "I see your Act already has these casts: [list existing casts]."

**AskUserQuestion Format**:
```json
{
  "question": "What should the new cast accomplish?",
  "header": "Cast Purpose",
  "options": [
    {"label": "Data Ingestion", "description": "Fetch and preprocess data from external sources"},
    {"label": "Batch Processing", "description": "Process multiple items in parallel or sequence"},
    {"label": "Validation/Sanitization", "description": "Validate and clean input data"},
    {"label": "Specialized Handler", "description": "Handle specific domain or use case"}
  ],
  "multiSelect": false
}
```

**Follow-up**: If "Other" selected → Use provided text as Cast purpose

---

### Q2: Cast Goal

**Condition**:
- Skip if: Cast goal clear from Q1 answer or user request
- Required when: Need specific clarification

**AskUserQuestion Format**:
```json
{
  "question": "What should this new cast do? (specific goal)",
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

---

### Q3: Relationship to Existing Casts

**Condition**:
- Skip if: Relationship clear from user request context
- Required when: Multiple existing casts and relationship unclear

**AskUserQuestion Format**:
```json
{
  "question": "How does this cast relate to existing ones?",
  "header": "Relationship",
  "options": [
    {"label": "Independent", "description": "Runs separately, no direct connection to other casts"},
    {"label": "Sequential", "description": "Runs after another cast, receives its output"},
    {"label": "Shared Logic (Sub-Cast)", "description": "Provides reusable logic used by multiple casts"},
    {"label": "Parallel", "description": "Runs alongside other casts, shares data"}
  ],
  "multiSelect": false
}
```

**Follow-up based on answer:**
- If "Sequential" → Ask: "Which cast runs before it? What data is passed?"
- If "Shared Logic" → Ask: "Which casts will use this sub-cast?"
- If "Other" → Use provided text to understand relationship

---

### Q4: Input/Output Types

**Condition**:
- Skip if: I/O types inferable from cast goal and relationship
- Required when: Custom or complex I/O needed

**AskUserQuestion Format** (ask as two separate questions):

**Input Type:**
```json
{
  "question": "What is the input data type?",
  "header": "Input Type",
  "options": [
    {"label": "Text (str)", "description": "User questions, document content, etc."},
    {"label": "File/Document", "description": "PDF, Word, images, file paths"},
    {"label": "Structured Data", "description": "JSON, dict, database records"},
    {"label": "Request Batch", "description": "Multiple items to process"}
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
    {"label": "Processed Data", "description": "Transformed/validated data for next step"},
    {"label": "Action/Command", "description": "Tasks to execute, API call results"}
  ],
  "multiSelect": true
}
```

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

**New Cast: {cast_name}**
- **Goal:** [cast goal]
- **Relationship:** [how it relates to existing casts]
- **Input:** [input]
- **Output:** [output]
- **Constraints:** [constraints]
```

**Wait for confirmation before proceeding to pattern selection.**