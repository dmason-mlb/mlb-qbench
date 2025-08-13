"""Field harmonization utilities for normalizing test data."""

from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from ..models.test_models import TestDoc, TestStep

logger = structlog.get_logger()


def normalize_functional_test(raw_data: dict[str, Any]) -> Optional[TestDoc]:
    """
    Normalize functional test data to standard format.

    Functional JSON structure (Xray format):
    {
        "testInfo": {
            "summary": "string",
            "type": "Manual",
            "priority": "string",
            "labels": ["string"]
        },
        "issueKey": "string",
        "folder": "string",
        "precondition": "string",
        "objective": "string",
        "steps": [
            {
                "index": 1,
                "action": "string",
                "data": "string",
                "result": "string"
            }
        ]
    }
    """
    try:
        # Handle nested structure - functional tests have data wrapped in 'rows'
        if 'rows' in raw_data and isinstance(raw_data['rows'], list):
            # This is the outer structure, not a single test
            logger.warning("Received outer structure instead of single test", data_keys=list(raw_data.keys()))
            return None

        # Map issueKey to jiraKey for compatibility
        if 'issueKey' in raw_data and 'jiraKey' not in raw_data:
            raw_data['jiraKey'] = raw_data['issueKey']
        if 'testCaseId' in raw_data and 'testId' not in raw_data:
            raw_data['testId'] = raw_data['testCaseId']

        # Extract test info - handle both old and Xray formats
        test_info = raw_data.get("testInfo", {})

        # For Xray format, steps are at the root level
        raw_steps = raw_data.get("steps", test_info.get("steps", []))

        # Handle testScript structure (functional tests have testScript instead of testInfo)
        if not test_info and 'testScript' in raw_data:
            # Map fields from the flattened structure
            test_info = {
                'summary': raw_data.get('summary', ''),
                'description': raw_data.get('description', ''),
                'labels': raw_data.get('labels', []),
                'priority': raw_data.get('priority', 'Medium'),
                'testType': raw_data.get('testType', 'Manual'),
                'steps': raw_data.get('testScript', {}).get('steps', []),
                'folder': raw_data.get('folder', '')
            }
            raw_steps = test_info.get('steps', [])

        # Determine UID
        uid = raw_data.get("jiraKey") or raw_data.get("issueKey") or raw_data.get("testId")
        if not uid:
            logger.warning("No jiraKey, issueKey or testId found", data=raw_data)
            return None

        # Extract and normalize steps
        steps = []
        for step in raw_steps:
            if isinstance(step, dict):
                # Handle Xray format steps
                index = step.get("index", len(steps) + 1)
                action = step.get("action", step.get("description", ""))
                data = step.get("data", "")
                if data and action:
                    action = f"{action} (Data: {data})"

                # Functional tests have 'result' field instead of 'expected'
                expected = step.get("expected", step.get("expectedResult", step.get("result", [])))
                if isinstance(expected, str):
                    expected = [expected] if expected else []
                elif not isinstance(expected, list):
                    expected = []
            else:
                # If step is just a string
                index = len(steps) + 1
                action = str(step)
                expected = []

            if action:  # Only add non-empty steps
                steps.append(TestStep(
                    index=index,
                    action=action,
                    expected=expected
                ))

        # Get description - use objective for Xray format
        description = test_info.get("description") or raw_data.get("objective", "")

        # Get preconditions - convert string to list if needed
        preconditions = raw_data.get("preconditions", raw_data.get("precondition", []))
        if isinstance(preconditions, str):
            preconditions = [preconditions] if preconditions else []

        # Create normalized test document
        test_doc = TestDoc(
            uid=uid,
            jiraKey=raw_data.get("jiraKey") or raw_data.get("issueKey"),
            testCaseId=raw_data.get("testId"),
            title=test_info.get("summary", raw_data.get("summary", "Untitled Test")),
            summary=test_info.get("summary", raw_data.get("summary")),
            description=description,
            testType=test_info.get("type", test_info.get("testType", "Manual")),
            priority=normalize_priority(test_info.get("priority", raw_data.get("priority", "Medium"))),
            platforms=raw_data.get("platforms", []),  # Use platforms from raw_data if available
            tags=test_info.get("labels", raw_data.get("labels", [])),  # labels → tags
            folderStructure=raw_data.get("folder", test_info.get("folder")),  # folder → folderStructure
            preconditions=preconditions,
            steps=steps,
            expectedResults=test_info.get("expectedResults") or raw_data.get("expectedResults"),
            testData=test_info.get("testData") or raw_data.get("testData"),
            relatedIssues=raw_data.get("relatedIssues", []),  # Check raw_data too
            testPath=raw_data.get("testPath"),  # Check raw_data too
            source="functional_tests_xray.json",
            ingested_at=datetime.now(timezone.utc)
        )

        return test_doc

    except Exception as e:
        logger.error(f"Error normalizing functional test: {e}", data=raw_data)
        return None


def normalize_api_test(raw_data: dict[str, Any]) -> Optional[TestDoc]:
    """
    Normalize API test data to standard format.

    API JSON structure (Xray format):
    {
        "title": "string",
        "priority": "string",
        "platforms": ["string"],
        "folderStructure": "string" or ["string"],
        "tags": ["string"],
        "preconditions": ["string"],
        "testSteps": [
            {
                "action": "string",
                "expectedResult": "string"  # Note: Xray uses expectedResult, not expected
            }
        ],
        "testData": "string",
        "relatedIssues": ["string"],
        "jiraKey": "string" or null,
        "testPath": "string",
        "testCaseId": "string"
    }
    """
    try:
        # Determine UID - handle null jiraKey
        jira_key = raw_data.get("jiraKey")
        test_case_id = raw_data.get("testCaseId")

        if jira_key:
            uid = jira_key
        elif test_case_id:
            uid = test_case_id
            logger.warning(f"Using testCaseId as UID due to null jiraKey: {test_case_id}")
        else:
            logger.warning("No jiraKey or testCaseId found", data=raw_data)
            return None

        # Extract and normalize steps - check both 'testSteps' and 'steps'
        raw_steps = raw_data.get("testSteps", raw_data.get("steps", []))
        steps = []
        for idx, step in enumerate(raw_steps, 1):
            if isinstance(step, dict):
                action = step.get("action", step.get("description", ""))
                # Handle Xray format which uses 'expectedResult' instead of 'expected'
                expected = step.get("expected", step.get("expectedResult", []))
                if isinstance(expected, str):
                    expected = [expected] if expected else []
                elif not isinstance(expected, list):
                    expected = []
            else:
                action = str(step)
                expected = []

            if action:
                steps.append(TestStep(
                    index=idx,
                    action=action,
                    expected=expected
                ))

        # Normalize testType - convert lowercase to uppercase
        test_type = raw_data.get("testType", "API")
        if isinstance(test_type, str) and test_type.lower() == "api":
            test_type = "API"

        # Normalize folderStructure - convert list to path string
        folder_structure = raw_data.get("folderStructure")
        if isinstance(folder_structure, list):
            folder_structure = "/".join(folder_structure)

        # Normalize preconditions - convert string to list if needed
        preconditions = raw_data.get("preconditions", [])
        if isinstance(preconditions, str):
            preconditions = [preconditions] if preconditions else []

        # Create normalized test document
        test_doc = TestDoc(
            uid=uid,
            jiraKey=jira_key,  # Can be None
            testCaseId=test_case_id,
            title=raw_data.get("title", "Untitled Test"),
            summary=raw_data.get("summary", raw_data.get("title")),  # Use summary or title as fallback
            description=raw_data.get("description"),
            testType=test_type,  # Use normalized testType
            priority=normalize_priority(raw_data.get("priority", "Medium")),
            platforms=raw_data.get("platforms", []),
            tags=raw_data.get("tags", []),
            folderStructure=folder_structure,  # Use normalized folderStructure
            preconditions=preconditions,  # Use normalized preconditions
            steps=steps,
            expectedResults=raw_data.get("expectedResults"),
            testData=raw_data.get("testData"),
            relatedIssues=raw_data.get("relatedIssues", []),
            testPath=raw_data.get("testPath"),
            source="api_tests_xray.json",
            ingested_at=datetime.now(timezone.utc)
        )

        return test_doc

    except Exception as e:
        logger.error(f"Error normalizing API test: {e}", data=raw_data)
        return None


def normalize_priority(priority: str) -> str:
    """Normalize priority values to standard set."""
    if not priority:
        return "Medium"

    priority_lower = priority.lower().strip()

    # Map variations to standard values
    priority_map = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "1": "Critical",
        "2": "High",
        "3": "Medium",
        "4": "Low",
        "p1": "Critical",
        "p2": "High",
        "p3": "Medium",
        "p4": "Low",
    }

    return priority_map.get(priority_lower, "Medium")


def merge_tags(tags1: list[str], tags2: list[str]) -> list[str]:
    """Merge and deduplicate tags from multiple sources."""
    # Use set to deduplicate, then sort for consistency
    all_tags = set(tags1 or []) | set(tags2 or [])
    return sorted(all_tags)


def ensure_folder_structure(test_doc: TestDoc, source_type: str) -> None:
    """Ensure folderStructure field is populated."""
    if not test_doc.folderStructure:
        if source_type == "functional":
            # For functional tests, we might have folder info elsewhere
            # This is a placeholder - adjust based on actual data
            test_doc.folderStructure = "Functional Tests"
        elif source_type == "api":
            # API tests should have folderStructure
            test_doc.folderStructure = "API Tests"

    # Normalize folder separators
    if test_doc.folderStructure:
        test_doc.folderStructure = test_doc.folderStructure.replace("\\", "/")


def validate_test_doc(test_doc: TestDoc) -> list[str]:
    """Validate test document and return list of warnings."""
    warnings = []

    # Check for essential fields
    if not test_doc.title or test_doc.title == "Untitled Test":
        warnings.append(f"Test {test_doc.uid} has no title")

    if not test_doc.steps:
        warnings.append(f"Test {test_doc.uid} has no steps")

    if not test_doc.tags:
        warnings.append(f"Test {test_doc.uid} has no tags")

    # Check for UID issues
    if not test_doc.jiraKey and test_doc.testCaseId:
        warnings.append(f"Test {test_doc.uid} using testCaseId as fallback (no jiraKey)")

    return warnings


def normalize_test_batch(tests: list[dict[str, Any]], source_type: str) -> tuple[list[TestDoc], list[str]]:
    """
    Normalize a batch of tests and collect warnings.

    Returns:
        Tuple of (normalized_tests, warnings)
    """
    normalized_tests = []
    all_warnings = []

    for idx, test_data in enumerate(tests):
        try:
            # Normalize based on source type
            if source_type == "functional":
                test_doc = normalize_functional_test(test_data)
            elif source_type == "api":
                test_doc = normalize_api_test(test_data)
            else:
                logger.error(f"Unknown source type: {source_type}")
                continue

            if test_doc:
                # Ensure folder structure
                ensure_folder_structure(test_doc, source_type)

                # Validate and collect warnings
                warnings = validate_test_doc(test_doc)
                all_warnings.extend(warnings)

                normalized_tests.append(test_doc)
            else:
                all_warnings.append(f"Failed to normalize test at index {idx}")

        except Exception as e:
            logger.error(f"Error processing test at index {idx}: {e}")
            all_warnings.append(f"Error processing test at index {idx}: {str(e)}")

    return normalized_tests, all_warnings


if __name__ == "__main__":
    # Test normalization

    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Test functional format
    functional_test = {
        "testId": "FUNC-001",
        "jiraKey": "FRAMED-1234",
        "testInfo": {
            "summary": "Test localization",
            "description": "Verify Spanish localization",
            "labels": ["localization", "spanish"],
            "priority": "High",
            "testType": "Manual",
            "steps": [
                {"action": "Navigate to settings", "expected": ["Settings page loads"]},
                {"action": "Change language to Spanish", "expected": ["UI updates to Spanish"]}
            ],
            "folder": "Functional/Localization"
        }
    }

    # Test API format with null jiraKey
    api_test = {
        "title": "API Localization Test",
        "priority": "High",
        "platforms": ["iOS", "Android"],
        "folderStructure": "API Tests/Localization",
        "tags": ["api", "localization"],
        "preconditions": ["API key valid"],
        "testSteps": [
            {"action": "Send GET request", "expected": ["200 status"]},
            {"action": "Verify response", "expected": ["Spanish content"]}
        ],
        "testData": "lang=es",
        "relatedIssues": ["FRAMED-999"],
        "jiraKey": None,
        "testPath": "tests/api/localization.py",
        "testCaseId": "API-001"
    }

    # Test normalization
    logger.info("Testing functional normalization")
    func_doc = normalize_functional_test(functional_test)
    if func_doc:
        logger.info("Functional test normalized", test=func_doc.model_dump())

    logger.info("Testing API normalization")
    api_doc = normalize_api_test(api_test)
    if api_doc:
        logger.info("API test normalized", test=api_doc.model_dump())
