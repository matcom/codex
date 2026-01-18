# The Algorithm Codex

**The Algorithm Codex** is a comprehensive repository of reference implementations for common and advanced algorithms in computer science. Designed as a companion for computer science students and professionals, it provides clean, modern Python 3.13+ implementations while emphasizing clarity, intuition, and algorithmic efficiency.

## Literate Programming

This project follows a **literate programming** philosophy. Unlike traditional software projects, the primary source of truth is the book itself, located in the `docs/` directory.

* **Book-to-Code:** The Python source code in the `src/` directory is automatically generated from the Markdown files in the `docs/` folder.
* **Narrative Driven:** Every implementation is surrounded by prose that explains the intuition behind the algorithm and provides a "back-of-the-envelope" cost analysis.
* **Tooling:** We use [illiterate](https://github.com/apiad/illiterate) to extract code blocks from the documentation and [Quarto](https://quarto.org/) to render the book in HTML and PDF formats.

## Project Structure

* `docs/`: Contains the Markdown and Quarto files that make up the book.
* `src/codex/`: The generated Python package.
* `tests/`: A comprehensive test suite using `pytest` to ensure all implementations are correct.
* `makefile`: Automation for building the source, rendering docs, and running tests.
* `pyproject.toml` & `uv.lock`: Python project metadata and dependency management.

## Roadmap

The Codex is organized to build complex ideas on top of simpler ones. The planned content includes:

* **Part I: Searching and Sorting:** Basic search (linear, binary) and fundamental sorting algorithms.
* **Part II: Fundamental Data Structures:** Linked lists, stacks, queues, and hashing.
* **Part III: Trees:** Binary search trees, heaps, tries, and balanced trees.
* **Part IV: Graphs:** Traversal, shortest paths, spanning trees, and flow networks.
* **Part V: Dynamic Programming & Greedy Algorithms:** Paradigm-shifting problem-solving techniques.
* **Part VI: Specialized Domains:** Computational geometry, number theory, and game theory.
* **Part VII: Advanced Complexity:** NP-completeness, approximation algorithms, and randomized algorithms.

## Development

To set up the development environment, ensure you have Python 3.13+ and the `uv` package manager installed.

* **Extract source from docs:** `make source`
* **Run tests:** `make tests`
* **Render book:** `make docs`
* **Live development:** `make dev` (watches for doc changes to rebuild source automatically)

## Licenses

* **Book Content:** [CC-BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). You are free to share and adapt the material for non-commercial purposes, provided you give appropriate credit and distribute your contributions under the same license.
* **Source Code:** [MIT License](https://opensource.org/licenses/MIT). The implementations can be used for any purpose, including commercial software.

## About the Author

The Algorithm Codex is written and maintained by **Alejandro Piad Morffis, Ph.D.**, a Computer Science professor and researcher. For updates on the Codex and other explorations into the science of computation, subscribe to [The Computist Journal](https://blog.apiad.net).