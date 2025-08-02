# XRAY GraphQL API Mutations Documentation

This document provides comprehensive information about XRAY GraphQL mutations for creating and managing test entities.

## Table of Contents
1. [createFolder Mutation](#createfolder-mutation)
2. [createTest Mutation](#createtest-mutation)
3. [createTestSet Mutation](#createtestset-mutation)
4. [addTestsToFolder Mutation](#addteststofolder-mutation)
5. [addTestsToTestSet Mutation](#addteststotestset-mutation)
6. [Input Types](#input-types)
7. [Object Types](#object-types)

## createFolder Mutation

Creates a new folder in the test repository hierarchy.

### Arguments
- `projectId` (String, optional) - The project ID of the folder
- `testPlanId` (String, optional) - The Test Plan ID of the folder
- `path` (String, **required**) - The path of the folder (e.g., "/generic" or "/component/subcomponent")
- `testIssueIds` ([String], optional) - Array of Test IDs to add to the folder
- `issueIds` ([String], optional) - Array of Test and/or Precondition IDs to add to the folder

**Note**: Use either `testIssueIds` OR `issueIds`, but not both.

### Return Type: ActionFolderResult
```graphql
{
  folder: SimpleFolderResults {
    name: String
    path: String
    testsCount: Int
    preconditionsCount: Int
    issuesCount: Int
  }
  warnings: [String]
}
```

### Example Usage
```graphql
mutation {
  createFolder(
    projectId: "10000",
    path: "/generic",
    testIssueIds: ["10002", "12324", "12345"]
  ) {
    folder {
      name
      path
      testsCount
    }
    warnings
  }
}
```

## createTest Mutation

Creates a new test case in JIRA/XRAY.

### Arguments
- `jira` (JSON, **required**) - JIRA fields for the test issue (summary, description, etc.)
- `testType` (UpdateTestTypeInput, optional) - Test type specification
- `steps` ([CreateStepInput], optional) - Array of test steps for manual tests
- `unstructured` (String, optional) - Unstructured test definition
- `gherkin` (String, optional) - Gherkin definition for BDD tests
- `preconditionIssueIds` ([String], optional) - Array of precondition issue IDs
- `folderPath` (String, optional) - Repository folder path to place the test

### Return Type: CreateTestResult
```graphql
{
  test: Test {
    issueId: String
    projectId: String
    testType: TestType
    steps: [Step]
    unstructured: String
    gherkin: String
    folder: Folder
    dataset: Dataset
    scenarioType: String
    preconditions: PreconditionResults
    testSets: TestSetResults
    testPlans: TestPlanResults
    testExecutions: TestExecutionResults
    testRuns: TestRunResults
    history: XrayHistoryResults
    testVersions: TestVersionResults
    coverableIssues: CoverableIssueResults
    jira: JSON
    status: TestStatusType
    lastModified: String
  }
  warnings: [String]
}
```

### Example Usage
```graphql
mutation {
  createTest(
    jira: {
      fields: {
        project: { id: "10000" },
        summary: "Test login functionality",
        description: "Verify user can login with valid credentials",
        issuetype: { id: "10100" }
      }
    },
    testType: { name: "Manual" },
    steps: [
      {
        action: "Navigate to login page",
        data: "URL: https://example.com/login",
        result: "Login page is displayed"
      },
      {
        action: "Enter valid credentials",
        data: "Username: testuser, Password: ****",
        result: "Credentials are entered"
      }
    ],
    folderPath: "/Authentication"
  ) {
    test {
      issueId
      jira
    }
    warnings
  }
}
```

## createTestSet Mutation

Creates a new test set for organizing tests.

### Arguments
- `jira` (JSON, **required**) - JIRA fields for the test set issue
- `testIssueIds` ([String], optional) - Array of test IDs to include in the test set

### Return Type: CreateTestSetResult
```graphql
{
  testSet: TestSet {
    issueId: String
    projectId: String
    tests: TestResults
    history: XrayHistoryResults
    jira: JSON
    lastModified: String
  }
  warnings: [String]
}
```

### Example Usage
```graphql
mutation {
  createTestSet(
    jira: {
      fields: {
        project: { id: "10000" },
        summary: "Regression Test Set - Login Module",
        description: "Contains all regression tests for login functionality",
        issuetype: { id: "10200" }
      }
    },
    testIssueIds: ["TEST-1", "TEST-2", "TEST-3"]
  ) {
    testSet {
      issueId
      jira
    }
    warnings
  }
}
```

## addTestsToFolder Mutation

Adds existing tests to a folder.

### Arguments
- `projectId` (String, optional) - The project ID
- `testPlanId` (String, optional) - The Test Plan ID
- `path` (String, **required**) - The folder path
- `testIssueIds` ([String], **required**) - Array of test IDs to add
- `index` (Int, optional) - Position index for ordering

### Return Type: ActionFolderResult
Same as createFolder return type.

### Example Usage
```graphql
mutation {
  addTestsToFolder(
    projectId: "10000",
    path: "/Authentication",
    testIssueIds: ["TEST-10", "TEST-11", "TEST-12"]
  ) {
    folder {
      name
      path
      testsCount
    }
    warnings
  }
}
```

## addTestsToTestSet Mutation

Associates tests with an existing test set.

### Arguments
- `issueId` (String, **required**) - The test set issue ID
- `testIssueIds` ([String], **required**) - Array of test IDs to add

### Return Type: AddTestsResult
```graphql
{
  addedTests: [String]
  warning: String
}
```

### Example Usage
```graphql
mutation {
  addTestsToTestSet(
    issueId: "TESTSET-1",
    testIssueIds: ["TEST-20", "TEST-21", "TEST-22"]
  ) {
    addedTests
    warning
  }
}
```

## Input Types

### UpdateTestTypeInput
Used to specify test type when creating tests.
```graphql
{
  id: String
  name: String  # e.g., "Manual", "Automated", "Generic"
}
```

### CreateStepInput
Used to define test steps for manual tests.
```graphql
{
  action: String           # The action to perform
  data: String            # Test data for the step
  result: String          # Expected result
  attachments: [AttachmentInput]
  customFields: [CustomStepFieldInput]
  callTestIssueId: String # For calling another test
}
```

### AttachmentInput
Used to attach files to test steps.
```graphql
{
  filename: String
  mimeType: String
  data: String  # Base64 encoded file content
}
```

### CustomStepFieldInput
Used to set custom field values on test steps.
```graphql
{
  id: String    # Custom field ID
  value: JSON   # Field value
}
```

### TestTypeInput
Alternative test type specification.
```graphql
{
  id: String
  name: String
  kind: String
}
```

## Object Types

### Test Object
Represents a test case with all its properties.

**Key Fields:**
- `issueId` - The JIRA issue ID
- `projectId` - The project ID
- `testType` - The type of test (Manual, Automated, etc.)
- `steps` - Array of test steps
- `unstructured` - Unstructured test content
- `gherkin` - Gherkin/BDD content
- `folder` - The repository folder containing the test
- `preconditions` - Associated preconditions
- `testSets` - Test sets containing this test
- `jira` - All JIRA fields as JSON
- `status` - Current test status
- `lastModified` - Last modification timestamp

### Folder Object
Represents a folder in the test repository.

**Fields:**
- `name` - Folder name
- `path` - Full folder path

### TestSet Object
Represents a test set for organizing tests.

**Key Fields:**
- `issueId` - The JIRA issue ID
- `projectId` - The project ID
- `tests` - Tests contained in this set
- `jira` - All JIRA fields as JSON
- `lastModified` - Last modification timestamp

## Important Notes

1. **Project Context**: Most mutations require either `projectId` or the project must be specified in the `jira` fields.

2. **Issue Types**: The `issuetype` field in JIRA objects must use the correct ID for your JIRA instance:
   - Test issues typically use a specific test issue type ID
   - Test Set issues use a different issue type ID

3. **Folder Paths**: 
   - Always start with "/" 
   - Use forward slashes for hierarchy (e.g., "/Component/Subcomponent")
   - Folders are created automatically if they don't exist

4. **Test Types**: Common values include "Manual", "Automated", "Generic", "Cucumber"

5. **Error Handling**: Always check the `warnings` field in responses for non-critical issues.

6. **Batch Operations**: When adding multiple tests, consider the performance implications and API limits.