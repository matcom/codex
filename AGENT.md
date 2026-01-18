To help any AI coding agent understand and contribute effectively to **The Algorithm Codex**, we will create an `AGENT.md` file. This document outlines the project's unique "literate programming" architecture and established coding standards.

# AGENT.md: Guidelines for AI Coding Agents

Welcome to **The Algorithm Codex**. This document provides the necessary context for AI agents to contribute code and prose while maintaining the project's integrity.

## 1. Literate Programming with `illiterate`

The primary source of truth for this project is the documentation located in `docs/`. We use a tool called **[illiterate](https://github.com/apiad/illiterate)** to extract code from Markdown files and generate the Python source and test suites.

### How to export code

To export a block of code to a specific file, use the following syntax in Markdown:

```markdown
    ```python {export=path/to/target_file.py}
    # Your code here
    ```
```

* **Extraction**: Running `make source` triggers `illiterate`, which scans the `docs/` directory and writes the code blocks to their respective paths in `src/` or `tests/`.
* **Append Mode**: Multiple blocks can export to the same file; `illiterate` will append them in the order they appear in the documentation.
* **Constraint**: Never edit files in `src/` or `tests/` directly. Always modify the corresponding `.md` file in `docs/` and run `make source` to sync the changes.

## 2. Project Structure

* `docs/`: Contains the narrative and the source code (in Markdown).
* `index.qmd`: The book's preface and roadmap.
* `01_search.md`, etc.: Individual chapters.


* `src/codex/`: The generated Python package.
* `types.py`: Contains core protocols like `Ordering[T]` and `default_order`.


* `tests/`: The generated test suite.
* `makefile`: Use `make source` to generate code, `make tests` to run `pytest`, and `make docs` to render the book.

## 3. Coding Standards

* **Python Version**: Use Python 3.13+ features, including modern generic syntax (e.g., `def func[T](...)`).
* **Type Hinting**: All functions must be fully typed. Use `Sequence` instead of `list` for input parameters to remain generic.
* **Ordering Protocol**: For any algorithm involving comparisons, use the `Ordering[T]` type alias and `default_order` provided in `codex.types`.
* **Functional Style**: Prefer pure functions and minimal class usage. Classes should primarily serve as simple data stores.

## 4. Writing Style for Explanations

The goal of the Codex is to build intuition before implementation.

* **The "Why" First**: Before presenting code, explain the problem and the core intuition behind the solution.
* **Back-of-the-envelope Analysis**: Provide high-level time and space complexity analysis (, , etc.) for every major algorithm.
* **Simplicity over Micro-optimization**: Avoid language-specific hacks or loop unrolling. Focus on algorithmic efficiency—speed should come from the algorithm's structure, not runtime tricks.
* **Incremental Learning**: Introduce simpler concepts first and use them as building blocks for more complex chapters.

## 5. Typical Workflow for Agents

1. Identify the target chapter in `docs/` or create a new one.
2. Write the narrative explanation in Markdown.
3. Insert code blocks with the `{export=...}` attribute for both the implementation and its corresponding test.
4. Run `make source` to generate the `.py` files.
5. Run `make tests` to verify the implementation.
6. Update `_quarto.yml` if a new chapter was added.
