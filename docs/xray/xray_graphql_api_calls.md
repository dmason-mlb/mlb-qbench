# XRAY GraphQL API Calls for Test Organization

Based on the Confluence documentation and XRAY GraphQL schema, here are the required GraphQL calls to create and organize test cases according to the strategy defined in the documents.

## 1. Folder Structure Creation

### Create Root Folders
Creates the main feature folders as defined in the organization strategy.

```graphql
mutation CreateRootFolder($projectId: String!, $folderPath: String!) {
    createFolder(
        projectId: $projectId,
        path: $folderPath
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

**Required Calls:**
- `/Browse Menu`
- `/Team Page`
- `/Gameday`
- `/Scoreboard`

### Create Sub-Folders
Creates the hierarchical folder structure under each root folder.

```graphql
mutation CreateSubFolder($projectId: String!, $folderPath: String!) {
    createFolder(
        projectId: $projectId,
        path: $folderPath
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

**Required Sub-Folders for Each Feature:**
- Browse Menu: `/Browse Menu/Core Navigation`, `/Browse Menu/Content Display`, `/Browse Menu/Personalization`, `/Browse Menu/Jewel Events`, `/Browse Menu/Game States`
- Team Page: `/Team Page/Date Bar`, `/Team Page/Matchup Display`, `/Team Page/Product Links`, `/Team Page/Jewel Events`
- Gameday: `/Gameday/WebView`, `/Gameday/JS Bridge`, `/Gameday/Game States`, `/Gameday/Jewel Events`
- Scoreboard: `/Scoreboard/GameCell`, `/Scoreboard/CalendarBar`, `/Scoreboard/Jewel Events`, `/Scoreboard/Game States`

### Create Jewel Events Sub-Folders
```graphql
mutation CreateJewelEventFolders($projectId: String!, $folderPath: String!) {
    createFolder(
        projectId: $projectId,
        path: $folderPath
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

**Required Jewel Event Folders (under each feature's Jewel Events folder):**
- `/Opening Day`
- `/All-Star Week`
- `/Postseason`
- `/Spring Training`
- `/International Series`

## 2. Test Case Creation

### Create Manual Test with Steps
```graphql
mutation CreateManualTest(
    $projectKey: String!,
    $summary: String!,
    $testSteps: [CreateStepInput!],
    $labels: [String!],
    $priority: String,
    $assignee: String,
    $components: [String!]
) {
    createTest(
        testType: { name: "Manual" },
        steps: $testSteps,
        jira: {
            fields: { 
                summary: $summary, 
                project: { key: $projectKey },
                labels: $labels,
                priority: { name: $priority },
                assignee: { name: $assignee },
                components: $components
            }
        }
    ) {
        test {
            issueId
            testType {
                name
            }
            steps {
                action
                data
                result
            }
            jira(fields: ["key", "labels", "priority", "assignee"])
        }
        warnings
    }
}
```

### Create Generic Test
```graphql
mutation CreateGenericTest(
    $projectKey: String!,
    $summary: String!,
    $unstructured: String!,
    $labels: [String!],
    $priority: String
) {
    createTest(
        testType: { name: "Generic" },
        unstructured: $unstructured,
        jira: {
            fields: { 
                summary: $summary, 
                project: { key: $projectKey },
                labels: $labels,
                priority: { name: $priority }
            }
        }
    ) {
        test {
            issueId
            testType {
                name
            }
            unstructured
            jira(fields: ["key", "labels"])
        }
        warnings
    }
}
```

**Label Examples Based on Strategy:**
- Feature: `@browse-menu`, `@team-page`, `@gameday`, `@scoreboard`
- Test Type: `@functional`, `@api`, `@integration`, `@e2e`
- Platform: `@ios`, `@android`, `@ipad`, `@cross-platform`
- Priority: `@critical`, `@high`, `@medium`, `@low`
- Execution: `@smoke`, `@regression`, `@nightly`, `@release`
- Component: `@navigation`, `@content-display`, `@gamecell`
- Jewel Event: `@jewel-event`, `@opening-day`, `@all-star`, `@postseason`
- Game State: `@game-state`, `@preview-state`, `@live-state`, `@final-state`

## 3. Add Tests to Folders

```graphql
mutation AddTestsToFolder(
    $projectId: String!,
    $folderPath: String!,
    $testIssueIds: [String!]!
) {
    addTestsToFolder(
        projectId: $projectId,
        path: $folderPath,
        testIssueIds: $testIssueIds
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

## 4. Create Test Sets

### Create Smoke Test Sets
```graphql
mutation CreateTestSet(
    $projectKey: String!,
    $setName: String!,
    $testIssueIds: [String!]!
) {
    createTestSet(
        testIssueIds: $testIssueIds,
        jira: {
            fields: { 
                summary: $setName, 
                project: { key: $projectKey }
            }
        }
    ) {
        testSet {
            issueId
            jira(fields: ["key"])
        }
        warnings
    }
}
```

**Required Test Sets:**
1. Smoke Test Sets:
   - `SDUI-Smoke-Tests/Browse-Menu-Smoke` (15 tests)
   - `SDUI-Smoke-Tests/Team-Page-Smoke` (12 tests)
   - `SDUI-Smoke-Tests/Gameday-Smoke` (10 tests)
   - `SDUI-Smoke-Tests/Scoreboard-Smoke` (13 tests)

2. Feature Complete Sets:
   - `Feature-Complete-Sets/Browse-Menu-Complete` (101 tests)
   - `Feature-Complete-Sets/Team-Page-Complete` (89 tests)
   - `Feature-Complete-Sets/Gameday-Complete` (117 tests)
   - `Feature-Complete-Sets/Scoreboard-Complete` (102 tests)

3. Platform-Specific Sets:
   - `Platform-Sets/iOS-Only-Tests`
   - `Platform-Sets/Android-Only-Tests`
   - `Platform-Sets/iPad-Specific-Tests`
   - `Platform-Sets/Cross-Platform-Validation`

4. Jewel Event Test Sets:
   - `Jewel-Event-Sets/Opening-Day-Suite` (15 tests)
   - `Jewel-Event-Sets/All-Star-Week-Suite` (12 tests)
   - `Jewel-Event-Sets/Postseason-Suite` (15 tests)
   - `Jewel-Event-Sets/World-Series-Suite` (8 tests)

5. Game State Test Sets:
   - `Game-State-Sets/Preview-State-Suite` (10 tests)
   - `Game-State-Sets/Live-State-Suite` (15 tests)
   - `Game-State-Sets/Final-State-Suite` (8 tests)
   - `Game-State-Sets/State-Transition-Suite` (3 tests)

## 5. Add Tests to Test Sets

```graphql
mutation AddTestsToTestSet(
    $testSetIssueId: String!,
    $testIssueIds: [String!]!
) {
    addTestsToTestSet(
        issueId: $testSetIssueId,
        testIssueIds: $testIssueIds
    ) {
        addedTests
        warning
    }
}
```

## 6. Query Operations

### Get Folder Information
```graphql
query GetFolder($projectId: String!, $folderPath: String!) {
    getFolder(projectId: $projectId, path: $folderPath) {
        name
        path
        testsCount
        tests {
            issueId
            jira(fields: ["key", "summary", "labels"])
        }
    }
}
```

### Get Test Details
```graphql
query GetTest($issueId: String!) {
    getTest(issueId: $issueId) {
        issueId
        testType {
            name
            kind
        }
        steps {
            id
            data
            action
            result
        }
        jira(fields: ["key", "summary", "labels", "priority", "assignee"])
    }
}
```

### Get Test Set Details
```graphql
query GetTestSet($issueId: String!) {
    getTestSet(issueId: $issueId) {
        issueId
        tests(limit: 100) {
            total
            results {
                issueId
                jira(fields: ["key", "summary"])
            }
        }
        jira(fields: ["key", "summary"])
    }
}
```

## Implementation Notes

1. **Project ID**: You'll need the JIRA project ID (numeric) for folder operations
2. **Project Key**: You'll need the JIRA project key (e.g., "CALC", "MLB") for issue creation
3. **Labels**: In JIRA, labels are added as an array of strings in the labels field
4. **Priority**: Priority should match existing JIRA priority names (e.g., "Critical", "High", "Medium", "Low")
5. **Components**: Components must exist in the JIRA project before being assigned
6. **Assignee**: Use the username or email of the assignee

## Execution Order

1. Create folder structure (root folders first, then sub-folders)
2. Create test cases with appropriate labels
3. Add tests to folders based on their classification
4. Create test sets
5. Add tests to test sets based on execution needs

## Error Handling

Each mutation returns a `warnings` field that should be checked for:
- Invalid project ID/key
- Duplicate folder paths
- Non-existent test IDs
- Permission issues
- Invalid field values