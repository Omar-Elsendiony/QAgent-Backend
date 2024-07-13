from Imports import *
from utils.CustomThread import *


class DecisionMaker:

    def __init__(self, JudgeChain, myglobals):
        self.JudgeChain = JudgeChain
        # self.db = db
        self.myglobals = myglobals



    def generate(self, code, description, errorTestCases):
        """
        This function is responsible for generating the test cases and running them
        It is the core of the DecisionMaker class. It is responsible for:
        1. Extracting the code and description from the example
        2. Generating the test cases
        3. Running the test cases
        4. Storing the results in a JSON file
        Args: None
        Return: None
        """
        try:
            errorMsg = getOneError(errorTestCases)
            generatedJudgement = self.JudgeChain.invoke(
                {
                    "code": code,
                    "description": description,
                    # "test_cases_of_few_shot": fewShotStr,
                    "test_case_error": errorTestCases,
                    "error_message": errorMsg,
                }
            )  # ,"test_cases_of_few_shot":fewShotStr
        except Exception as e:
            print("ERROR in invoking Judge Chain")
            print(e)
            return
        

        judgementCodeBuggy,judgementTestBuggy, explanation, isIncompleteResponse = getJudgmentFromGeneration(
                generatedJudgement["text"]
            )

        return judgementCodeBuggy, judgementTestBuggy, explanation, isIncompleteResponse



    def extractFewShots(self, code):
        """
        Extract the few shot code and test cases from the database
        Args: code (str): The code of the example
        Return: fewShotStr (str): The few shot code and test cases
        """
        # get the few shot code and test cases
        codeOfFewShots, testCasesFewShots = getFewShots(self.db, code)
        # take the most similar few shot other than the code itself
        codeOfFewShots = codeOfFewShots[1:4]
        testCasesFewShots = testCasesFewShots[1:4]
        fewShotStr = preprocessStringFewShot(codeOfFewShots, testCasesFewShots)
        return fewShotStr



    def extractExampleInfo(self, example):
        # Extract the code and description from the example
        code = example["code"]
        description = example["description"]
        return code, description

    def runTest(self, code, unittestCode):
        """
        Run the test case after some preprocessing of the returned response
        """
        unittestCode = preprocessUnitTest(unittestCode)
        codeTobeRun = getRunningCode(code, unittestCode)
        feedback = runCode(codeTobeRun, self.myglobals)
        feedbackparsed = getFeedbackFromRun(feedback)
        return feedback, feedbackparsed, codeTobeRun

    