from utils.config import Config


def test_project_metadata_and_paths_are_defined():
    assert Config.PROJECT_NAME == "ResearchFlow Agent"
    assert Config.REPORTS_DIR.endswith("reports")
    assert Config.API_BASE_URL.startswith("http")
