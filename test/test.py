import unittest
import os
import sys
import yaml
from unittest.mock import patch, MagicMock

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import validate_chart_directory, get_dependencies, check_vulnerabilities, valid_semver, process_chart

class TestHelmKeeper(unittest.TestCase):

    CHART_PATH_GITLAB = "test/resources/gitlab"
    INVALID_CHART_PATH = "test/resources/invalid"

    def setUp(self):
        os.makedirs(self.INVALID_CHART_PATH, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.INVALID_CHART_PATH):
            os.rmdir(self.INVALID_CHART_PATH)

    def test_validate_chart_directory(self):
        # Now returns a dict or None
        self.assertIsNotNone(validate_chart_directory(self.CHART_PATH_GITLAB))
        self.assertIsNone(validate_chart_directory(self.INVALID_CHART_PATH))
        self.assertIsNone(validate_chart_directory("./non-existent"))

    @patch('main.system_call')
    def test_get_dependencies(self, mock_system_call):
        # Mock helm output
        mock_output = """NAME\tVERSION\tREPOSITORY\tSTATUS
gitlab\t1.0.0\thttps://charts.gitlab.io\tok
"""
        mock_system_call.return_value = (mock_output, True)
        
        deps = get_dependencies("dummy_path")
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0]['name'], 'gitlab')
        self.assertEqual(deps[0]['version'], '1.0.0')

    def test_valid_semver(self):
        self.assertTrue(valid_semver("1.2.3"))
        self.assertFalse(valid_semver("invalid"))

    @patch('requests.post')
    def test_check_vulnerabilities(self, mock_post):
        # Mock OSV response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"vulns": [{"id": "CVE-2023-1234"}]}
        mock_post.return_value = mock_response
        
        vulns = check_vulnerabilities("test-package", "1.0.0")
        self.assertEqual(vulns, ["CVE-2023-1234"])

    @patch('main.validate_chart_directory')
    @patch('main.get_dependencies')
    @patch('main.get_latest_version')
    @patch('main.validate_compatibility')
    def test_process_chart(self, mock_compat, mock_latest, mock_deps, mock_validate):
        # Setup mocks for a full run
        mock_validate.return_value = {"yaml": {"dependencies": []}}
        mock_deps.return_value = [{"name": "foo", "version": "1.0.0", "repository": "http://repo"}]
        mock_latest.return_value = "1.1.0" # Update available
        mock_compat.return_value = True
        
        # We catch SystemExit because process_chart might exit if we passed check_only=True
        # But default process_chart doesn't exit for success, it prints.
        # Let's just run it and ensure no exception
        try:
            process_chart("dummy_path", check_only=False, json_output=True)
        except SystemExit:
            self.fail("process_chart raised SystemExit unexpectedly")

if __name__ == '__main__':
    unittest.main()
