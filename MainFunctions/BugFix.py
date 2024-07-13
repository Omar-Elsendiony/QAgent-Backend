from Imports import *
from utils.CustomThread import *


class BugFix:

    def __init__(
        self,
        BugFixChain,
        myglobals,
        firstFeedback=True,
    ):
        self.BugFixChain = BugFixChain
        self.myglobals = myglobals
        self.firstFeedback = firstFeedback

    def generate(
        self,
        Description,
        codeUnderTest,
        allTestcases,
        errorTestCases,
        errorMessage,
    ):
        """
        This function is responsible for Fixing Bugs in Code and running the code with generated tests
        The function is responsible for:
        1. Extracting the code and description from the example
        2. Fixing Bugs in Code
        3. Running the test cases
        4. Storing the results in a JSON file
        Args: None
        Return: None
        """
        # TODO: Might need judgement back again!
        # no feedback means testcase passed so don't run it again
        # truncated from step before
        # if (
        #     "OK" in currFeedback
        #     or pd.isna(currFeedback)
        #     or currFeedback == ""
        #     or currFeedback is None
        # ):
        #     print("Example", i, " has already passed")
        #     c.write(
        #         "Example "
        #         + str(i)
        #         + " has already passed\n=====================================\n"
        #     )
        #     continue
        # if Judgement == "True":
        #     print("Example", i, " has been judged to contain erroneous test cases")
        #     c.write(
        #         "Example "
        #         + str(i)
        #         + " has been judged to contain erroneous test cases\n=====================================\n"
        #     )
        try:
            GeneratedBugFix = self.BugFixChain.invoke(
                {
                    "description": Description,
                    "code": codeUnderTest,
                    "error_message": errorMessage,
                    "test_case_error": errorTestCases,
                }
            )
        except Exception as e:
            print("ERROR in invoking Feedback Chain")
            print(e)
        newCode, isIncompleteResponse = getCodeFromResponse(GeneratedBugFix["text"], 3)
        if isIncompleteResponse:
            print(
                "Test Case Didn't Run Due to Incomplete Response\n=====================================\n"
            )
        unittestCode = preprocessUnitTest(allTestcases)
        codeTobeRun = getRunningCode(newCode, unittestCode)
        feedback = runCode(codeTobeRun, self.myglobals)
        NonSucceedingCasesNames = getNonSucceedingTestcases(feedback)
        NonSucceedingCasesNamesList = (
            NonSucceedingCasesNames["failed"] + NonSucceedingCasesNames["error"]
        )
        testsToRepeat = getEachTestCase(unittestCode, NonSucceedingCasesNamesList)
        feedbackparsed = getFeedbackFromRun(feedback)
        return newCode, unittestCode, feedbackparsed, testsToRepeat
