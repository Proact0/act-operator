# Mode 3: Extract Sub-Cast Questions

Use when analyzing existing cast for complexity and suggesting extraction.

---

## Step 1: Analyze Current Cast

**Read the cast-specific CLAUDE.md** (`/casts/{cast_snake_name}/CLAUDE.md`) and analyze:
- Count nodes (excluding START/END)
- Identify repeated patterns
- Check for isolated sections
- Look for reusable logic across multiple casts (check root `/CLAUDE.md` Casts table and other cast files)

**Complexity indicators:**
- Node count > 7
- Repeated node sequences
- Shared logic across multiple casts
- Isolated section with clear input/output

---

## When to Suggest Extraction

**Only suggest if:**
- Node count > 7
- Repeated node sequences found
- Shared logic across multiple casts
- Isolated section with clear input/output

**Do NOT suggest if:**
- Cast is simple (≤7 nodes)
- No clear extraction boundary
- Logic is tightly coupled

---

## Questions

### Q1: Complexity Check & Proceed Confirmation

**Present analysis first, then ask for confirmation:**

**Analysis Template:**
```
"I'm analyzing Cast: {cast_name}.

**Current complexity:**
- Node count: {X} nodes
- [Additional findings: e.g., repeated patterns, isolated sections]
```

**AskUserQuestion Format**:
```json
{
  "question": "Should we consider extracting any sections to reduce complexity?",
  "header": "Extract?",
  "options": [
    {"label": "Yes, proceed", "description": "Review extraction proposal and select nodes"},
    {"label": "No, keep as-is", "description": "Current structure is acceptable"},
    {"label": "Need more info", "description": "Explain complexity implications first"}
  ],
  "multiSelect": false
}
```

**Follow-up**:
- If "Yes, proceed" → Continue to Q2
- If "No, keep as-is" → End extraction flow
- If "Need more info" → Explain complexity impact, then re-ask

---

### Q2: Node Selection for Extraction

**Present extraction proposal with specific nodes:**

**Proposal Template:**
```
"I notice [specific pattern/section]:

**Candidate nodes for extraction:**
- {NodeA}: [brief description]
- {NodeB}: [brief description]
- {NodeC}: [brief description]

**Suggested Sub-Cast name:** {ProposedName}

**Benefits:**
- Reduces main cast from {X} to {Y} nodes
- Reusable in [other casts if applicable]
- Clearer separation of concerns
```

**AskUserQuestion Format**:
```json
{
  "question": "Which nodes should be extracted to the sub-cast?",
  "header": "Nodes",
  "options": [
    {"label": "{NodeA}", "description": "[NodeA description]"},
    {"label": "{NodeB}", "description": "[NodeB description]"},
    {"label": "{NodeC}", "description": "[NodeC description]"},
    {"label": "{NodeD}", "description": "[NodeD description]"}
  ],
  "multiSelect": true
}
```

**Note**: Dynamically populate options with actual nodes from analysis. Use multiSelect to allow selecting multiple nodes.

**Follow-up**: If "Other" selected → Ask user to specify which nodes to extract

---

### Q3: Sub-Cast Purpose

**Condition**:
- Skip if: Purpose clear from selected nodes
- Required when: Clarification needed for extracted functionality

**AskUserQuestion Format**:
```json
{
  "question": "What is the primary purpose of this sub-cast?",
  "header": "Purpose",
  "options": [
    {"label": "Data Preprocessing", "description": "Clean, validate, transform input data"},
    {"label": "Core Processing Logic", "description": "Main business logic extraction"},
    {"label": "Output Formatting", "description": "Format and structure output data"},
    {"label": "Shared Utility", "description": "Reusable logic for multiple casts"}
  ],
  "multiSelect": false
}
```

---

### Q4: Input/Output Verification

**Present inferred I/O and ask for confirmation:**

**AskUserQuestion Format**:
```json
{
  "question": "I've inferred the following I/O for the sub-cast. Is this correct?",
  "header": "I/O Check",
  "options": [
    {"label": "Yes, correct", "description": "Input: [inferred input] | Output: [inferred output]"},
    {"label": "Modify input", "description": "I need to specify different input"},
    {"label": "Modify output", "description": "I need to specify different output"},
    {"label": "Modify both", "description": "Both input and output need changes"}
  ],
  "multiSelect": false
}
```

**Follow-up**:
- If "Yes, correct" → Proceed to update plan
- If "Modify input/output/both" → Ask user to specify changes

---

## After Confirmation: Update Plan

**Explain next steps:**
```
"I'll create:

1. **New Sub-Cast: {name}**
   - Extract {X} nodes from {parent_cast}
   - Add to Casts table in root `/CLAUDE.md`
   - Create `/casts/{subcast_snake_name}/CLAUDE.md` with extracted specification

2. **Update {parent_cast}**
   - Replace extracted nodes with sub-cast invocation node in `/casts/{parent_cast_snake_name}/CLAUDE.md`
   - Update diagram

This will reduce {parent_cast} complexity and make the logic reusable.
```

**Final Confirmation AskUserQuestion**:
```json
{
  "question": "Proceed with sub-cast extraction?",
  "header": "Confirm",
  "options": [
    {"label": "Yes, create sub-cast", "description": "Proceed with extraction as described"},
    {"label": "Modify plan", "description": "I want to change something first"},
    {"label": "Cancel", "description": "Don't extract, keep current structure"}
  ],
  "multiSelect": false
}
```

**Wait for final confirmation before designing sub-cast.**