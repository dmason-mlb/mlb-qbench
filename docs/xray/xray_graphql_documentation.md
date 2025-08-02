# Schema Types

<details>
  <summary><strong>Table of Contents</strong></summary>

  * [Query](#query)
  * [Mutation](#mutation)
  * [Objects](#objects)
    * [ActionFolderResult](#actionfolderresult)
    * [AddDefectsResult](#adddefectsresult)
    * [AddEvidenceResult](#addevidenceresult)
    * [AddPreconditionsResult](#addpreconditionsresult)
    * [AddTestEnvironmentsResult](#addtestenvironmentsresult)
    * [AddTestExecutionsResult](#addtestexecutionsresult)
    * [AddTestPlansResult](#addtestplansresult)
    * [AddTestSetsResult](#addtestsetsresult)
    * [AddTestsResult](#addtestsresult)
    * [Attachment](#attachment)
    * [Changes](#changes)
    * [CoverableIssue](#coverableissue)
    * [CoverableIssueResults](#coverableissueresults)
    * [CoverageStatus](#coveragestatus)
    * [CreatePreconditionResult](#createpreconditionresult)
    * [CreateTestExecutionResult](#createtestexecutionresult)
    * [CreateTestPlanResult](#createtestplanresult)
    * [CreateTestResult](#createtestresult)
    * [CreateTestSetResult](#createtestsetresult)
    * [CustomStepField](#customstepfield)
    * [Dataset](#dataset)
    * [DatasetRow](#datasetrow)
    * [Evidence](#evidence)
    * [Example](#example)
    * [ExpandedStep](#expandedstep)
    * [ExpandedTest](#expandedtest)
    * [ExpandedTestResults](#expandedtestresults)
    * [Folder](#folder)
    * [FolderResults](#folderresults)
    * [IssueLinkType](#issuelinktype)
    * [Parameter](#parameter)
    * [Precondition](#precondition)
    * [PreconditionResults](#preconditionresults)
    * [ProjectSettings](#projectsettings)
    * [ProjectSettingsTestCoverage](#projectsettingstestcoverage)
    * [ProjectSettingsTestRunCustomField](#projectsettingstestruncustomfield)
    * [ProjectSettingsTestRunCustomFields](#projectsettingstestruncustomfields)
    * [ProjectSettingsTestStepField](#projectsettingsteststepfield)
    * [ProjectSettingsTestStepSettings](#projectsettingsteststepsettings)
    * [ProjectSettingsTestType](#projectsettingstesttype)
    * [RemoveDefectsResult](#removedefectsresult)
    * [RemoveEvidenceResult](#removeevidenceresult)
    * [Result](#result)
    * [ResultsEmbedding](#resultsembedding)
    * [ResultsExample](#resultsexample)
    * [ResultsStep](#resultsstep)
    * [SimpleFolderResults](#simplefolderresults)
    * [Status](#status)
    * [Step](#step)
    * [StepStatus](#stepstatus)
    * [Test](#test)
    * [TestExecution](#testexecution)
    * [TestExecutionResults](#testexecutionresults)
    * [TestPlan](#testplan)
    * [TestPlanResults](#testplanresults)
    * [TestResults](#testresults)
    * [TestRun](#testrun)
    * [TestRunCustomFieldValue](#testruncustomfieldvalue)
    * [TestRunCustomStepField](#testruncustomstepfield)
    * [TestRunIteration](#testruniteration)
    * [TestRunIterationResults](#testruniterationresults)
    * [TestRunIterationStepResult](#testruniterationstepresult)
    * [TestRunIterationStepResults](#testruniterationstepresults)
    * [TestRunParameter](#testrunparameter)
    * [TestRunPrecondition](#testrunprecondition)
    * [TestRunPreconditionResults](#testrunpreconditionresults)
    * [TestRunResults](#testrunresults)
    * [TestRunStep](#testrunstep)
    * [TestSet](#testset)
    * [TestSetResults](#testsetresults)
    * [TestStatusType](#teststatustype)
    * [TestType](#testtype)
    * [TestVersion](#testversion)
    * [TestVersionResults](#testversionresults)
    * [UpdateIterationStatusResult](#updateiterationstatusresult)
    * [UpdateTestRunExampleStatusResult](#updatetestrunexamplestatusresult)
    * [UpdateTestRunResult](#updatetestrunresult)
    * [UpdateTestRunStepResult](#updatetestrunstepresult)
    * [UpdateTestRunStepStatusResult](#updatetestrunstepstatusresult)
    * [UpdateTestStepResult](#updateteststepresult)
    * [XrayHistoryEntry](#xrayhistoryentry)
    * [XrayHistoryResults](#xrayhistoryresults)
  * [Inputs](#inputs)
    * [AttachmentDataInput](#attachmentdatainput)
    * [AttachmentInput](#attachmentinput)
    * [AttachmentOperationsInput](#attachmentoperationsinput)
    * [CreateStepInput](#createstepinput)
    * [CustomFieldInput](#customfieldinput)
    * [CustomStepFieldInput](#customstepfieldinput)
    * [FolderSearchInput](#foldersearchinput)
    * [PreconditionFolderSearchInput](#preconditionfoldersearchinput)
    * [TestRunDefectOperationsInput](#testrundefectoperationsinput)
    * [TestRunEvidenceOperationsInput](#testrunevidenceoperationsinput)
    * [TestTypeInput](#testtypeinput)
    * [TestWithVersionInput](#testwithversioninput)
    * [UpdatePreconditionInput](#updatepreconditioninput)
    * [UpdatePreconditionTypeInput](#updatepreconditiontypeinput)
    * [UpdateStepInput](#updatestepinput)
    * [UpdateTestRunStepInput](#updatetestrunstepinput)
    * [UpdateTestTypeInput](#updatetesttypeinput)
  * [Scalars](#scalars)
    * [Boolean](#boolean)
    * [Float](#float)
    * [Int](#int)
    * [JSON](#json)
    * [String](#string)

</details>

## Query
<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="query.getcoverableissue">getCoverableIssue</strong></td>
<td valign="top"><a href="#coverableissue">CoverableIssue</a></td>
<td>

Returns a Coverable Issue by issueId.
===
The query below returns a Coverable Issue.
<pre>
{
    <b>getCoverableIssue</b> {
        issueId
        jira(fields: ["assignee", "reporter"])
        status {
            name
            description
            color
        }
    }
}
</pre>
===
===
The query below returns the Coverable Issue with issue id **12345**.
<pre>
{
    <b>getCoverableIssue</b>(issueId: "12345") {
        issueId
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Coverable Issue to be returned.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getcoverableissues">getCoverableIssues</strong></td>
<td valign="top"><a href="#coverableissueresults">CoverableIssueResults</a></td>
<td>

Returns multiple coverable issues by jql or issue ids.
===
The query below returns 10 coverable issues that match the provided jql.
<pre>
{
    <b>getCoverableIssues</b>(limit: 10) {
        total
        start
        limit
        results {
            issueId
            jira(fields: ["assignee", "reporter"])
            status {
                name
                description
                color
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Coverable Issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jql</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the jql that defines the search.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getdataset">getDataset</strong></td>
<td valign="top"><a href="#dataset">Dataset</a></td>
<td>

Returns a Dataset by its testIssueId.
===
The Query below returns a Dataset.
<pre>
{
    <b>getDataset</b>(testIssueId: "12345") {
        id
        parameters {
            name
            type
            listValues
        }
        rows { 
          order 
          Values
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">callTestIssueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

(Optional) The unique identifier of the Test Call.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

(Optional) The unique identifier of the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The unique identifier of the Dataset to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanIssueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

(Optional) The unique identifier of the Test Plan.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getdatasets">getDatasets</strong></td>
<td valign="top">[<a href="#dataset">Dataset</a>]</td>
<td>

Returns multiple Datasets based on optional filters.
===
The Query below demonstrates how to retrieve multiple Datasets, including their metadata, parameters
<pre>
{
    <b>getDatasets</b>(
        testIssueIds: ["30000", "40000"],
    ) 
      {
        id
        testIssueId  
        testExecIssueId
        testPlanIssueId
        parameters {
            name
            type
            listValues
        }
        rows {
          order
          Values
        }
      }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

(Optional) Filter by Test ExecutionIds.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Filter by test issue IDs.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

(Optional) Filter by Test PlanIds.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getexpandedtest">getExpandedTest</strong></td>
<td valign="top"><a href="#expandedtest">ExpandedTest</a></td>
<td>

Returns a test (with the call test steps expanded) by issue id and version id.
===
The query below returns the test version 2 of the test with the id "12345".
<pre>
{
    <b>getExpandedTest</b>(issueId: "12345", testVersionId: "2") {
        issueId
        testType {
            name
            kind
        }
        steps {
            parentTestIssueId
            calledTestIssueId
            id
            data
            action
            result
            attachments {
                id
                filename
            }
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the test issue to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will get the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getexpandedtests">getExpandedTests</strong></td>
<td valign="top"><a href="#expandedtestresults">ExpandedTestResults</a></td>
<td>

Returns multiple tests (with the call test steps expanded) by jql, issue ids, project id or test type.
===
The query below returns the first 100 tests.
<pre>
{
    <b>getExpandedTests</b>(limit: 100) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
            jira(fields: ["assignee", "reporter"])
            warnings
        }
    }
}
</pre>
===
===
The query below returns 10 tests that match the provided jql.
<pre>
{
    <b>getExpandedTests</b>(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
            steps {
                parentTestIssueId
                calledTestIssueId
                id
                data
                action
                result
                attachments {
                    id
                    filename
                }
                customfields {
                    id
                    value
                }
            }
            jira(fields: ["assignee", "reporter"])
            warnings
        }
    }
}
</pre>
<b>Note</b>: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.
===
===
The query below returns the tests of each test version.
<pre>
{
    <b>getExpandedTests</b>(tests:[{ issueId:"12345", testVersionId: "1" }, { issueId:"54321", testVersionId: "2" }]) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">folder</td>
<td valign="top"><a href="#foldersearchinput">FolderSearchInput</a></td>
<td>

the folder information required to filter the Test issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Test issues with default Test versions to be returned. Cannot be used with <b>tests</b>.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jql</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the jql that defines the search.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">modifiedSince</td>
<td valign="top"><a href="#string">String</a></td>
<td>

all tests modified after this date will be returned

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the project of the Test issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testType</td>
<td valign="top"><a href="#testtypeinput">TestTypeInput</a></td>
<td>

the Test Type of the Test issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">tests</td>
<td valign="top">[<a href="#testwithversioninput">TestWithVersionInput</a>]</td>
<td>

the ids of the Test versions and Tests. If not given Test Version, will get the default Test version. Cannot be used with <b>issueIds</b>.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getfolder">getFolder</strong></td>
<td valign="top"><a href="#folderresults">FolderResults</a></td>
<td>

Returns the folder for the given projectId with the specified Path along with its child folders.
===
The query below returns the root folder and all its child folders.
<pre>
{
    <b>getFolder</b>(projectId: "10000", path: "/") {
        name
        path
        testsCount
        folders
    }
}
</pre>
===
===
The query below returns the folder with path "/generic" and all its child folders.
<pre>
{
    <b>getFolder</b>(projectId: "10000", path: "/generic") {
        name
        path
        testsCount
        folders
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">path</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getissuelinktypes">getIssueLinkTypes</strong></td>
<td valign="top">[<a href="#issuelinktype">IssueLinkType</a>]</td>
<td>

Returns the Issue Link Types
===
The Query below returns all Issue Link Types
<pre>
{
    <b>getIssueLinkTypes</b> {
        issueLinks {
            id
            name
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getprecondition">getPrecondition</strong></td>
<td valign="top"><a href="#precondition">Precondition</a></td>
<td>

Returns a Precondition by issue id.
===
The Query below returns a Precondition.
<pre>
{
    <b>getPrecondition</b> {
        issueId
        preconditionType {
            kind
            name
        }
    }
}
</pre>
===
===
The Query below returns the Precondition with issue id **12345**
<pre>
{
    <b>getPrecondition</b>(issueId: "12345") {
        issueId
        definition
        jira(fields: ["assignee", "reporter"])
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the issue id of the Precondition to be returned.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getpreconditions">getPreconditions</strong></td>
<td valign="top"><a href="#preconditionresults">PreconditionResults</a></td>
<td>

Returns multiple Preconditions by jql, issueIds, projectId or Precondition Type.
===
The Query below returns the first 100 Preconditions.
<pre>
{
    <b>getPreconditions</b>(limit: 100) {
        total
        start
        limit
        results {
            issueId
            preconditionType {
                name
                kind
            }
            definition
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
===
===
The Query below returns 10 Preconditions that match the provided jql
<pre>
{
    <b>getPreconditions</b>(jql: "project = 'PC'", limit: 10) {
        results {
            issueId
            preconditionType {
                name
                kind
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
<b>Note</b>: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">folder</td>
<td valign="top"><a href="#preconditionfoldersearchinput">PreconditionFolderSearchInput</a></td>
<td>

the folder information required to filter the Test issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Precondition issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jql</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the jql that defines the search.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Preconditions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">modifiedSince</td>
<td valign="top"><a href="#string">String</a></td>
<td>

all Preconditions modified after this date will be returned

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">preconditionType</td>
<td valign="top"><a href="#testtypeinput">TestTypeInput</a></td>
<td>

the Precondition Type of the Precondition issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the project of the Precondition issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getprojectsettings">getProjectSettings</strong></td>
<td valign="top"><a href="#projectsettings">ProjectSettings</a></td>
<td>

Returns the Project Settings of a Project.
===
The Query below returns multiple Status
<pre>
{
    <b>getProjectSettings</b> ( projectIdOrKey: "10000" ) {
        projectId,
        testEnvironments,
        testCoverageSettings {
            coverableIssueTypeIds
            epicIssuesRelation
            issueSubTasksRelation
            issueLinkTypeId
            issueLinkTypeDirection
        }
        defectIssueTypes
        testTypeSettings {
            testTypes {
                id
                name
                kind
            }
            defaultTestTypeId
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectIdOrKey</td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project Id

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getstatus">getStatus</strong></td>
<td valign="top"><a href="#status">Status</a></td>
<td>

Returns a Status by Test Run Status name.
===
The Query below returns a Status
<pre>
{
    <b>getStatus</b>( name: "PASSED") {
        name
        description
        final
        color
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">name</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the status name of Test Run Status

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getstatuses">getStatuses</strong></td>
<td valign="top">[<a href="#status">Status</a>]</td>
<td>

Returns all Test Run Status.
===
The Query below returns multiple Status
<pre>
{
    <b>getStatuses</b> {
        name
        description
        final
        color
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id to get statuses for. If not provided, returns global statuses

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getstepstatus">getStepStatus</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Returns a Status by Test Run Step Status name.
===
The Query below returns a Status
<pre>
{
    <b>getStepStatus</b>( name: "PASSED") {
        name
        description
        color
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">name</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the status name of test run step status

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.getstepstatuses">getStepStatuses</strong></td>
<td valign="top">[<a href="#stepstatus">StepStatus</a>]</td>
<td>

Returns all Test Run Step Status.
===
The Query below returns multiple Status
<pre>
{
    <b>getStepStatuses</b> {
        name
        description
        color
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id to get step statuses for. If not provided, returns global step statuses

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettest">getTest</strong></td>
<td valign="top"><a href="#test">Test</a></td>
<td>

Returns a Test by issueId.
===
The query below returns a Test.
<pre>
{
    <b>getTest</b> {
        issueId
        gherkin
        jira(fields: ["assignee", "reporter"])
    }
}
</pre>
===
===
The query below returns the Test with issue id **12345**.
<pre>
{
    <b>getTest</b>(issueId: "12345") {
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
            attachments {
                id
                filename
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the Test issue to be returned.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestexecution">getTestExecution</strong></td>
<td valign="top"><a href="#testexecution">TestExecution</a></td>
<td>

Returns a Test Execution by issue id.
===
The Query below returns a Test Execution.
<pre>
{
    <b>getTestExecution</b> {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}
</pre>
===
===
The Query below returns the Test Execution with issue id **12345**.
<pre>
{
    <b>getTestExecution</b>(issueId: "12345") {
        issueId
        tests(limit: 100) {
            total
            start
            limit
            results {
                issueId
                testType {
                    name
                }
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the Test Execution issue to be returned.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestexecutions">getTestExecutions</strong></td>
<td valign="top"><a href="#testexecutionresults">TestExecutionResults</a></td>
<td>

Returns multiple Test Executions by jql, issue ids or project id.
===
The Query below returns the first 100 Test Executions
<pre>
{
    <b>getTestExecutions</b>(limit: 100) {
        total
        start
        limit
        results {
            issueId
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
===
===
The Query below returns 10 Test Executions that match the provided jql.
<pre>
{
    <b>getTestExecutions</b>(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
            issueId
            tests(limit: 10) {
                total
                start
                limit
                results {
                    issueId
                    testType {
                        name
                    }
                }
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
<b>Note</b>: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Test Executions issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jql</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the jql that defines the search.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Executions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">modifiedSince</td>
<td valign="top"><a href="#string">String</a></td>
<td>

all Test Executions modified after this date will be returned

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the project of the Test Execution issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestplan">getTestPlan</strong></td>
<td valign="top"><a href="#testplan">TestPlan</a></td>
<td>

Returns a Test Plan by issue id.
===
The Query below returns a Test Plan.
<pre>
{
    <b>getTestPlan</b> {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}
</pre>
===
===
The Query below returns the Test Plan with issue id **12345**
<pre>
{
    <b>getTestPlan</b>(issueId: "12345") {
        issueId
        tests(limit: 100) {
            results {
                issueId
                testType {
                    name
                }
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the issue id of the Test Plan issue to be returned.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestplans">getTestPlans</strong></td>
<td valign="top"><a href="#testplanresults">TestPlanResults</a></td>
<td>

Returns multiple Test Plans by jql, issue ids or project id.
===
The Query below returns the first 100 Test Plans
<pre>
{
    <b>getTestPlans</b>(limit: 100) {
        total
        start
        limit
        results {
            issueId
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
===
===
The Query below returns 10 Test Plans that match the provided jql.
<pre>
{
    <b>getTestPlans</b>(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
            issueId
            tests(limit: 10) {
                total
                start
                limit
                results {
                    issueId
                    testType {
                        name
                    }
                }
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
<b>Note</b>: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Test Plan issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jql</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the jql that defines the search.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Plans to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">modifiedSince</td>
<td valign="top"><a href="#string">String</a></td>
<td>

all Test Plans modified after this date will be returned

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the project of the Test Plan issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestrun">getTestRun</strong></td>
<td valign="top"><a href="#testrun">TestRun</a></td>
<td>

Returns a Test Run by Test issue id and Test Execution issue id.
===
The Query below returns a Test Run
<pre>
{
    <b>getTestRun</b>( testIssueId: "11165", testExecIssueId: "11164") {
        id
        status {
            name
            color
            description
        }
        gherkin
        examples {
            id
            status {
                name
                color
                description
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the issue id of the Test Execution of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the issue id of the Test of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestrunbyid">getTestRunById</strong></td>
<td valign="top"><a href="#testrun">TestRun</a></td>
<td>

Returns a Test Run by id.
===
The Query below returns a Test Run.
<pre>
{
    <b>getTestRunById</b>( id: "5acc7ab0a3fe1b6fcdc3c737") {
        id
        status {
            name
            color
            description
        }
        steps {
            action
            data
            result
            attachments {
                id
                filename
            }
            status {
                name
                color
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestruns">getTestRuns</strong></td>
<td valign="top"><a href="#testrunresults">TestRunResults</a></td>
<td>

Returns multiple Test Runs testIssueIds and/or testExecIssueIds.
===
The query below returns the first 100 Test Runs that match the given testIssueIds and testExecIssueIds.
<pre>
{
    <b>getTestRuns</b>( testIssueIds: ["10001", "10002"], testExecIssueIds: ["10001", "10002"], limit: 100 ) {
        total
        limit
        start
        results {
            id
            status {
                name
                color
                description
            }
            gherkin
            examples {
                id
                status {
                name
                color
                description
                }
            }
            test {
                issueId
            }
            testExecution {
                issueId
            }
        }
    }
}
</pre>
=== ===
The query below returns the first 100 Test Runs that match the given ids.
<pre>
{
    <b>getTestRuns</b>( testIssueIds: ["12345"], limit: 100 ) {
        total
        limit
        start
        results {
            id
            status {
                name
                color
                description
            }
            steps {
                action
                data
                result
                attachments {
                    id
                    filename
                }
                status {
                    name
                    color
                }
            }
            test {
                issueId
            }
            testExecution {
                issueId
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Runs to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">modifiedSince</td>
<td valign="top"><a href="#string">String</a></td>
<td>

all TestRuns modified after this date will be returned

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Execution of the Test Runs.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test of the Test Runs.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunAssignees</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the user account ids of the assignee of the Test Runs.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestrunsbyid">getTestRunsById</strong></td>
<td valign="top"><a href="#testrunresults">TestRunResults</a></td>
<td>

Returns multiple Test Runs by id.
===
The query below returns the first 100 Test Runs that match the given ids.
<pre>
{
    <b>getTestRunsById</b>( ids: ["5acc7ab0a3fe1b6fcdc3c737"], limit: 10 ) {
        total
        limit
        start
        results {
            id
            status {
                name
                color
                description
            }
            gherkin
            examples {
                id
                status {
                    name
                    color
                    description
                }
            }
            test {
                issueId
            }
            testExecution {
                issueId
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">ids</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Test Runs.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Runs to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestset">getTestSet</strong></td>
<td valign="top"><a href="#testset">TestSet</a></td>
<td>

Returns a Test Set by issueId
===
The query below returns a test set
<pre>
{
    <b>getTestSet</b> {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}
</pre>
===
===
The query below returns the test set with issue id **12345**
<pre>
{
    <b>getTestSet</b>(issueId: "12345") {
        issueId
        tests(limit: 100) {
            results {
                issueId
                testType {
                    name
                }
            }
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the Test Set issue to be returned.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettestsets">getTestSets</strong></td>
<td valign="top"><a href="#testsetresults">TestSetResults</a></td>
<td>

Returns multiple Test Sets by jql, issueIds or projectId.
===
The query below returns the first 100 Test Sets.
<pre>
{
    <b>getTestSets</b>(limit: 100) {
        total
        start
        limit
        results {
            issueId
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
===
===
The query below returns 10 Test Sets that match the provided jql.
<pre>
{
    <b>getTestSets</b>(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
            issueId
            tests(limit: 10) {
                results {
                    issueId
                    testType {
                        name
                    }
                }
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
<b>Note</b>: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Test Set issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jql</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the jql that defines the search.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Sets to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">modifiedSince</td>
<td valign="top"><a href="#string">String</a></td>
<td>

all test sets modified after this date will be returned

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the project of the Test Set issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="query.gettests">getTests</strong></td>
<td valign="top"><a href="#testresults">TestResults</a></td>
<td>

Returns multiple tests by jql, issue ids, project id or test type.
===
The query below returns the first 100 tests.
<pre>
{
    <b>getTests</b>(limit: 100) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
===
===
The query below returns 10 tests that match the provided jql.
<pre>
{
    <b>getTests</b>(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
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
                attachments {
                    id
                    filename
                }
                customfields {
                    id
                    value
                }
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}
</pre>
<b>Note</b>: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">folder</td>
<td valign="top"><a href="#foldersearchinput">FolderSearchInput</a></td>
<td>

the folder information required to filter the Test issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Test issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jql</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the jql that defines the search.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">modifiedSince</td>
<td valign="top"><a href="#string">String</a></td>
<td>

all tests modified after this date will be returned

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the id of the project of the Test issues to be returned.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testType</td>
<td valign="top"><a href="#testtypeinput">TestTypeInput</a></td>
<td>

the Test Type of the Test issues to be returned.

</td>
</tr>
</tbody>
</table>

## Mutation
<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="mutation.adddefectstotestrun">addDefectsToTestRun</strong></td>
<td valign="top"><a href="#adddefectsresult">AddDefectsResult</a></td>
<td>

Mutation used to add defects to a Test Run.
===
The mutation below adds 2 defects to the Test Run.
<pre>
mutation {
    <b>addDefectsToTestRun</b>( id: "5acc7ab0a3fe1b6fcdc3c737", issues: ["XRAY-1234", "12345"]) {
        addedDefects
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issues</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the ids or keys of the defects to add to the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.adddefectstotestrunstep">addDefectsToTestRunStep</strong></td>
<td valign="top"><a href="#adddefectsresult">AddDefectsResult</a></td>
<td>

Mutation used to add defects to a Test Run Step.
===
The mutation below adds 2 defects to the Test Run Step.
<pre>
mutation {
    <b>addDefectsToTestRunStep</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        issues: ["XRAY-1234", "12345"]
    ) {
        addedDefects
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issues</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids or keys of the defects.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addevidencetotestrun">addEvidenceToTestRun</strong></td>
<td valign="top"><a href="#addevidenceresult">AddEvidenceResult</a></td>
<td>

Mutation used to add evidence to a Test Run.
===
The mutation below adds an evidence to the Test Run.
<pre>
mutation {
    <b>addEvidenceToTestRun</b>(
        id: "5acc7ab0a3fe1b6fcdc3c737",
        evidence: [
            {
                filename: "evidence.txt"
                mimeType: "text/plain"
                data: "SGVsbG8gV29ybGQ="
            }
        ]
    ) {
        addedEvidence
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">evidence</td>
<td valign="top">[<a href="#attachmentdatainput">AttachmentDataInput</a>]!</td>
<td>

the evidence to add to the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addevidencetotestrunstep">addEvidenceToTestRunStep</strong></td>
<td valign="top"><a href="#addevidenceresult">AddEvidenceResult</a></td>
<td>

Mutation used to add evidence to a Test Run Step.
===
The mutation below adds an evidence to the Test Run Step.
<pre>
mutation {
    <b>addEvidenceToTestRunStep</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        evidence: [
            {
                filename: "evidence.txt"
                mimeType: "text/plain"
                data: "SGVsbG8gV29ybGQ="
            }
        ]
    ) {
        addedEvidence
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">evidence</td>
<td valign="top">[<a href="#attachmentdatainput">AttachmentDataInput</a>]</td>
<td>

the evidence to add to the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addissuestofolder">addIssuesToFolder</strong></td>
<td valign="top"><a href="#actionfolderresult">ActionFolderResult</a></td>
<td>

Mutation used to add issues to a Folder.
===
The mutation below will add issues to a Folder.
<pre>
mutation {
    <b>addIssuesToFolder</b>(
        projectId: "10000",
        path: "/generic",
        issueIds: ["10002","12324","12345"]
    ) {
        folder {
            name
            path
            issuesCount
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">index</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of where to insert the Tests in.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the Test or Precondition ids to add to the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">path</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addpreconditionstotest">addPreconditionsToTest</strong></td>
<td valign="top"><a href="#addpreconditionsresult">AddPreconditionsResult</a></td>
<td>

Mutation used to associate Preconditions to the Test.
<b>Note</b>: The preconditions to be associated with the Test must be of the same Test Type of the Test.
===
The mutation below will associate the precondition with issue id "54321" to the test "12345".
<pre>
mutation {
    <b>addPreconditionsToTest</b>(
        issueId: "12345",
        preconditionIssueIds: ["54321"]
    ) {
        addedPreconditions
        warning
    }
}
</pre>
===
===
The mutation below will associate the precondition with issue id "54321" to the version 3 of the Test "12345".
<pre>
mutation {
    <b>addPreconditionsToTest</b>(
        issueId: "12345",
        versionId: 3,
        preconditionIssueIds: ["54321"]
    ) {
        addedPreconditions
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">preconditionIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Preconditions.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addtestenvironmentstotestexecution">addTestEnvironmentsToTestExecution</strong></td>
<td valign="top"><a href="#addtestenvironmentsresult">AddTestEnvironmentsResult</a></td>
<td>

Mutation used to add Test Environments to the Test Execution.
===
The mutation below will add the test Environments "android" and "ios" to the Test execution "12345".
<pre>
mutation {
    <b>addTestEnvironmentsToTestExecution</b>(
        issueId: "12345",
        testEnvironments: ["android", "ios"]
    ) {
        associatedTestEnvironments
        createdTestEnvironments
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testEnvironments</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the test environments to add.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addtestexecutionstotest">addTestExecutionsToTest</strong></td>
<td valign="top"><a href="#addtestexecutionsresult">AddTestExecutionsResult</a></td>
<td>

Mutation used to associate Test Executions to the Test.
===
The mutation below will associate the Test Execution with issue id "54321" to the Test "12345".
<pre>
mutation {
    <b>addTestExecutionsToTest</b>(
        issueId: "12345",
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}
</pre>
===
===
The mutation below will associate the Test Execution with issue id "54321" to version 3 of the Test "12345".
<pre>
mutation {
    <b>addTestExecutionsToTest</b>(
        issueId: "12345",
        versionId: 3,
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Executions.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addtestexecutionstotestplan">addTestExecutionsToTestPlan</strong></td>
<td valign="top"><a href="#addtestexecutionsresult">AddTestExecutionsResult</a></td>
<td>

Mutation used to associate Test Executions to the Test Plan.
===
The mutation below will associate the Test Execution with issue id "54321" to the test Plan "12345".
<pre>
mutation {
    <b>addTestExecutionsToTestPlan</b>(
        issueId: "12345",
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Plan.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Executions.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addtestplanstotest">addTestPlansToTest</strong></td>
<td valign="top"><a href="#addtestplansresult">AddTestPlansResult</a></td>
<td>

Mutation used to associate Test Plans to the Test.
===
The mutation below will associate the Test Plan with issue id "54321" to the test "12345".
<pre>
mutation {
    <b>addTestPlansToTest</b>(
        issueId: "12345",
        testPlanIssueIds: ["54321"]
    ) {
        addedTestPlans
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Plans.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addtestsetstotest">addTestSetsToTest</strong></td>
<td valign="top"><a href="#addtestsetsresult">AddTestSetsResult</a></td>
<td>

Mutation used to associate Test Sets to the Test.
===
The mutation below will associate the test set with issue id "54321" to the test "12345".
<pre>
mutation {
    <b>addTestSetsToTest</b>(
        issueId: "12345",
        testSetIssueIds: ["54321"]
    ) {
        addedTestSets
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testSetIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Sets.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addteststep">addTestStep</strong></td>
<td valign="top"><a href="#step">Step</a></td>
<td>

Mutation used to add a Step to a Test.
===
The mutation below will add a new Step to the test with id "12345".
<pre>
mutation {
    <b>addTestStep</b>(
        issueId: "12345",
        step: {
            action: "Use Xray Cloud Rest Api to add a new Step to the Test",
            result: "Step was added to the Test",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Tokyo"}]
        }
    ) {
        id
        action
        data
        result
    }
}
</pre>
===
===
The mutation below will add a new Step to the version 3 of the Test with id "12345".
<pre>
mutation {
    <b>addTestStep</b>(
        issueId: "12345",
        versionId: 3,
        step: {
            action: "Use Xray Cloud Rest Api to add a new Step to the Test",
            result: "Step was added to the Test",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Tokyo"}]
        }
    ) {
        id
        action
        data
        result
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">step</td>
<td valign="top"><a href="#createstepinput">CreateStepInput</a>!</td>
<td>

the Step to add to the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addteststofolder">addTestsToFolder</strong></td>
<td valign="top"><a href="#actionfolderresult">ActionFolderResult</a></td>
<td>

Mutation used to add tests to a Folder.
===
The mutation below will add tests to a Folder.
<pre>
mutation {
    <b>addTestsToFolder</b>(
        projectId: "10000",
        path: "/generic",
        testIssueIds: ["10002","12324","12345"]
    ) {
        folder {
            name
            path
            testsCount
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">index</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of where to insert the Tests in.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">path</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the Test ids to add to the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addteststoprecondition">addTestsToPrecondition</strong></td>
<td valign="top"><a href="#addtestsresult">AddTestsResult</a></td>
<td>

Mutation used to associate Tests to the Precondition. One of <b>testIssueIds</b> or <b>tests</b> is required.
<b>Note</b>: The Tests to be associated with the Precondition must be of the same Test Type of the Precondition.
===
The mutation below will associate the Test with issue id "54321" to the Precondition "12345"
<pre>
mutation {
    <b>addTestsToPrecondition</b>(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}
</pre>
===
===
The mutation below will associate the version 2 of Test "54321" and the version 3 of Test "67890" to the Precondition "12345"
<pre>
mutation {
    <b>addTestsToPrecondition</b>(
        issueId: "12345",
        tests: [{ issueId: "54321", versionId: 2 }, { issueId: "67890", versionId: 3 }]
    ) {
        addedTests
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Precondition.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Tests. Will associate the default Test versions. Cannot be used with <b>tests</b>.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">tests</td>
<td valign="top">[<a href="#testwithversioninput">TestWithVersionInput</a>]</td>
<td>

the ids of the Test versions.  Cannot be used with <b>testIssueIds</b>.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addteststotestexecution">addTestsToTestExecution</strong></td>
<td valign="top"><a href="#addtestsresult">AddTestsResult</a></td>
<td>

Mutation used to associate Tests to the Test Execution. One of <b>testIssueIds</b> or <b>tests</b> is required.
===
The mutation below will associate the test with issue id "54321" to the Test execution "12345".
<pre>
mutation {
    <b>addTestsToTestExecution</b>(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Tests. Will associate the default Test versions. Cannot be used with <b>tests</b>.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">tests</td>
<td valign="top">[<a href="#testwithversioninput">TestWithVersionInput</a>]</td>
<td>

the ids of the Test versions. Cannot be used with <b>testIssueIds</b>.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addteststotestplan">addTestsToTestPlan</strong></td>
<td valign="top"><a href="#addtestsresult">AddTestsResult</a></td>
<td>

Mutation used to associate Tests to the Test Plan.
===
The mutation below will associate the test with issue id "54321" to the Test Plan "12345".
<pre>
mutation {
    <b>addTestsToTestPlan</b>(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Plan.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.addteststotestset">addTestsToTestSet</strong></td>
<td valign="top"><a href="#addtestsresult">AddTestsResult</a></td>
<td>

Mutation used to associate Tests to the Test Set.
===
The mutation below will associate the test with issue id "54321" to the Test Set "12345".
<pre>
mutation {
    <b>addTestsToTestSet</b>(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Set.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.createfolder">createFolder</strong></td>
<td valign="top"><a href="#actionfolderresult">ActionFolderResult</a></td>
<td>

Mutation used to create a new Folder.
===
The mutation below will create a new Folder.
<pre>
mutation {
    <b>createFolder</b>(
        projectId: "10000",
        path: "/generic"
    ) {
        folder {
            name
            path
            testsCount
        }
        warnings
    }
}
</pre>
===
===
The mutation below will create a new Folder and add tests to it.
<pre>
mutation {
    <b>createFolder</b>(
        projectId: "10000",
        path: "/generic",
        testIssueIds: ["10002","12324","12345"]
    ) {
        folder {
            name
            path
            testsCount
        }
        warnings
    }
}
</pre>
===
===
The mutation below will create a new Folder and add tests and/or preconditions to it.
<pre>
mutation {
    <b>createFolder</b>(
        projectId: "10000",
        path: "/generic",
        issueIds: ["10002","12324","12345"]
    ) {
        folder {
            name
            path
            testsCount
            issuesCount
            preconditionsCount
        }
        warnings
    }
}
</pre>
<b>Note</b>: Use createFolder with <b>testIssueIds</b> (in which all ids must be from Tests)
OR with <b>issueIds</b> (which can be eiter Test ids and/or Precondition ids), but not with both.
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the Test or Precondition ids to add to the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">path</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the Test ids to add to the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.createprecondition">createPrecondition</strong></td>
<td valign="top"><a href="#createpreconditionresult">CreatePreconditionResult</a></td>
<td>

Mutation used to create a new Precondition.
===
The mutation below will create a new Precondition.
<pre>
mutation {
    <b>createPrecondition</b>(
        preconditionType: { name: "Generic" }
        definition: "Turn on calculator."
        jira: {
            fields: { summary:"Turn on calculator", project: {key: "CALC"} }
        }
    ) {
        precondition {
            issueId
            preconditionType {
                name
            }
            definition
            jira(fields: ["key"])
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">definition</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the definition of the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">folderPath</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test repository folder for the Precondition.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jira</td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

the jira object that will be used to create the Precondition.
Check [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-post) Jira endpoint for more information related with this field.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">preconditionType</td>
<td valign="top"><a href="#updatepreconditiontypeinput">UpdatePreconditionTypeInput</a></td>
<td>

the Precondition Type of the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the Test issue ids to be associated with the Precondition issue. Will associate the default Test versions. Cannot be used with <b>tests</b>.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">tests</td>
<td valign="top">[<a href="#testwithversioninput">TestWithVersionInput</a>]</td>
<td>

the Test versions to be associated with the Precondition. Cannot be used with <b>testIssueIds</b>.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.createtest">createTest</strong></td>
<td valign="top"><a href="#createtestresult">CreateTestResult</a></td>
<td>

Mutation used to create a new Test.
===
The mutation below will create a new Test.
<pre>
mutation {
    <b>createTest</b>(
        testType: { name: "Generic" },
        unstructured: "Perform exploratory tests on calculator.",
        jira: {
            fields: { summary:"Exploratory Test", project: {key: "CALC"} }
        }
    ) {
        test {
            issueId
            testType {
                name
            }
            unstructured
            jira(fields: ["key"])
        }
        warnings
    }
}
</pre>
=== ===
The mutation below will create a new Test.
<pre>
mutation {
    <b>createTest</b>(
        testType: { name: "Manual" },
        steps: [
            {
                action: "Create first example step",
                result: "First step was created"
            },
            {
                action: "Create second example step with data",
                data: "Data for the step",
                result: "Second step was created with data"
            }
        ],
        jira: {
            fields: { summary:"Exploratory Test", project: {key: "CALC"} }
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
            jira(fields: ["key"])
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">folderPath</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test repository folder for the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">gherkin</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the gherkin definition of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jira</td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

the Jira object that will be used to create the Test.
Check [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-post) Jira endpoint for more information related with this field.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">preconditionIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the Precondition ids that be associated with the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">steps</td>
<td valign="top">[<a href="#createstepinput">CreateStepInput</a>]</td>
<td>

the Step definition of the test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testType</td>
<td valign="top"><a href="#updatetesttypeinput">UpdateTestTypeInput</a></td>
<td>

the Test Type of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">unstructured</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the unstructured definition of the Test.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.createtestexecution">createTestExecution</strong></td>
<td valign="top"><a href="#createtestexecutionresult">CreateTestExecutionResult</a></td>
<td>

Mutation used to create a new Test Execution.
===
The mutation below will create a new Test Execution.
<pre>
mutation {
    <b>createTestExecution</b>(
        testIssueIds: ["54321"]
        testEnvironments: ["android"]
        jira: {
            fields: { summary: "Test Execution for CALC-123", project: {key: "CALC"} }
        }
    ) {
        testExecution {
            issueId
            jira(fields: ["key"])
        }
        warnings
        createdTestEnvironments
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jira</td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

the Jira object that will be used to create the Test Execution.
Check [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-post) Jira endpoint for more information related with this field.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testEnvironments</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the test environments to be added to the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the test issue ids that will be associated with the Test Execution. Cannot be used with <b>tests</b>.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">tests</td>
<td valign="top">[<a href="#testwithversioninput">TestWithVersionInput</a>]</td>
<td>

the Test versions to be associated with the Test Execution. Cannot be used with <b>testIssueIds</b>.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.createtestplan">createTestPlan</strong></td>
<td valign="top"><a href="#createtestplanresult">CreateTestPlanResult</a></td>
<td>

Mutation used to create a new Test Plan.
===
The mutation below will create a new Test Plan.
<pre>
mutation {
    <b>createTestPlan</b>(
        testIssueIds: ["54321"]
        jira: {
            fields: { summary: "Test Plan for v1.0", project: {key: "CALC"} }
        }
    ) {
        testPlan {
            issueId
            jira(fields: ["key"])
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jira</td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

the Jira object that will be used to create the Test Plan.
Check [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-post) Jira endpoint for more information related with this field.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">savedFilter</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the saved filter id or name that will be used to configure the Test Plan. Cannot be used with <b>testIssueIds</b>.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the test issue ids that will be associated with the Test Plan. Cannot be used with <b>savedFilter</b>.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.createtestset">createTestSet</strong></td>
<td valign="top"><a href="#createtestsetresult">CreateTestSetResult</a></td>
<td>

Mutation used to create a new Test Set.
===
The mutation below will create a new Test Set.
<pre>
mutation {
    <b>createTestSet</b>(
        testIssueIds: ["54321"]
        jira: {
            fields: { summary: "Test Set for Generic Tests", project: {key: "CALC"} }
        }
    ) {
        testSet {
            issueId
            jira(fields: ["key"])
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">jira</td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

the Jira object that will be used to create the Test Set.
Check [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-post) Jira endpoint for more information related with this field.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the Test ids that will be associated with the Test Set.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.deletefolder">deleteFolder</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to delete a Folder.
===
The mutation below will delete a Folder.
<pre>
mutation {
    <b>deleteFolder</b>(
        projectId: "10000",
        path: "/generic"
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">path</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.deleteprecondition">deletePrecondition</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to delete a Precondition
===
The mutation below will delete the Precondition with issue id "12345"
<pre>
mutation {
    <b>deletePrecondition</b>(issueId: "12345")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Precondition.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.deletetest">deleteTest</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to delete a Test.
===
The mutation below will delete the Test with issue id "12345".
<pre>
mutation {
    <b>deleteTest</b>(issueId: "12345")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.deletetestexecution">deleteTestExecution</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to delete a Test Execution.
===
The mutation below will delete the Test Execution with id "12345".
<pre>
mutation {
    <b>deleteTestExecution</b>(issueId: "12345")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.deletetestplan">deleteTestPlan</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to delete a Test Plan.
===
The mutation below will delete the Test Plan with id "12345".
<pre>
mutation {
    <b>deleteTestPlan</b>(issueId: "12345")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

issue id of the Test Plan.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.deletetestset">deleteTestSet</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to delete a Test Set
===
The mutation below will delete the Test Set with issue id "12345".
<pre>
mutation {
    <b>deleteTestSet</b>(issueId: "12345")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The issue id of the Test Set.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.movefolder">moveFolder</strong></td>
<td valign="top"><a href="#actionfolderresult">ActionFolderResult</a></td>
<td>

Mutation used to move a Folder.
===
The mutation below will move a Folder.
<pre>
mutation {
    <b>moveFolder</b>(
        projectId: "10000",
        path: "/generic",
        destinationPath: "/testType"
    ) {
        folder {
            name
            path
            testsCount
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">destinationPath</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the new path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">index</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of where to insert the folder in.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">path</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removeallteststeps">removeAllTestSteps</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove all Steps from a Test.
===
The mutation below removes all the Steps from test with id "12345".
<pre>
mutation {
    <b>removeAllTestSteps</b>(
        issueId: "12345",
    )
}
</pre>
===
===
The mutation below removes all the Steps from the version 3 of the Test with id "12345".
<pre>
mutation {
    <b>removeAllTestSteps</b>(
        issueId: "12345",
        versionId: 3
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removedefectsfromtestrun">removeDefectsFromTestRun</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove defects from a Test Run.
===
The mutation below removes 2 defects from the Test Run.
<pre>
mutation {
    <b>removeDefectsFromTestRun</b>( id: "5acc7ab0a3fe1b6fcdc3c737", issues: ["XRAY-1234", "12345"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issues</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the ids or keys of the defects to remove from the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removedefectsfromtestrunstep">removeDefectsFromTestRunStep</strong></td>
<td valign="top"><a href="#removedefectsresult">RemoveDefectsResult</a></td>
<td>

Mutation used to remove defects from a Test Run.
===
The mutation below removes 2 defects from the Test Run.
<pre>
mutation {
    <b>removeDefectsFromTestRunStep</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        issues: ["XRAY-1234", "12345"]
    ) {
        removedDefects
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issues</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the ids or keys of the defects.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removeevidencefromtestrun">removeEvidenceFromTestRun</strong></td>
<td valign="top"><a href="#removeevidenceresult">RemoveEvidenceResult</a></td>
<td>

Mutation used to remove evidence from a Test Run.
===
The mutation below removes an evidence from the Test Run.
<pre>
mutation {
    <b>removeEvidenceFromTestRun</b>(
        id: "5acc7ab0a3fe1b6fcdc3c737",
        evidenceFilenames: ["evidence.txt"]
    ) {
        removedEvidence
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">evidenceFilenames</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the filenames of the evidence to remove from the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">evidenceIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the evidence to remove from the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removeevidencefromtestrunstep">removeEvidenceFromTestRunStep</strong></td>
<td valign="top"><a href="#removeevidenceresult">RemoveEvidenceResult</a></td>
<td>

Mutation used to remove evidence from a Test Run Step.
===
The mutation below removes an evidence from the Test Run Step.
<pre>
mutation {
    <b>removeEvidenceFromTestRunStep</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        evidenceFilenames: ["evidence.txt"]
    ) {
        removedEvidence
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">evidenceFilenames</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the filename of the evidence.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">evidenceIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the id of the evidence.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removeissuesfromfolder">removeIssuesFromFolder</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove issues from Folder.
===
The mutation below will remove issues from a Folder.
<pre>
mutation {
    <b>removeIssuesFromFolder</b>(
        projectId: "10000",
        issueIds: ["10002","12324","12345"]
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the Test or Precondition ids to remove from the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removepreconditionsfromtest">removePreconditionsFromTest</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Preconditions from the Test.
===
The mutation below will remove the preconditions with issue id "54321" and "67890" from the test "12345".
<pre>
mutation {
    <b>removePreconditionsFromTest</b>(issueId: "12345", preconditionIssueIds: ["54321", "67890"])
}
</pre>
===
===
The mutation below will remove the preconditions with issue id "54321" and "67890" from the version 3 of the Test "12345".
<pre>
mutation {
    <b>removePreconditionsFromTest</b>(issueId: "12345", versionId: 3, preconditionIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">preconditionIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Preconditions.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestenvironmentsfromtestexecution">removeTestEnvironmentsFromTestExecution</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Test Environments from the Test Execution.
===
The mutation below will remoive the Test Environments "android" and "ios" from the Test execution "12345".
<pre>
mutation {
    <b>removeTestEnvironmentsFromTestExecution</b>(
        issueId: "12345",
        testEnvironments: ["android", "ios"]
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testEnvironments</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the test environments to remove

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestexecutionsfromtest">removeTestExecutionsFromTest</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Test Executions from the Test.
===
The mutation below will remove the Test Executions with issue id "54321" and "67890" from the Test "12345".
<pre>
mutation {
    <b>removeTestExecutionsFromTest</b>(issueId: "12345", testExecIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Executions.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestexecutionsfromtestplan">removeTestExecutionsFromTestPlan</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Test Executions from the Test Plan.
===
The mutation below will remove the Test executions with issue id "54321" and "67890" from the Test Plan "12345".
<pre>
mutation {
    <b>removeTestExecutionsFromTestPlan</b>(issueId: "12345", testExecIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Plan.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testExecIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Executions.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestplansfromtest">removeTestPlansFromTest</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Test Plans from the Test.
===
The mutation below will remove the Test Plans with issue id "54321" and "67890" from the Test "12345".
<pre>
mutation {
    <b>removeTestPlansFromTest</b>(issueId: "12345", testPlanIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Plans.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestsetsfromtest">removeTestSetsFromTest</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Test Sets from the Test.
===
The mutation below will remove the Test Sets with issue id "54321" and "67890" from the test "12345".
<pre>
mutation {
    <b>removeTestSetsFromTest</b>(issueId: "12345", testSetIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testSetIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Test Sets.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removeteststep">removeTestStep</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove a Step from a Test.
===
The mutation below removes the Step with id "836d30ec-f034-4a03-879e-9c44a1d6d1fe".
<pre>
mutation {
    <b>removeTestStep</b>(
        stepId: "836d30ec-f034-4a03-879e-9c44a1d6d1fe",
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestsfromfolder">removeTestsFromFolder</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove tests from Folder.
===
The mutation below will remove tests from a Folder.
<pre>
mutation {
    <b>removeTestsFromFolder</b>(
        projectId: "10000",
        testIssueIds: ["10002","12324","12345"]
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the Test ids to remove from the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestsfromprecondition">removeTestsFromPrecondition</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Tests from the Precondition. One of <b>testIssueIds</b> or <b>tests</b> is required.
===
The mutation below will remove the Tests with issue id "54321" and "67890" from the Precondition "12345".
<pre>
mutation {
    <b>removeTestsFromPrecondition</b>(issueId: "12345", testIssueIds: ["54321", "67890"])
}
</pre>
===
===
The mutation below will remove the version 2 of Test "54321" and the version 3 of Test "67890" from the Precondition "12345".
<pre>
mutation {
    <b>removeTestsFromPrecondition</b>(
        issueId: "12345",
        tests: [{ issueId: "54321", versionId: 2 }, { issueId: "67890", versionId: 3 }]
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Precondition.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Tests. Will remove the default Test versions. Cannot be used with <b>tests</b>.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">tests</td>
<td valign="top">[<a href="#testwithversioninput">TestWithVersionInput</a>]</td>
<td>

the ids of the Test versions. Cannot be used with <b>testIssueIds</b>.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestsfromtestexecution">removeTestsFromTestExecution</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Tests from the Test Execution.
===
The mutation below will remove the Tests with issue id "54321" and "67890" from the Test Execution "12345".
<pre>
mutation {
    <b>removeTestsFromTestExecution</b>(issueId: "12345", testIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

issue id of the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestsfromtestplan">removeTestsFromTestPlan</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Tests from the Test Plan.
===
The mutation below will remove the Tests with id "54321" and "67890" from the Test Plan "12345".
<pre>
mutation {
    <b>removeTestsFromTestPlan</b>(issueId: "12345", testIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Plan.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.removetestsfromtestset">removeTestsFromTestSet</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to remove Tests from the Test Set.
===
The mutation below will remove the Tests with issue id "54321" and "67890" from the test set "12345".
<pre>
mutation {
    <b>removeTestsFromTestSet</b>(issueId: "12345", testIssueIds: ["54321", "67890"])
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test Set.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testIssueIds</td>
<td valign="top">[<a href="#string">String</a>]!</td>
<td>

the issue ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.renamefolder">renameFolder</strong></td>
<td valign="top"><a href="#actionfolderresult">ActionFolderResult</a></td>
<td>

Mutation used to rename a Folder.
===
The mutation below will rename a Folder.
<pre>
mutation {
    <b>renameFolder</b>(
        projectId: "10000",
        path: "/generic",
        newName: "Junit"
    ) {
        folder {
            name
            path
            testsCount
        }
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">newName</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the new name of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">path</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">projectId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the project id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlanId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.resettestrun">resetTestRun</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to reset the Test Run. This will load the new test definition and delete the current execution data.
===
The mutation below resets the Test Run.
<pre>
mutation {
    <b>resetTestRun</b>( id: "5acc7ab0a3fe1b6fcdc3c737")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.settestruntimer">setTestRunTimer</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to set the timer in Test Run. This will start, pause or stop the timer in Test Run.
===
The mutation below start the timer in Test Run.
<pre>
mutation {
    <b>setTestRunTimer</b>( 
        testRunId: "5acc7ab0a3fe1b6fcdc3c737"
        running: true
    ) {
        warnings
    }
}
</pre>

The mutation below stop the timer in Test Run.
<pre>
mutation {
    <b>setTestRunTimer</b>( 
        testRunId: "5acc7ab0a3fe1b6fcdc3c737"
        reset: true
    ) {
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">reset</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

to stop the timer

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">running</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

to start (true) or pause (false) the timer

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updategherkintestdefinition">updateGherkinTestDefinition</strong></td>
<td valign="top"><a href="#test">Test</a></td>
<td>

Mutation used to update the Gherkin definition of a Test.
===
The mutation below will update the gherkin definition of the Test with id "12345".
<pre>
mutation {
    <b>updateGherkinTestDefinition</b>(issueId: "12345", gherkin: "Gherkin definition" ) {
        issueId
        gherkin
    }
}
</pre>
===
===
The mutation below will update the gherkin definition of the version 3 of the Test with id "12345".
<pre>
mutation {
    <b>updateGherkinTestDefinition</b>(issueId: "12345", versionId: 3, gherkin: "Gherkin definition" ) {
        issueId
        gherkin
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">gherkin</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the gherkin definition of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updateiterationstatus">updateIterationStatus</strong></td>
<td valign="top"><a href="#updateiterationstatusresult">UpdateIterationStatusResult</a></td>
<td>

Mutation used to update the status of a Test Run iteration.
===
The mutation below updates the status of a Test Run iteration.
<pre>
mutation {
    <b>updateIterationStatus</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        iterationRank: "0",
        status: "PASSED"
    ) {
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">status</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id or name of the status of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updateprecondition">updatePrecondition</strong></td>
<td valign="top"><a href="#precondition">Precondition</a></td>
<td>

Mutation used to update a Precondition
===
The mutation below will update the Precondition with id "49137"
<pre>
mutation {
    <b>updatePrecondition</b>(
        issueId: "49137",
        data: { preconditionType: {name: "Manual" }, definition: "Turn on calculator" }
    ) {
        issueId
        preconditionType {
            kind
            name
        }
        definition
    }
}
</pre>
===
===
The mutation below will update the Precondition with id "12345" and move it to the specified folder
<pre>
mutation {
    <b>updatePrecondition</b>(
        issueId: "12345",
        data: { folderPath: "/generic" }
    ) {
        issueId
        preconditionType {
            kind
            name
        }
        definition
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">data</td>
<td valign="top"><a href="#updatepreconditioninput">UpdatePreconditionInput</a></td>
<td>

the object containing the information to update the Precondition.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Precondition.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatepreconditionfolder">updatePreconditionFolder</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used update the precondition folder on the Test Repository.
===
The mutation below will add the precondition to "Component/UI" folder.
<pre>
mutation {
    <b>updatePreconditionFolder</b>(
        issueId: "12345",
        folderPath: "/Component/UI"
    )
}
</pre>
The mutation below will move the Precondition to the root.
<pre>
mutation {
    <b>updatePreconditionFolder</b>(
        issueId: "12345",
        folderPath: "/"
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">folderPath</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the Test repository folder for the Precondition.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Precondition.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestfolder">updateTestFolder</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used update the Test folder on the Test Repository.
===
The mutation below will add the test to "Component/UI" folder.
<pre>
mutation {
    <b>updateTestFolder</b>(
        issueId: "12345",
        folderPath: "/Component/UI"
    )
}
</pre>
The mutation below will move the Test to the root.
<pre>
mutation {
    <b>updateTestFolder</b>(
        issueId: "12345",
        folderPath: "/"
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">folderPath</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the Test repository folder for the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestrun">updateTestRun</strong></td>
<td valign="top"><a href="#updatetestrunresult">UpdateTestRunResult</a></td>
<td>

Mutation used to update a Test Run.
===
The mutation below updates a Test Run.
<pre>
mutation {
    <b>updateTestRun</b>( id: "5acc7ab0a3fe1b6fcdc3c737", comment: "Everything is OK.", startedOn: "2020-03-09T10:35:09Z", finishedOn: "2020-04-09T10:35:09Z", assigneeId: "e5983db2-90f7-4135-a96f-46907e72290e", executedById: "e5983db2-90f7-4135-a96f-46907e72290e") {
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">assigneeId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the assignee of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">comment</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the comment of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">customFields</td>
<td valign="top">[<a href="#customfieldinput">CustomFieldInput</a>]</td>
<td>

the customFields of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">executedById</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the executedBy of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">finishedOn</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the finishedOn of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">startedOn</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the startedOn of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestruncomment">updateTestRunComment</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to update the comment of a Test Run.
===
The mutation below updates the comment of a Test Run.
<pre>
mutation {
    <b>updateTestRunComment</b>( id: "5acc7ab0a3fe1b6fcdc3c737", comment: "Everything is OK.")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">comment</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the comment of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestrunexamplestatus">updateTestRunExampleStatus</strong></td>
<td valign="top"><a href="#updatetestrunexamplestatusresult">UpdateTestRunExampleStatusResult</a></td>
<td>

Mutation used to update the status of a Test Run Example.
===
The mutation below updates the status of a Test Run example.
<pre>
mutation {
    <b>updateTestRunExampleStatus</b>(
        exampleId: "5bbd8ab0a3fe1b6fcdc3c737",
        status: "PASSED"
    ) {
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">exampleId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Example.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">status</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id or name of the status of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestrunstatus">updateTestRunStatus</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to update the status of a Test Run.
===
The mutation below updates the status of a Test Run.
<pre>
mutation {
    <b>updateTestRunStatus</b>( id: "5acc7ab0a3fe1b6fcdc3c737", status: "PASSED")
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">id</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">status</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id or name of the status of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestrunstep">updateTestRunStep</strong></td>
<td valign="top"><a href="#updatetestrunstepresult">UpdateTestRunStepResult</a></td>
<td>

Mutation used to update the Test Run Step.
===
The mutation below will change the status, update the comment and add a defect to the Test Run Step.
<pre>
mutation {
    <b>updateTestRunStep</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        updateData: {
            comment: "Step failed"
            status: "FAILED"
            defects: {
                add: ["12345"]
            }
        }
    ) {
        addedDefects
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">updateData</td>
<td valign="top"><a href="#updatetestrunstepinput">UpdateTestRunStepInput</a>!</td>
<td>

the update information.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestrunstepcomment">updateTestRunStepComment</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mutation used to update the comment of a Test Run Step.
===
The mutation below updates the comment of a Test Run Step.
<pre>
mutation {
    <b>updateTestRunStepComment</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        comment: "This step is OK."
    )
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">comment</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the comment of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetestrunstepstatus">updateTestRunStepStatus</strong></td>
<td valign="top"><a href="#updatetestrunstepstatusresult">UpdateTestRunStepStatusResult</a></td>
<td>

Mutation used to update the status of a Test Run Step.
===
The mutation below updates the status of a Test Run Step.
<pre>
mutation {
    <b>updateTestRunStepStatus</b>(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        status: "PASSED"
    ) {
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">iterationRank</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">status</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id or name of the status of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testRunId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

The id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updateteststep">updateTestStep</strong></td>
<td valign="top"><a href="#updateteststepresult">UpdateTestStepResult</a></td>
<td>

Mutation used to update a Step of a Test.
===
The mutation below will update the Step with id "836d30ec-f034-4a03-879e-9c44a1d6d1fe".
<pre>
mutation {
    <b>updateTestStep</b>(
        stepId: "836d30ec-f034-4a03-879e-9c44a1d6d1fe",
        step: {
            result: "Xray Cloud Rest Api works as expected",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Lisbon"}]
        }
    ) {
        warnings
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">step</td>
<td valign="top"><a href="#updatestepinput">UpdateStepInput</a>!</td>
<td>

the information to update on the Step.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">stepId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the id of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updatetesttype">updateTestType</strong></td>
<td valign="top"><a href="#test">Test</a></td>
<td>

Mutation used to update the Test Type of a Test.
===
The mutation below will update the Test Type of the Test with id "12345".
<pre>
mutation {
    <b>updateTestType</b>(issueId: "12345", testType: {name: "Manual"} ) {
        issueId
        testType {
            name
            kind
        }
    }
}
</pre>
===
===
The mutation below will update the Test Type of the version 3 of the Test with id "12345".
<pre>
mutation {
    <b>updateTestType</b>(issueId: "12345", versionId: 3, testType: {name: "Manual"} ) {
        issueId
        testType {
            name
            kind
        }
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testType</td>
<td valign="top"><a href="#updatetesttypeinput">UpdateTestTypeInput</a>!</td>
<td>

the Test Type to update on the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="mutation.updateunstructuredtestdefinition">updateUnstructuredTestDefinition</strong></td>
<td valign="top"><a href="#test">Test</a></td>
<td>

Mutation used to update the Unstructured definition of a Test.
===
The mutation below will update the unstructured definition of the Test with id "12345".
<pre>
mutation {
    <b>updateUnstructuredTestDefinition</b>(issueId: "12345", unstructured: "Generic definition" ) {
        issueId
        unstructured
    }
}
</pre>
===
===
The mutation below will update the unstructured definition of the version 3 of the Test with id "12345".
<pre>
mutation {
    <b>updateUnstructuredTestDefinition</b>(issueId: "12345", versionId: 3, unstructured: "Generic definition" ) {
        issueId
        unstructured
    }
}
</pre>
===

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueId</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the issue id of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">unstructured</td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

the unstructured definition of the Test.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">versionId</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the id of a Test version. If not given, will update the default Test version.

</td>
</tr>
</tbody>
</table>

## Objects

### ActionFolderResult

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="actionfolderresult.folder">folder</strong></td>
<td valign="top"><a href="#simplefolderresults">SimpleFolderResults</a></td>
<td>

Folder updated during the operation.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="actionfolderresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warning generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddDefectsResult

Added Defects Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="adddefectsresult.addeddefects">addedDefects</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the added Defects.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="adddefectsresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddEvidenceResult

Add Evidence Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="addevidenceresult.addedevidence">addedEvidence</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the added Evidence.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addevidenceresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddPreconditionsResult

Add Preconditions Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="addpreconditionsresult.addedpreconditions">addedPreconditions</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Issue ids of the added Preconditions.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addpreconditionsresult.warning">warning</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Warning generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddTestEnvironmentsResult

Add Test Environments Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="addtestenvironmentsresult.associatedtestenvironments">associatedTestEnvironments</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Test Environments that were associated.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addtestenvironmentsresult.createdtestenvironments">createdTestEnvironments</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Test Environments that were created.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addtestenvironmentsresult.warning">warning</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Warning generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddTestExecutionsResult

Add Test Executions Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="addtestexecutionsresult.addedtestexecutions">addedTestExecutions</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Issue ids of the added Test Executions.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addtestexecutionsresult.warning">warning</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Warning generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddTestPlansResult

Add Test Plans Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="addtestplansresult.addedtestplans">addedTestPlans</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Issue ids of the added Test Plans.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addtestplansresult.warning">warning</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Warning generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddTestSetsResult

Add Test Sets Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="addtestsetsresult.addedtestsets">addedTestSets</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Issue ids of the added Test Set.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addtestsetsresult.warning">warning</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Warning generated during the operation.

</td>
</tr>
</tbody>
</table>

### AddTestsResult

Add Tests Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="addtestsresult.addedtests">addedTests</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Issue Ids of the added Tests.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="addtestsresult.warning">warning</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Warning generated during the operation.

</td>
</tr>
</tbody>
</table>

### Attachment

Step Attachment type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="attachment.downloadlink">downloadLink</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Download link of the attachment.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachment.filename">filename</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Filename of the attachment.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachment.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the attachment.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachment.storedinjira">storedInJira</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

If the file is stored in Jira.

</td>
</tr>
</tbody>
</table>

### Changes

Xray History Changes type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="changes.change">change</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Change details.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="changes.field">field</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Field the change refers to.

</td>
</tr>
</tbody>
</table>

### CoverableIssue

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="coverableissue.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Issue id of the Coverable Issue Issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coverableissue.jira">jira</strong></td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

Extra Jira information of the Coverable issue.

Arguments
fields: List of the fields to be displayed.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">fields</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td></td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coverableissue.status">status</strong></td>
<td valign="top"><a href="#coveragestatus">CoverageStatus</a></td>
<td>

Test Coverage Status of the Coverable Issue. This status can be calculated based on latest status, version or Test Plan.

Arguments
environment: the environment for which to calculate the for status.
isFinal: whether the final statuses has precedence over non-final.
version: the version name for which to calculate the status for.
testPlan: the Test Plan issue id for which to calculate the status for.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">environment</td>
<td valign="top"><a href="#string">String</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">isFinal</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlan</td>
<td valign="top"><a href="#string">String</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">version</td>
<td valign="top"><a href="#string">String</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coverableissue.tests">tests</strong></td>
<td valign="top"><a href="#testresults">TestResults</a></td>
<td>

List of Tests associated with the Coverable Issue issue.

Arguments
issueIds: the issue ids of the Tests.
limit: the maximum amount of tests to be returned. The maximum is 100.
start: the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td></td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td></td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td></td>
</tr>
</tbody>
</table>

### CoverableIssueResults

Coverable Issue Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="coverableissueresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The maximum amount of Coverable Issues to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coverableissueresults.results">results</strong></td>
<td valign="top">[<a href="#coverableissue">CoverableIssue</a>]</td>
<td>

Test issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coverableissueresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coverableissueresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coverableissueresults.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated if you have a invalid Coverable Issue

</td>
</tr>
</tbody>
</table>

### CoverageStatus

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="coveragestatus.color">color</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Color of the Coverage Status

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coveragestatus.description">description</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Description of the Coverage Status

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="coveragestatus.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Coverage Status

</td>
</tr>
</tbody>
</table>

### CreatePreconditionResult

Create Precondition Response type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="createpreconditionresult.precondition">precondition</strong></td>
<td valign="top"><a href="#precondition">Precondition</a></td>
<td>

Precondition that was created.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createpreconditionresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### CreateTestExecutionResult

Create Test Execution Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="createtestexecutionresult.createdtestenvironments">createdTestEnvironments</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Test Environments that were created.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createtestexecutionresult.testexecution">testExecution</strong></td>
<td valign="top"><a href="#testexecution">TestExecution</a></td>
<td>

Test Execution that was created.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createtestexecutionresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### CreateTestPlanResult

Create Test Plan Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="createtestplanresult.testplan">testPlan</strong></td>
<td valign="top"><a href="#testplan">TestPlan</a></td>
<td>

Test Plan that was created.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createtestplanresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### CreateTestResult

Create Test Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="createtestresult.test">test</strong></td>
<td valign="top"><a href="#test">Test</a></td>
<td>

Test that was created.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createtestresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### CreateTestSetResult

Create Test Set Result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="createtestsetresult.testset">testSet</strong></td>
<td valign="top"><a href="#testset">TestSet</a></td>
<td>

Test Set that was created.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createtestsetresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### CustomStepField

Step CustomField type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="customstepfield.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Custom Field.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="customstepfield.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Custom Field.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="customstepfield.value">value</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Value of the Custom Field.

</td>
</tr>
</tbody>
</table>

### Dataset

Dataset type
Represents a single Dataset entity with its metadata, parameters, and associated dataset rows.

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="dataset.calltestissueid">callTestIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The ID of the call test issue (only for test step datasets).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="dataset.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Unique identifier of the Dataset.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="dataset.parameters">parameters</strong></td>
<td valign="top">[<a href="#parameter">Parameter</a>]</td>
<td>

Parameters of the Dataset, represented as an array of key-value pairs.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="dataset.rows">rows</strong></td>
<td valign="top">[<a href="#datasetrow">DatasetRow</a>]</td>
<td>

The rows of the Dataset, representing combinatorial data.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="dataset.testexecissueid">testExecIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The ID of the test execution issue associated with the Dataset.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="dataset.testissueid">testIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The ID of the test issue associated with the Dataset.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="dataset.testplanissueid">testPlanIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The ID of the test plan issue associated with the Dataset.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="dataset.teststepid">testStepId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The ID of the test step associated with the Dataset (only for test step datasets).

</td>
</tr>
</tbody>
</table>

### DatasetRow

DatasetRow type
Represents a single row in the Dataset, containing combinatorial data.

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="datasetrow.values">Values</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

The values of the row, stored String array.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="datasetrow.order">order</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The order of the row in the Dataset.

</td>
</tr>
</tbody>
</table>

### Evidence

Evidence Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="evidence.createdon">createdOn</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Evidence creation timestamp.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="evidence.downloadlink">downloadLink</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Download link of the Evidence.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="evidence.filename">filename</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Filename of the Evidence.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="evidence.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Evidence.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="evidence.size">size</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

File size in bytes.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="evidence.storedinjira">storedInJira</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

If file is stored in Jira

</td>
</tr>
</tbody>
</table>

### Example

Example Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="example.duration">duration</strong></td>
<td valign="top"><a href="#float">Float</a></td>
<td>

Duration of the Example.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="example.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Example.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="example.status">status</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Status of the Example.

</td>
</tr>
</tbody>
</table>

### ExpandedStep

Expanded test step type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.action">action</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Action of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.attachments">attachments</strong></td>
<td valign="top">[<a href="#attachment">Attachment</a>]</td>
<td>

Attachments of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.calledtestissueid">calledTestIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The issue id of the called test with the step

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.customfields">customFields</strong></td>
<td valign="top">[<a href="#customstepfield">CustomStepField</a>]</td>
<td>

Custom Fields of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.parenttestissueid">parentTestIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The issue id of the test calling the step

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedstep.result">result</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Result of the Step.

</td>
</tr>
</tbody>
</table>

### ExpandedTest

Expaded test issue type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.coverableissues">coverableIssues</strong></td>
<td valign="top"><a href="#coverableissueresults">CoverableIssueResults</a></td>
<td>

List of Coverable Issues associated with the Test issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Coverable Issues

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Coverable Issues to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.dataset">dataset</strong></td>
<td valign="top"><a href="#dataset">Dataset</a></td>
<td>

Dataset linked to the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.folder">folder</strong></td>
<td valign="top"><a href="#folder">Folder</a></td>
<td>

Test Repository folder of the Test.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.gherkin">gherkin</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Gherkin definition of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.history">history</strong></td>
<td valign="top"><a href="#xrayhistoryresults">XrayHistoryResults</a></td>
<td>

List of Xray History results for the issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of entries to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Issue id of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.jira">jira</strong></td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

Extra Jira information of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">fields</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

List of the fields to be displayed.
Check the field '**fields**' of [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-issueIdOrKey-get) Jira endpoint for more information.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the test was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.preconditions">preconditions</strong></td>
<td valign="top"><a href="#preconditionresults">PreconditionResults</a></td>
<td>

List of Precondition associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Preconditions.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Preconditions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.projectid">projectId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project id of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.scenariotype">scenarioType</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Gherkin type of the Test issue.
Possible values: 'scenario' or 'scenario_outline'.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.status">status</strong></td>
<td valign="top"><a href="#teststatustype">TestStatusType</a></td>
<td>

Status of the Test. This status can be calculated based on latest status, version or Test Plan.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">environment</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the environment for which to calculate the for status.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">isFinal</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

whether the final statuses has precedence over non-final.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlan</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id for which to calculate the status for.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">version</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the version name for which to calculate the status for.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.steps">steps</strong></td>
<td valign="top">[<a href="#expandedstep">ExpandedStep</a>]</td>
<td>

Expanded step definition of the test.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.testexecutions">testExecutions</strong></td>
<td valign="top"><a href="#testexecutionresults">TestExecutionResults</a></td>
<td>

List of Test Executions associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Executions

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Executions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.testplans">testPlans</strong></td>
<td valign="top"><a href="#testplanresults">TestPlanResults</a></td>
<td>

List of Test Plans associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Plans

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Plans to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.testruns">testRuns</strong></td>
<td valign="top"><a href="#testrunresults">TestRunResults</a></td>
<td>

List of Test Runs for the Test issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Runs to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.testsets">testSets</strong></td>
<td valign="top"><a href="#testsetresults">TestSetResults</a></td>
<td>

List of Test Sets associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Sets

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Sets to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.testtype">testType</strong></td>
<td valign="top"><a href="#testtype">TestType</a></td>
<td>

Test type of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.testversions">testVersions</strong></td>
<td valign="top"><a href="#testversionresults">TestVersionResults</a></td>
<td>

List of Test versions of the Test

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">archived</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

if should include archived Test versions in the result.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test versions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testTypeId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

to filter Test versions by Test Type

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.unstructured">unstructured</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Unstructured definition of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.versionid">versionId</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Version id of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtest.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated while expanding the test steps.

</td>
</tr>
</tbody>
</table>

### ExpandedTestResults

Expanded tests results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="expandedtestresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The maximum amount of Tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtestresults.results">results</strong></td>
<td valign="top">[<a href="#expandedtest">ExpandedTest</a>]</td>
<td>

Expanded test issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtestresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="expandedtestresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
</tbody>
</table>

### Folder

Test Repository folder type.

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="folder.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Folder name

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="folder.path">path</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Folder path

</td>
</tr>
</tbody>
</table>

### FolderResults

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="folderresults.folders">folders</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Folder children

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="folderresults.issuescount">issuesCount</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Folder issues count

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="folderresults.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Folder name

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="folderresults.path">path</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Folder path

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="folderresults.preconditionscount">preconditionsCount</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Folder preconditions count

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="folderresults.testscount">testsCount</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Folder tests count

</td>
</tr>
</tbody>
</table>

### IssueLinkType

Issue Link Type type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="issuelinktype.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of Issue Link Type

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="issuelinktype.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of Issue Link Type

</td>
</tr>
</tbody>
</table>

### Parameter

Parameter type
Represents a single parameter in the Dataset.

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="parameter.combinations">combinations</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Indicates whether the parameter supports combinations.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="parameter.listvalues">listValues</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

The list of values for the parameter.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="parameter.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The name of the parameter.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="parameter.projectlistid">projectListId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The ID of the project list associated with the parameter.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="parameter.type">type</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The type of the parameter.

</td>
</tr>
</tbody>
</table>

### Precondition

Precondition issue type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="precondition.definition">definition</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Definition of the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.folder">folder</strong></td>
<td valign="top"><a href="#folder">Folder</a></td>
<td>

Test Repository folder of the Precondition.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.history">history</strong></td>
<td valign="top"><a href="#xrayhistoryresults">XrayHistoryResults</a></td>
<td>

List of Xray History results for the issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of entries to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.jira">jira</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Extra Jira information of the Precondition Issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">fields</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

list of the fields to be displayed.
Check the field '**fields**' of [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-issueIdOrKey-get) Jira endpoint for more information.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the precondition was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.preconditiontype">preconditionType</strong></td>
<td valign="top"><a href="#testtype">TestType</a></td>
<td>

Precondition Type of the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.projectid">projectId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project id of the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.testversions">testVersions</strong></td>
<td valign="top"><a href="#testversionresults">TestVersionResults</a></td>
<td>

List of the Test versions associated with the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">archived</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

if should include archived Test versions in the result.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test versions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testTypeId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

to filter Test versions by Test Type

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="precondition.tests">tests</strong></td>
<td valign="top"><a href="#testresults">TestResults</a></td>
<td>

List of the Tests associated with the Precondition issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
</tbody>
</table>

### PreconditionResults

Precondition Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="preconditionresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of Preconditions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="preconditionresults.results">results</strong></td>
<td valign="top">[<a href="#precondition">Precondition</a>]</td>
<td>

Precondition issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="preconditionresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="preconditionresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
</tbody>
</table>

### ProjectSettings

Project Settings type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="projectsettings.defectissuetypes">defectIssueTypes</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Defect Issue Types.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettings.projectid">projectId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project id.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettings.testcoveragesettings">testCoverageSettings</strong></td>
<td valign="top"><a href="#projectsettingstestcoverage">ProjectSettingsTestCoverage</a></td>
<td>

Test Coverage Settings.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettings.testenvironments">testEnvironments</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Test Environments.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettings.testruncustomfieldsettings">testRunCustomFieldSettings</strong></td>
<td valign="top"><a href="#projectsettingstestruncustomfields">ProjectSettingsTestRunCustomFields</a></td>
<td>

Test Run Custom Fields Settings.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettings.teststepsettings">testStepSettings</strong></td>
<td valign="top"><a href="#projectsettingsteststepsettings">ProjectSettingsTestStepSettings</a></td>
<td>

Test Step Settings.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettings.testtypesettings">testTypeSettings</strong></td>
<td valign="top"><a href="#projectsettingstesttype">ProjectSettingsTestType</a></td>
<td>

Test Type Settings.

</td>
</tr>
</tbody>
</table>

### ProjectSettingsTestCoverage

Project Test Coverage Settings type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestcoverage.coverableissuetypeids">coverableIssueTypeIds</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Coverable issue type ids

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestcoverage.epicissuesrelation">epicIssuesRelation</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Epic - Issues(Stories) relation

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestcoverage.issuelinktypedirection">issueLinkTypeDirection</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Issue Link Type Direction

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestcoverage.issuelinktypeid">issueLinkTypeId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Issue Link Type Id

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestcoverage.issuesubtasksrelation">issueSubTasksRelation</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Issue - Sub-tasks relation

</td>
</tr>
</tbody>
</table>

### ProjectSettingsTestRunCustomField

Project Test Run Custom Field Settings type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestruncustomfield.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestruncustomfield.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestruncustomfield.required">required</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Is the field required

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestruncustomfield.type">type</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Type

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestruncustomfield.values">values</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Values

</td>
</tr>
</tbody>
</table>

### ProjectSettingsTestRunCustomFields

Project Test Run Custom Field Field Settings type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstestruncustomfields.fields">fields</strong></td>
<td valign="top">[<a href="#projectsettingstestruncustomfield">ProjectSettingsTestRunCustomField</a>]</td>
<td>

Fields

</td>
</tr>
</tbody>
</table>

### ProjectSettingsTestStepField

Project Test Step Field Settings type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingsteststepfield.disabled">disabled</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Is the field disabled

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingsteststepfield.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingsteststepfield.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingsteststepfield.required">required</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Is the field required

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingsteststepfield.type">type</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Type

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingsteststepfield.values">values</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Values

</td>
</tr>
</tbody>
</table>

### ProjectSettingsTestStepSettings

Project Test Step Settings type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingsteststepsettings.fields">fields</strong></td>
<td valign="top">[<a href="#projectsettingsteststepfield">ProjectSettingsTestStepField</a>]</td>
<td>

Fields

</td>
</tr>
</tbody>
</table>

### ProjectSettingsTestType

Project Test Type Settings type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstesttype.defaulttesttypeid">defaultTestTypeId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Default Test Type Id

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="projectsettingstesttype.testtypes">testTypes</strong></td>
<td valign="top">[<a href="#testtype">TestType</a>]</td>
<td>

Test Types

</td>
</tr>
</tbody>
</table>

### RemoveDefectsResult

Remove defects Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="removedefectsresult.removeddefects">removedDefects</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the removed Defects.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="removedefectsresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### RemoveEvidenceResult

Remove Evidence Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="removeevidenceresult.removedevidence">removedEvidence</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the removed Evidence.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="removeevidenceresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### Result

Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="result.backgrounds">backgrounds</strong></td>
<td valign="top">[<a href="#resultsstep">ResultsStep</a>]</td>
<td>

Backgrounds of the Results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.duration">duration</strong></td>
<td valign="top"><a href="#float">Float</a></td>
<td>

Duration of the Result.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.examples">examples</strong></td>
<td valign="top">[<a href="#resultsexample">ResultsExample</a>]</td>
<td>

Examples of the Result.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.hooks">hooks</strong></td>
<td valign="top">[<a href="#resultsstep">ResultsStep</a>]</td>
<td>

Hooks of the Results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.log">log</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Output if exist an error or a failure (JUNIT, XUNIT, NUNIT, TESTNG)

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Result.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.status">status</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Status of the Result.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.steps">steps</strong></td>
<td valign="top">[<a href="#resultsstep">ResultsStep</a>]</td>
<td>

Steps of the Results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="result.wasimported">wasImported</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Whether or not the Result was imported.

</td>
</tr>
</tbody>
</table>

### ResultsEmbedding

Results Embedding

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="resultsembedding.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the Embedding. Base64 format.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsembedding.downloadlink">downloadLink</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Link to download the embedding if no data is present

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsembedding.filename">filename</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Filename of the Embedding.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsembedding.mimetype">mimeType</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Mime Type of the Embedding.

</td>
</tr>
</tbody>
</table>

### ResultsExample

Results Example Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="resultsexample.backgrounds">backgrounds</strong></td>
<td valign="top">[<a href="#resultsstep">ResultsStep</a>]</td>
<td>

Backgrounds of the Results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsexample.duration">duration</strong></td>
<td valign="top"><a href="#float">Float</a></td>
<td>

Duration of the Result.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsexample.hooks">hooks</strong></td>
<td valign="top">[<a href="#resultsstep">ResultsStep</a>]</td>
<td>

Hooks of the Results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsexample.status">status</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Status of the Result.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsexample.steps">steps</strong></td>
<td valign="top">[<a href="#resultsstep">ResultsStep</a>]</td>
<td>

Steps of the Results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsexample.wasimported">wasImported</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Whether or not the Result was imported.

</td>
</tr>
</tbody>
</table>

### ResultsStep

Results Step

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="resultsstep.duration">duration</strong></td>
<td valign="top"><a href="#float">Float</a></td>
<td>

Duration of the step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsstep.embeddings">embeddings</strong></td>
<td valign="top">[<a href="#resultsembedding">ResultsEmbedding</a>]</td>
<td>

Embeddings of the step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsstep.error">error</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Error of the step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsstep.keyword">keyword</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

If a gherkin step, keyword of the gherkin step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsstep.log">log</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

If a Robot step, output of the Robot step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsstep.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="resultsstep.status">status</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Status of the step.

</td>
</tr>
</tbody>
</table>

### SimpleFolderResults

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="simplefolderresults.issuescount">issuesCount</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Folder issues count

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="simplefolderresults.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Folder name

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="simplefolderresults.path">path</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Folder path

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="simplefolderresults.preconditionscount">preconditionsCount</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Folder preconditions count

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="simplefolderresults.testscount">testsCount</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Folder tests count

</td>
</tr>
</tbody>
</table>

### Status

Status Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="status.color">color</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Color of the Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="status.coveragestatus">coverageStatus</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Coverage mapping of the Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="status.description">description</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Description of the Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="status.final">final</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Whether the Status is final or not.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="status.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Status.

</td>
</tr>
</tbody>
</table>

### Step

Test Step type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="step.action">action</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Action of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="step.attachments">attachments</strong></td>
<td valign="top">[<a href="#attachment">Attachment</a>]</td>
<td>

Attachments of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="step.calltestissueid">callTestIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The issue id of the test being called in the step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="step.customfields">customFields</strong></td>
<td valign="top">[<a href="#customstepfield">CustomStepField</a>]</td>
<td>

Custom Fields of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="step.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="step.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="step.result">result</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Result of the Step.

</td>
</tr>
</tbody>
</table>

### StepStatus

Step Status Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="stepstatus.color">color</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Color of the Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="stepstatus.description">description</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Description of the Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="stepstatus.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="stepstatus.teststatus">testStatus</strong></td>
<td valign="top"><a href="#status">Status</a></td>
<td>

The test status to which the step status is mapped to.

</td>
</tr>
</tbody>
</table>

### Test

Test issue type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="test.coverableissues">coverableIssues</strong></td>
<td valign="top"><a href="#coverableissueresults">CoverableIssueResults</a></td>
<td>

List of Coverable Issues associated with the Test issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Coverable Issues

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Coverable Issues to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.dataset">dataset</strong></td>
<td valign="top"><a href="#dataset">Dataset</a></td>
<td>

Dataset linked to the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.folder">folder</strong></td>
<td valign="top"><a href="#folder">Folder</a></td>
<td>

Test Repository folder of the Test.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.gherkin">gherkin</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Gherkin definition of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.history">history</strong></td>
<td valign="top"><a href="#xrayhistoryresults">XrayHistoryResults</a></td>
<td>

List of Xray History results for the issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of entries to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Issue id of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.jira">jira</strong></td>
<td valign="top"><a href="#json">JSON</a>!</td>
<td>

Extra Jira information of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">fields</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

List of the fields to be displayed.
Check the field '**fields**' of [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-issueIdOrKey-get) Jira endpoint for more information.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the test was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.preconditions">preconditions</strong></td>
<td valign="top"><a href="#preconditionresults">PreconditionResults</a></td>
<td>

List of Precondition associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Preconditions.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Preconditions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.projectid">projectId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project id of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.scenariotype">scenarioType</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Gherkin type of the Test issue.
Possible values: 'scenario' or 'scenario_outline'.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.status">status</strong></td>
<td valign="top"><a href="#teststatustype">TestStatusType</a></td>
<td>

Status of the Test. This status can be calculated based on latest status, version or Test Plan.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">environment</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the environment for which to calculate the for status.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">isFinal</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

whether the final statuses has precedence over non-final.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testPlan</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the Test Plan id for which to calculate the status for.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">version</td>
<td valign="top"><a href="#string">String</a></td>
<td>

the version name for which to calculate the status for.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.steps">steps</strong></td>
<td valign="top">[<a href="#step">Step</a>]</td>
<td>

Step definition of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.testexecutions">testExecutions</strong></td>
<td valign="top"><a href="#testexecutionresults">TestExecutionResults</a></td>
<td>

List of Test Executions associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Executions

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Executions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.testplans">testPlans</strong></td>
<td valign="top"><a href="#testplanresults">TestPlanResults</a></td>
<td>

List of Test Plans associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Plans

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Plans to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.testruns">testRuns</strong></td>
<td valign="top"><a href="#testrunresults">TestRunResults</a></td>
<td>

List of Test Runs for the Test issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Runs to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.testsets">testSets</strong></td>
<td valign="top"><a href="#testsetresults">TestSetResults</a></td>
<td>

List of Test Sets associated with the Test issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Sets

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Sets to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.testtype">testType</strong></td>
<td valign="top"><a href="#testtype">TestType</a></td>
<td>

Test type of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.testversions">testVersions</strong></td>
<td valign="top"><a href="#testversionresults">TestVersionResults</a></td>
<td>

List of Test versions of the Test

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">archived</td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

if should include archived Test versions in the result.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test versions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">testTypeId</td>
<td valign="top"><a href="#string">String</a></td>
<td>

to filter Test versions by Test Type

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="test.unstructured">unstructured</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Unstructured definition of the Test issue.

</td>
</tr>
</tbody>
</table>

### TestExecution

Test Execution issue type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.history">history</strong></td>
<td valign="top"><a href="#xrayhistoryresults">XrayHistoryResults</a></td>
<td>

List of Xray History results for the issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of entries to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Execution issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.jira">jira</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Extra Jira information of the Test Execution Issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">fields</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

List of the fields to be displayed.
Check the field '**fields**' of [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-issueIdOrKey-get) Jira endpoint for more information.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the test exec was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.projectid">projectId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project id of the Test Execution issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.testenvironments">testEnvironments</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Test Environments of the Test Execution.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.testplans">testPlans</strong></td>
<td valign="top"><a href="#testplanresults">TestPlanResults</a></td>
<td>

List of Test Plans associated with the Test Execution Issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the Test Plans.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Plans to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.testruns">testRuns</strong></td>
<td valign="top"><a href="#testrunresults">TestRunResults</a></td>
<td>

List of Test Runs for the Test Execution Issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecution.tests">tests</strong></td>
<td valign="top"><a href="#testresults">TestResults</a></td>
<td>

List of Tests associated with the Test Execution Issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
</tbody>
</table>

### TestExecutionResults

Test Execution Results Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testexecutionresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of Test Executions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecutionresults.results">results</strong></td>
<td valign="top">[<a href="#testexecution">TestExecution</a>]</td>
<td>

Test Execution issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecutionresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testexecutionresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
</tbody>
</table>

### TestPlan

Test Plan issue type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testplan.folders">folders</strong></td>
<td valign="top"><a href="#folderresults">FolderResults</a></td>
<td>

Folder structure of the Test Plan.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplan.history">history</strong></td>
<td valign="top"><a href="#xrayhistoryresults">XrayHistoryResults</a></td>
<td>

List of Xray History results for the issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of entries to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplan.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Plan issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplan.jira">jira</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Extra Jira information of the Test Plan issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">fields</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

list of the fields to be displayed.
Check the field '**fields**' of [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-issueIdOrKey-get) Jira endpoint for more information.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplan.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the test plan was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplan.projectid">projectId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project id of the Test Plan issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplan.testexecutions">testExecutions</strong></td>
<td valign="top"><a href="#testexecutionresults">TestExecutionResults</a></td>
<td>

List of Test Executions associated with the Test Plan issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

issue ids of the Test Executions.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplan.tests">tests</strong></td>
<td valign="top"><a href="#testresults">TestResults</a></td>
<td>

List of Tests associated with the Test Plan issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
</tbody>
</table>

### TestPlanResults

Test Plan Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testplanresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of Test Plans to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplanresults.results">results</strong></td>
<td valign="top">[<a href="#testplan">TestPlan</a>]</td>
<td>

Test Plan issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplanresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplanresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testplanresults.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### TestResults

Test Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The maximum amount of Tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testresults.results">results</strong></td>
<td valign="top">[<a href="#test">Test</a>]</td>
<td>

Test issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testresults.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated if you have a invalid Test

</td>
</tr>
</tbody>
</table>

### TestRun

Test Run type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrun.assigneeid">assigneeId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

User's account id assigned to the Test Run. This is user assigned to the Test Run, not taking into account the assignee of the test execution.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.comment">comment</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Comment definition of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.customfields">customFields</strong></td>
<td valign="top">[<a href="#testruncustomfieldvalue">TestRunCustomFieldValue</a>]</td>
<td>

Custom Fields of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.defects">defects</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Defects of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.evidence">evidence</strong></td>
<td valign="top">[<a href="#evidence">Evidence</a>]</td>
<td>

Evidence of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.examples">examples</strong></td>
<td valign="top">[<a href="#example">Example</a>]</td>
<td>

Examples of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.executedbyid">executedById</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

User's account id that executed the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.finishedon">finishedOn</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Finished On date of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.gherkin">gherkin</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Cucumber definition of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.iterations">iterations</strong></td>
<td valign="top"><a href="#testruniterationresults">TestRunIterationResults</a></td>
<td>

Iterations of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of iterations to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the test run was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.parameters">parameters</strong></td>
<td valign="top">[<a href="#testrunparameter">TestRunParameter</a>]</td>
<td>

Parameters of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.preconditions">preconditions</strong></td>
<td valign="top"><a href="#testrunpreconditionresults">TestRunPreconditionResults</a></td>
<td>

Preconditions of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Preconditions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.results">results</strong></td>
<td valign="top">[<a href="#result">Result</a>]</td>
<td>

Results of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.scenariotype">scenarioType</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Cucumber Type definition of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.startedon">startedOn</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Started On date of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.status">status</strong></td>
<td valign="top"><a href="#status">Status</a></td>
<td>

Status of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.steps">steps</strong></td>
<td valign="top">[<a href="#testrunstep">TestRunStep</a>]</td>
<td>

Step definition of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.test">test</strong></td>
<td valign="top"><a href="#test">Test</a></td>
<td>

Test of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.testexecution">testExecution</strong></td>
<td valign="top"><a href="#testexecution">TestExecution</a></td>
<td>

Test Execution of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.testtype">testType</strong></td>
<td valign="top"><a href="#testtype">TestType</a></td>
<td>

Test Type of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.testversion">testVersion</strong></td>
<td valign="top"><a href="#testversion">TestVersion</a></td>
<td>

Test version of the Test Run.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrun.unstructured">unstructured</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Generic definition of the Test issue.

</td>
</tr>
</tbody>
</table>

### TestRunCustomFieldValue

Custom Fields Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testruncustomfieldvalue.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruncustomfieldvalue.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruncustomfieldvalue.values">values</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td></td>
</tr>
</tbody>
</table>

### TestRunCustomStepField

Step CustomField type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testruncustomstepfield.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Custom Field.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruncustomstepfield.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Custom Field.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruncustomstepfield.value">value</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Value of the Custom Field.

</td>
</tr>
</tbody>
</table>

### TestRunIteration

Test Run iteration type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testruniteration.parameters">parameters</strong></td>
<td valign="top">[<a href="#testrunparameter">TestRunParameter</a>]</td>
<td>

Parameters of the iteration.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniteration.rank">rank</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Rank of the iteration.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniteration.status">status</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Status of the iteration.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniteration.stepresults">stepResults</strong></td>
<td valign="top"><a href="#testruniterationstepresults">TestRunIterationStepResults</a></td>
<td>

Step results of the iteration.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of step results to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
</tbody>
</table>

### TestRunIterationResults

Test Run iterations results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of iterations to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationresults.results">results</strong></td>
<td valign="top">[<a href="#testruniteration">TestRunIteration</a>]</td>
<td>

Iteration results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of iterations.

</td>
</tr>
</tbody>
</table>

### TestRunIterationStepResult

Test Run iteration step result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresult.actualresult">actualResult</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Actual Result of the Test Run step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresult.comment">comment</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Comment of the Test Run step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresult.defects">defects</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Defects of the Test Run step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresult.evidence">evidence</strong></td>
<td valign="top">[<a href="#evidence">Evidence</a>]</td>
<td>

Evidence of the Test Run step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresult.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Run step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresult.status">status</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Status of the Test Run step.

</td>
</tr>
</tbody>
</table>

### TestRunIterationStepResults

Test Run iteration step results results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of step results to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresults.results">results</strong></td>
<td valign="top">[<a href="#testruniterationstepresult">TestRunIterationStepResult</a>]</td>
<td>

Step results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testruniterationstepresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of steps.

</td>
</tr>
</tbody>
</table>

### TestRunParameter

Test Run parameter type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrunparameter.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunparameter.value">value</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td></td>
</tr>
</tbody>
</table>

### TestRunPrecondition

Test Run Precondition type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrunprecondition.definition">definition</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Precondition definition.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunprecondition.preconditionref">preconditionRef</strong></td>
<td valign="top"><a href="#precondition">Precondition</a></td>
<td>

Precondition of the Test Run.

</td>
</tr>
</tbody>
</table>

### TestRunPreconditionResults

Precondition Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrunpreconditionresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of Preconditions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunpreconditionresults.results">results</strong></td>
<td valign="top">[<a href="#testrunprecondition">TestRunPrecondition</a>]</td>
<td>

Precondition results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunpreconditionresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunpreconditionresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of preconditions.

</td>
</tr>
</tbody>
</table>

### TestRunResults

Test Run Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrunresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The maximum amount of Test Runs to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunresults.results">results</strong></td>
<td valign="top">[<a href="#testrun">TestRun</a>]</td>
<td>

Test Run results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of Test Runs.

</td>
</tr>
</tbody>
</table>

### TestRunStep

Test Run Step Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.action">action</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Action of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.actualresult">actualResult</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Actual Result of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.attachments">attachments</strong></td>
<td valign="top">[<a href="#attachment">Attachment</a>]</td>
<td>

Attachments of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.comment">comment</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Comment of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.customfields">customFields</strong></td>
<td valign="top">[<a href="#testruncustomstepfield">TestRunCustomStepField</a>]</td>
<td>

Custom Fields of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.defects">defects</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Defects of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.evidence">evidence</strong></td>
<td valign="top">[<a href="#evidence">Evidence</a>]</td>
<td>

Evidence of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.result">result</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Result of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunstep.status">status</strong></td>
<td valign="top"><a href="#stepstatus">StepStatus</a></td>
<td>

Status of the Test Run Step.

</td>
</tr>
</tbody>
</table>

### TestSet

Test Set type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testset.history">history</strong></td>
<td valign="top"><a href="#xrayhistoryresults">XrayHistoryResults</a></td>
<td>

List of Xray History results for the issue

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of entries to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testset.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Issue id of the Test Set Issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testset.jira">jira</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Extra Jira information of the Test Set Issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">fields</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

List of the fields to be displayed.
Check the field '**fields**' of [this](https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-api-3-issue-issueIdOrKey-get) Jira endpoint for more information.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testset.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the test set was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testset.projectid">projectId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Project id of the Test Set Issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testset.tests">tests</strong></td>
<td valign="top"><a href="#testresults">TestResults</a></td>
<td>

List of Tests associated with the Test Set Issue.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the Tests.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

Maximum amount of tests to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
</tbody>
</table>

### TestSetResults

Test Set Results

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testsetresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of test sets to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testsetresults.results">results</strong></td>
<td valign="top">[<a href="#testset">TestSet</a>]</td>
<td>

Test Set issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testsetresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testsetresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
</tbody>
</table>

### TestStatusType

Test Status Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="teststatustype.color">color</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Color of the Test Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="teststatustype.description">description</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Description of the Test Status.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="teststatustype.final">final</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Whether the status is final or not.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="teststatustype.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Test Status.

</td>
</tr>
</tbody>
</table>

### TestType

Test Type type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testtype.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Type.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testtype.kind">kind</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Kind of the Test Type.
Possible values are "Gherkin", "Steps" or "Unstructured".

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testtype.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Test Type.

</td>
</tr>
</tbody>
</table>

### TestVersion

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testversion.archived">archived</strong></td>
<td valign="top"><a href="#boolean">Boolean</a>!</td>
<td>

If is an archived Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.default">default</strong></td>
<td valign="top"><a href="#boolean">Boolean</a>!</td>
<td>

If is the default Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.gherkin">gherkin</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Gherkin definition of the Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.id">id</strong></td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

Number of the Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.lastmodified">lastModified</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date when the Test version was last modified.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.name">name</strong></td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

Name of the Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.preconditions">preconditions</strong></td>
<td valign="top"><a href="#preconditionresults">PreconditionResults</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the ids of the Preconditions.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Preconditions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.scenariotype">scenarioType</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Gherkin type of the Test version.
Possible values: 'scenario' or 'scenario_outline'.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.steps">steps</strong></td>
<td valign="top">[<a href="#step">Step</a>]</td>
<td>

Step definition of the Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.test">test</strong></td>
<td valign="top"><a href="#test">Test</a>!</td>
<td></td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.testexecutions">testExecutions</strong></td>
<td valign="top"><a href="#testexecutionresults">TestExecutionResults</a></td>
<td>

List of Test Executions associated with the Test version.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">issueIds</td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

the issue ids of the Test Executions

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Executions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.testruns">testRuns</strong></td>
<td valign="top"><a href="#testrunresults">TestRunResults</a></td>
<td></td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">limit</td>
<td valign="top"><a href="#int">Int</a>!</td>
<td>

the maximum amount of Test Runs to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" align="right" valign="top">start</td>
<td valign="top"><a href="#int">Int</a></td>
<td>

the index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.testtype">testType</strong></td>
<td valign="top"><a href="#testtype">TestType</a></td>
<td>

Test type of the Test version.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversion.unstructured">unstructured</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Unstructured definition of the Test version.

</td>
</tr>
</tbody>
</table>

### TestVersionResults

Test version results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testversionresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The maximum amount of Test versions to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversionresults.results">results</strong></td>
<td valign="top">[<a href="#testversion">TestVersion</a>]</td>
<td>

Test version results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversionresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

The index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testversionresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of Test versions.

</td>
</tr>
</tbody>
</table>

### UpdateIterationStatusResult

Update Test Run iteration status result type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updateiterationstatusresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### UpdateTestRunExampleStatusResult

Update Test Run Example Status Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunexamplestatusresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### UpdateTestRunResult

Update Test Run Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### UpdateTestRunStepResult

Update Test Run Step Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepresult.addeddefects">addedDefects</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the added Defects.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepresult.addedevidence">addedEvidence</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the added Evidence.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepresult.removeddefects">removedDefects</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the removed Defects.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepresult.removedevidence">removedEvidence</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the removed Evidence.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### UpdateTestRunStepStatusResult

Update Test Run Step Status Result Type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepstatusresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### UpdateTestStepResult

Update Test Step Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updateteststepresult.addedattachments">addedAttachments</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

List of added attachments.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updateteststepresult.removedattachments">removedAttachments</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

List of removed attachments.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updateteststepresult.warnings">warnings</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Warnings generated during the operation.

</td>
</tr>
</tbody>
</table>

### XrayHistoryEntry

Xray History Entry type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryentry.action">action</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Action performed.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryentry.changes">changes</strong></td>
<td valign="top">[<a href="#changes">Changes</a>]</td>
<td>

Details of the change(s).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryentry.date">date</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Date of change(s).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryentry.user">user</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

User that performed the change(s).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryentry.version">version</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Test Version that the changes refer to (if applicable).

</td>
</tr>
</tbody>
</table>

### XrayHistoryResults

Xray History Results type

<table>
<thead>
<tr>
<th align="left">Field</th>
<th align="right">Argument</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryresults.limit">limit</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Maximum amount of History results to be returned. The maximum is 100.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryresults.results">results</strong></td>
<td valign="top">[<a href="#xrayhistoryentry">XrayHistoryEntry</a>]</td>
<td>

Precondition issue results.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryresults.start">start</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Index of the first item to return in the page of results (page offset).

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="xrayhistoryresults.total">total</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Total amount of issues.

</td>
</tr>
</tbody>
</table>

## Inputs

### AttachmentDataInput

Attachment Data Input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="attachmentdatainput.attachmentid">attachmentId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of an attachment.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachmentdatainput.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the attachment. Base64 format.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachmentdatainput.filename">filename</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

 A valid <b>AttachmentDataInput</b> must have the properties <b>filename</b>, <b>mimeType</b> and <b>data</b> defined.
In alternative, the <b>attachmentId</b> property can be used alone.
If both <b>attachmentId</b> and other properties are defined, <b>attachmentId</b> takes precedence and will be used as if it was defined alone.


Filename of the attachment.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachmentdatainput.mimetype">mimeType</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Content Type of the attachment.

</td>
</tr>
</tbody>
</table>

### AttachmentInput

Attachment input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="attachmentinput.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the attachment. This data should be in base64.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachmentinput.filename">filename</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Filename of the attachment.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachmentinput.mimetype">mimeType</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Content Type of the attachment.

</td>
</tr>
</tbody>
</table>

### AttachmentOperationsInput

Attachment Operations Input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="attachmentoperationsinput.add">add</strong></td>
<td valign="top">[<a href="#attachmentinput">AttachmentInput</a>]</td>
<td>

Attachments to add to the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachmentoperationsinput.removefilenames">removeFilenames</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Filenames of the attachments to remove from the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="attachmentoperationsinput.removeids">removeIds</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Ids of the attachments to remove from the Step.

</td>
</tr>
</tbody>
</table>

### CreateStepInput

Create Step input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="createstepinput.action">action</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Action of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createstepinput.attachments">attachments</strong></td>
<td valign="top">[<a href="#attachmentinput">AttachmentInput</a>]</td>
<td>

Attachments of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createstepinput.calltestissueid">callTestIssueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

The issue id of the test called by the step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createstepinput.customfields">customFields</strong></td>
<td valign="top">[<a href="#customstepfieldinput">CustomStepFieldInput</a>]</td>
<td>

Custom Fields of the Step

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createstepinput.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="createstepinput.result">result</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Result of the Step.

</td>
</tr>
</tbody>
</table>

### CustomFieldInput

Custom Field Input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="customfieldinput.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the custom field.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="customfieldinput.value">value</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

Value of the custom field.

</td>
</tr>
</tbody>
</table>

### CustomStepFieldInput

Step Custom Field input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="customstepfieldinput.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Custom Field.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="customstepfieldinput.value">value</strong></td>
<td valign="top"><a href="#json">JSON</a></td>
<td>

value of the Custom Field.

</td>
</tr>
</tbody>
</table>

### FolderSearchInput

Folder Search input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="foldersearchinput.includedescendants">includeDescendants</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Whether descendant folders should be included in the search.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="foldersearchinput.path">path</strong></td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

Path of the Folder.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="foldersearchinput.testplanid">testPlanId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Test Plan id of the Folder.

</td>
</tr>
</tbody>
</table>

### PreconditionFolderSearchInput

Folder Search input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="preconditionfoldersearchinput.includedescendants">includeDescendants</strong></td>
<td valign="top"><a href="#boolean">Boolean</a></td>
<td>

Whether descendant folders should be included in the search.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="preconditionfoldersearchinput.path">path</strong></td>
<td valign="top"><a href="#string">String</a>!</td>
<td>

Path of the Folder.

</td>
</tr>
</tbody>
</table>

### TestRunDefectOperationsInput

Test Run Defect Operations Input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrundefectoperationsinput.add">add</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Defects to add to the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrundefectoperationsinput.remove">remove</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Defects to remove from the Test Run Step.

</td>
</tr>
</tbody>
</table>

### TestRunEvidenceOperationsInput

Test Run Evidence Operations Input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testrunevidenceoperationsinput.add">add</strong></td>
<td valign="top">[<a href="#attachmentdatainput">AttachmentDataInput</a>]</td>
<td>

Evidence to add to the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunevidenceoperationsinput.removefilenames">removeFilenames</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Evidence filenames to remove from the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testrunevidenceoperationsinput.removeids">removeIds</strong></td>
<td valign="top">[<a href="#string">String</a>]</td>
<td>

Evidence ids to remove from the Test Run Step.

</td>
</tr>
</tbody>
</table>

### TestTypeInput

Test Type input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testtypeinput.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Type.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testtypeinput.kind">kind</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Kind of the Test Type.
Possible values are "Gherkin", "Steps" or "Unstructured".

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testtypeinput.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Test Type.

</td>
</tr>
</tbody>
</table>

### TestWithVersionInput

Test with Version input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="testwithversioninput.issueid">issueId</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Issue id of the Test issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="testwithversioninput.versionid">versionId</strong></td>
<td valign="top"><a href="#int">Int</a></td>
<td>

Test Version id of the Test Issue

</td>
</tr>
</tbody>
</table>

### UpdatePreconditionInput

Update Precondition input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatepreconditioninput.definition">definition</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Definition of the Precondition Issue.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatepreconditioninput.folderpath">folderPath</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

the repository path to which the Precondition should be moved to

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatepreconditioninput.preconditiontype">preconditionType</strong></td>
<td valign="top"><a href="#updatepreconditiontypeinput">UpdatePreconditionTypeInput</a></td>
<td>

Precondition type of the Precondition Issue.

</td>
</tr>
</tbody>
</table>

### UpdatePreconditionTypeInput

Precondition Type input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatepreconditiontypeinput.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Precondition Type.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatepreconditiontypeinput.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Precondition Type.

</td>
</tr>
</tbody>
</table>

### UpdateStepInput

Update Step input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatestepinput.action">action</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Action of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatestepinput.attachments">attachments</strong></td>
<td valign="top"><a href="#attachmentoperationsinput">AttachmentOperationsInput</a></td>
<td>

Attachments of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatestepinput.customfields">customFields</strong></td>
<td valign="top">[<a href="#customstepfieldinput">CustomStepFieldInput</a>]</td>
<td>

Custom Fields of the Step

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatestepinput.data">data</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Data of the Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatestepinput.result">result</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Result of the Step.

</td>
</tr>
</tbody>
</table>

### UpdateTestRunStepInput

Update Test Run Step Input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepinput.actualresult">actualResult</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Actual Result of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepinput.comment">comment</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Comment to add to the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepinput.defects">defects</strong></td>
<td valign="top"><a href="#testrundefectoperationsinput">TestRunDefectOperationsInput</a></td>
<td>

Defects of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepinput.evidence">evidence</strong></td>
<td valign="top"><a href="#testrunevidenceoperationsinput">TestRunEvidenceOperationsInput</a></td>
<td>

Evidence of the Test Run Step.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetestrunstepinput.status">status</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Status to set to the Test Run Step.

</td>
</tr>
</tbody>
</table>

### UpdateTestTypeInput

Test Type input

<table>
<thead>
<tr>
<th colspan="2" align="left">Field</th>
<th align="left">Type</th>
<th align="left">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="2" valign="top"><strong id="updatetesttypeinput.id">id</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Id of the Test Type.

</td>
</tr>
<tr>
<td colspan="2" valign="top"><strong id="updatetesttypeinput.name">name</strong></td>
<td valign="top"><a href="#string">String</a></td>
<td>

Name of the Test Type.

</td>
</tr>
</tbody>
</table>

## Scalars

### Boolean

The `Boolean` scalar type represents `true` or `false`.

### Float

The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).

### Int

The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.

### JSON

The `JSON` scalar type represents JSON values as specified by [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf).

### String

The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.

