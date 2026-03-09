# Execution Plan: Literate Programming and Style Integration

This plan outlines the steps to integrate literate programming protocols and specific stylistic requirements into the project's Gemini CLI configuration.

## Objective
Harmonize the project's coding and writing standards by integrating the "illiterate" programming protocol and structural requirements into the AI agent's core instructions (`GEMINI.md`), command definitions (`draft.toml`, `revise.toml`), and the `style-guide.md`.

## Architectural Impact
- **Single Source of Truth**: Establishes the `docs/` directory as the primary source for both prose and code.
- **Workflow Enforcement**: Formalizes the TDD and literate programming cycle (Edit Docs -> `make source` -> `make tests`).
- **Standardized Content**: Ensures all algorithmic content follows a consistent hierarchy (Parts > Chapters > Algorithms) and includes mandatory complexity analysis.

## File Operations
- **Modify**: `GEMINI.md`
- **Modify**: `.gemini/commands/draft.toml`
- **Modify**: `.gemini/commands/revise.toml`
- **Modify**: `.gemini/style-guide.md`

## Step-by-Step Execution

### Step 1: Update `GEMINI.md` with Engineering Protocol
Integrate the core instructions from `AGENT.md` into the project's main context file.
- **Content to Add**:
    - **Literate Programming**: Definition of the `illiterate` protocol and the `{export=...}` syntax.
    - **Prohibited Actions**: Explicitly forbid direct editing of `src/` and `tests/`.
    - **Python Standards**: Mandate Python 3.13+ generic syntax and the use of `Ordering[T]` from `codex.types`.
    - **Workflow**: Define the cycle of using `make source` and `make tests`.

### Step 2: Update `style-guide.md` for Hierarchy and Rigor
Enforce the structural and technical requirements for "The Algorithm Codex".
- **Structural Hierarchy**: Define the mandatory structure: **Parts** (thematic groups) > **Chapters** (specific problems/areas) > **Algorithms** (individual implementations).
- **Narrative Requirements**:
    - "Intuition First": Explain the problem and core concept before showing code.
    - Mandatory "Complexity Analysis": Every algorithm must include a Big O analysis for time and space.
    - Mandatory "Correctness Proof/Sketch": Briefly explain why the algorithm works.
- **Code Standards**:
    - All code must be in `{export=...}` blocks.
    - All code must include corresponding tests (also exported).

### Step 3: Enhance `draft.toml` for Literate Drafting
Update the drafting workflow to naturally produce literate programming documents.
- **Phase 3 (Outline)**: Update to ensure the outline follows the Parts > Chapters > Algorithms hierarchy.
- **Phase 5 (Drafting)**: Explicitly instruct the agent to generate `{export=...}` blocks for both implementation and tests.
- **Post-Drafting**: Remind the agent to suggest running `make source` and `make tests` after creating a new draft in `docs/`.

### Step 4: Enhance `revise.toml` for Rigorous Review
Add a new dimension to the revision process focusing on the literate protocol and technical depth.
- **Phase 2 (Analysis)**: Add a sub-phase for **Literate & Technical Audit**:
    - Verify all code blocks have correct `{export=...}` paths.
    - Check for prose/code alignment (does the prose explain the actual code?).
    - Validate presence of complexity analysis and correctness sketches.
    - Check for Python 3.13+ generic syntax compliance.

## Testing and Validation
1. **Linting the Plan**: Ensure all file paths and command names are correct.
2. **Dry Run (Manual Verification)**:
    - Verify that `GEMINI.md` now contains all necessary context from `AGENT.md`.
    - Check that `style-guide.md` clearly states the Big O and hierarchy requirements.
    - Confirm `draft` and `revise` commands' prompts include the new literate instructions.
3. **End-to-End Workflow Test (Post-Implementation)**:
    - Run `/draft` for a simple algorithm (e.g., "Bubble Sort").
    - Verify the output has `{export=...}` blocks and the correct hierarchy.
    - Run `/revise` on the generated draft and ensure it flags any missing complexity analysis or literate syntax errors.
