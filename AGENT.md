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

### How to decompose code top-down

Long algorithms must be broken into smaller, narratively-framed pieces. The Codex has two mechanisms for this; the choice between them matters.

**Decomposition policy:**

* **Hard rule.** Any algorithm whose extracted body is longer than ~20 lines must be decomposed. A 50-line monolithic function is a chapter failure regardless of whether the function is correct — the reader can't hold it in their head.
* **Soft rule.** Decompose shorter algorithms too whenever a sub-procedure deserves its own pedagogical paragraph. The cost is one extra block; the benefit is that each conceptual step gets its own narrative beat.

#### Default: real Python subroutines

The default is **real Python subroutines** — each conceptual step is its own `def`, extracted into the same source file via append-mode `{export=...}` blocks. Each block gets its own prose frame.

```markdown
    ```python {export=src/codex/sort/quick.py}
    from typing import Sequence
    from codex.types import Ordering, default_order

    def quicksort[T](items: Sequence[T], order: Ordering[T] = default_order) -> list[T]:
        items = list(items)  # don't mutate the input
        _quicksort(items, 0, len(items), order)
        return items
    ```

    The recursive helper is two cases — a base case that bails on slices of
    length zero or one, and a recursive case that partitions and recurses on
    both halves.

    ```python {export=src/codex/sort/quick.py}
    def _quicksort[T](items: list[T], lo: int, hi: int, order: Ordering[T]) -> None:
        if hi - lo < 2:
            return
        pivot_index = partition(items, lo, hi, order)
        _quicksort(items, lo, pivot_index, order)
        _quicksort(items, pivot_index + 1, hi, order)
    ```

    And the partition step itself…

    ```python {export=src/codex/sort/quick.py}
    def partition[T](items: list[T], lo: int, hi: int, order: Ordering[T]) -> int:
        ...
    ```
```

`partition` is a real function with clear inputs and a clear output — that's what makes subroutines the right call here. The file `src/codex/sort/quick.py` ends up with three function definitions in document order.

#### Reserved: named fragments via `{name=...}` + `<<...>>`

`illiterate` also supports Knuth's CWEB-style named fragments. A code block marked with `{name=fragment_name}` is not extracted directly — it gets spliced in wherever `<<fragment_name>>` appears inside an `{export=...}` block. Fragments can include other fragments (nesting is fine). The fully-expanded code is what lands in `src/`; the chapter is the source of truth.

```markdown
    ```python {export=path/to/file.py}
    def outer():
        # ... outer skeleton ...
        <<inner_step>>
        # ... continues ...
    ```

    ```python {name=inner_step}
    if some_condition:
        break  # exits the outer function's loop
    ```
```

**Use named fragments only when extracting a subroutine would be incorrect** — when the inlined code genuinely cannot be a function. Specifically:

* **Control flow that crosses the boundary** — the fragment contains a `break`, `continue`, or `return` meant to affect the *outer* function. A subroutine can't do that.
* **Shared scope that would be ugly to thread** — the fragment reads or modifies more than two or three locals of its caller, and turning them into parameters + return-tuple would obscure the algorithm.
* **Tight inner loops where call cost matters** — rare in this book (the Codex isn't optimizing raw runtime), but legitimate when the algorithm's character *is* the inner-loop kernel.

When you use a fragment, the reasoning belongs in the chapter prose: *"This step has to live inline because the `break` exits the outer search loop — pulling it out as a function would force a sentinel return value and obscure the algorithm."* If you can't write that sentence, it should be a subroutine, not a fragment.

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
* **Top-down decomposition**: For any algorithm longer than ~20 lines, break it into pieces and frame each with prose. The default is real Python subroutines — separate `def` statements, each in its own `{export=...}` block. Named fragments (`{name=}` + `<<>>`) are reserved for cases where extracting a subroutine would be incorrect (control flow crossing the boundary, shared scope that would be ugly to thread). See §1 "How to decompose code top-down" for the mechanism and the criteria.

## 5. Typical Workflow for Agents

1. Identify the target chapter in `docs/` or create a new one.
2. Write the narrative explanation in Markdown.
3. Insert code blocks with the `{export=...}` attribute for both the implementation and its corresponding test.
4. Run `make source` to generate the `.py` files.
5. Run `make tests` to verify the implementation.
6. Update `_quarto.yml` if a new chapter was added.
