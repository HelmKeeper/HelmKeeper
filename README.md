# HelmKeeper

![License](https://img.shields.io/github/license/marcodasilva/HelmKeeper)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)

**HelmKeeper** is a tool designed to validate Helm charts, check for outdated dependencies, and scan for security vulnerabilities. It ensures your Kubernetes deployments are secure and up-to-date by integrating seamlessly into your CI/CD pipelines.

## Features

- **Dependency Updates**: Checks for newer versions of Helm chart dependencies.
- **Vulnerability Scanning**: Integrates with [OSV](https://osv.dev) to detect security issues in package versions.
- **Chart Validation**: Verifies chart integrity and syntactic correctness using `helm template`.
- **CI/CD Ready**: Supports JSON output and exit codes for pipeline integration.
- **Standardized**: Available as a Docker container and a GitHub Action.

## Installation & Usage

### 1. Using Docker (Recommended)

No installation required using Docker. The image is hosted on **Docker Hub**.

```bash
docker run --rm -v $(pwd):/apps marcodasilva/helmkeeper:latest /apps/my-chart --check
```

### 2. GitHub Actions

Use HelmKeeper directly in your GitHub Workflows:

```yaml
- name: Run HelmKeeper
  uses: marcodasilva/HelmKeeper@main
  with:
    chart-path: "./charts/my-app"
    check: "true"
```

### 3. GitLab CI / CD

Add this to your `.gitlab-ci.yml` to check your charts in your pipeline:

```yaml
helm-keeper-check:
  stage: test
  image: marcodasilva/helmkeeper:latest
  script:
    - python3 /app/main.py ./charts/my-app --check --json > helm-report.json
  artifacts:
    when: always
    paths:
      - helm-report.json
```

### 3. Running Locally (Python)

Requirements: Python 3.12+, Poetry

```bash
poetry install
poetry run python main.py ./path/to/chart
```

## Configuration

| Argument     | Description                                               |
| :----------- | :-------------------------------------------------------- |
| `chart_path` | Path to the directory containing `Chart.yaml`             |
| `--check`    | Exit with code 1 if updates/vulns found, or 2 if invalid. |
| `--json`     | Output the report in JSON format for parsing.             |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up your environment and submit Pull Requests.

## License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**.
Free for personal and non-commercial use. Commercial use requires a separate license.
See the [LICENSE](LICENSE) file for details.
