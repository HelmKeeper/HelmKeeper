# Contributing to HelmKeeper

Thank you for your interest in contributing to HelmKeeper! We want to make contributing to this project as easy and transparent as possible.

## Getting Started

1.  **Fork** the repository on GitHub.
2.  **Clone** your fork locally.
    ```bash
    git clone https://github.com/your-username/HelmKeeper.git
    cd HelmKeeper
    ```
3.  **Install dependencies**:

    ```bash
    poetry install
    ```

4.  **Install system tools** (Optional, for easy commands):
    - Make (optional)

## Development Workflow

1.  Create a branch for your feature or bugfix: `git checkout -b feature/amazing-feature`.
2.  Write your code and **add tests** in the `test/` directory.
3.  Run the tests to ensure everything is working:
    ```bash
    make test
    # or
    poetry run pytest
    ```
4.  Ensure your code style is consistent.

## Submitting a Pull Request

1.  Push your branch to GitHub.
2.  Open a Pull Request against the `main` branch.
3.  Provide a clear description of the problem and solution.
4.  Wait for review!

## Code of Conduct

Please be respectful and kind to other contributors.
