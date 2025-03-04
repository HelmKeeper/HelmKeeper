import yaml
import requests
import argparse
from typing import Dict, List
import json
import semver
import sys
import os
from subprocess import check_output, CalledProcessError, STDOUT


def system_call(command: str):
    """
    params:
        command: list of strings, ex. `["ls", "-l"]`
    returns: output, success
    """
    try:
        output = check_output(command.split(" "), stderr=STDOUT).decode()
        success = True
    except CalledProcessError as e:
        output = e.output.decode()
        success = False
    return output, success


def parse_chart(chart_path: str) -> Dict:
    """Parse a Helm Chart.yaml file."""
    with open(chart_path, 'r') as f:
        return yaml.safe_load(f)


def validate_chart_directory(directory: str) -> bool | dict[str, dict]:
    """Validate that the input is a directory and contains Chart.yaml (mandatory) and Chart.lock (optional)."""
    result = {}
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.") # Keep print statement for user feedback
        return False

    # TODO: Considered requirement.yaml
    chart_yaml = os.path.join(directory, "Chart.yaml")
    chart_lock = os.path.join(directory, "Chart.lock")

    if not os.path.isfile(chart_yaml):
        print("Error: Chart.yaml is missing in the directory.")
        return False

    try:
        result["yaml"] = parse_chart(chart_yaml)

    except yaml.YAMLError as e:
        print(f"Error parsing Chart.yaml: {e}") # Informative message
        return False

    if os.path.isfile(chart_lock):
        try: # YAML parsing for Chart.lock
            result["lock"] = parse_chart(chart_lock)
        except yaml.YAMLError as e:
            print(f"Error parsing Chart.lock: {e}")
            return False  # Handle gracefully
    else:
        print("Warning: The Chart.lock file is missing.")

    return result


def get_dependencies(chart_path: str) -> list:
    result, success = system_call(f'helm dep list {chart_path}')
    lines = result.strip().split("\n")
    headers = lines[0].split()
    results = []

    for line in lines[1:]:
        values = line.split(maxsplit=len(headers) - 1)
        result = {headers[i].lower(): values[i] for i in range(len(headers))}
        results.append(result)

    # TODO: Validate status <> Ok.
    return results


# Constants for ArtifactHub API and CVE databases
ARTIFACTHUB_API = "https://artifacthub.io/api/v1/packages/helm/"
CVE_API = "https://osv.dev/v1/query"


def get_latest_version2(package: str, repo: str) -> str | None:
    """Fetch the latest version of a Helm chart from ArtifactHub."""
    response = requests.get(f"{ARTIFACTHUB_API}{repo}/{package}")
    if response.status_code == 200:
        return response.json().get('version', None)
    return None


def get_latest_version(name: str, repo_url: str):
    """Get latest chart version using helm and jq."""
    try:
        example1 = system_call(f"helm repo add {name} {repo_url} --repository-config temp-repo.yaml")
        example2 = system_call("helm repo list --repository-config temp-repo.yaml -o json")
        ## TODO: Search if exists previous create. Repo admin module
        example3 = system_call("helm repo update --repository-config temp-repo.yaml")
        result, status = system_call(f"helm search repo {name}/{name} -l -o json")
        charts = json.loads(result)

        if status and charts:
            valid_charts = list(filter(lambda chart: valid_semver(chart.get("version")), charts))

            if valid_charts:
                latest_chart = max(valid_charts, key=lambda x: semver.VersionInfo.parse(x["version"]))
                return latest_chart.get("version")

        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def check_vulnerabilities(package: str, version: str) -> List[str]:
    """Check for vulnerabilities for a given package and version."""
    payload = {
        "package": package,
        "version": version,
        "ecosystem": "Helm"
    }
    response = requests.post(CVE_API, json=payload)
    if response.status_code == 200:
        return [vuln['id'] for vuln in response.json().get('vulnerabilities', [])]
    return []


def update_chart(chart_path: str, dependencies: List[Dict]) -> None:
    """Update the Chart.yaml file with new dependency versions."""
    with open(chart_path, 'r') as f:
        chart = yaml.safe_load(f)

    chart['dependencies'] = dependencies

    with open(chart_path, 'w') as f:
        yaml.safe_dump(chart, f)

    print(f"Updated {chart_path} successfully!")

def valid_semver(version: str) -> bool:
    """Check if the version is a valid SemVer string."""
    try:
        # Only check for valid SemVer versions with 'x.x.x' format
        semver.VersionInfo.parse(version)
        return True
    except ValueError:
        # Return False if the version can't be parsed as a valid SemVer string
        return False

def get_current_version(chart_data, package):
    # Check both 'yaml' and 'lock' dependencies
    for section in ['lock', 'yaml']:
        for dependency in chart_data[section]['dependencies']:
            if dependency['name'] == package:
                return dependency['version']
    return None


def process_chart(chart_path: str):
    """Process a Helm Chart.yaml file for updates and vulnerabilities. """
    chart_data = validate_chart_directory(chart_path)
    if not chart_data:
        print("Error: Invalid Chart.yaml file.")
        sys.exit(1)

    dependencies = get_dependencies(chart_path)
    for dep in dependencies:
        package = dep.get('name')
        repository = dep.get('repository')
        current_version = get_current_version(chart_data, package)
        latest_version = get_latest_version(package, repository)
        print(f"package: {package}")
        print(f"current_version: {current_version}")
        print(f"latest_version: {latest_version}")

def main():
    parser = argparse.ArgumentParser(description="Helm Chart Dependency Updater")
    parser.add_argument("chart", help="Path to the Chart.yaml file")
    args = parser.parse_args()
    process_chart(args.chart)


if __name__ == "__main__":
    main()
