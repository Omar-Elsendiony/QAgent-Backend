from utils import *
import pandas as pd
import os
import json
import sys
from multiprocessing import freeze_support

from main import main_function

class UnitTestsGenerator:

    def __init__(self, data_JsonObj, myglobals):
        self.data_JsonObj = (
            data_JsonObj  # data json object , previously humanEval_JsonObj
        )
        self.myglobals = myglobals
        self.failedExamplesNum = 0
        self.totalCoveredTargetsNum=0
        self.totalCoverageTargetsNum=0
        self.successfulExamplesNum = 0
        self.OutputFolder = "./src/benchmark/experiments/"
        self.JSONFile = self.OutputFolder + "RunningLogs.json"
        self.CasesJSONFile = self.OutputFolder + "Cases.json"
        self.logsDf = pd.DataFrame()
        self.casesDf = pd.DataFrame()

    def generate(self):
        """
        This function is responsible for generating the test cases and running them
        It is the core of the UnitTestsGenerator class. It is responsible for:
        1. Extracting the code and description from the example
        2. Generating the test cases
        3. Running the test cases
        4. Storing the results in a JSON file
        Args: None
        Return: None
        """
        self.checkPaths()
        FileHandle = open(self.OutputFolder + "Cases.txt", "w+")
        for i in range(94,153):
            # if (i == 10): continue
            print("Running Test Case ", i)
            FileHandle.write(
                "Running Test Case "
                + str(i)
                + "\n=====================================\n"
            )
            # description and code from database
            code = self.extractInfo(i)
            #write the code to inputfunction.py under src/ folder
            with open(f"{os.getcwd()}/src/inputfunction.py", "w") as f:
                f.write(code)
            f.close()
            try:
                unit_tests_Code,results_wrapped,error=main_function()
            except Exception as e:
                print("ERROR in running")
                print(e)
                FileHandle.write(
                    "Test Case "
                    + str(i)
                    + " Didn't Run Due to Errorr\n=====================================\n"
                )
                newRow = pd.DataFrame(
                    {
                        "CaseNumber": i,
                        "Code": code,
                        "Error": 1,
                        "GeneratedTestFile": "Error: No tests generated "+str(e),
                        "BranchExists":0,
                        "BranchCoveragePercentage": 0,
                        "CountCoveredTargets": 0,
                        "CountAllTargets": 0,
                        "TimeConsumed": 0,
                        "CountOffspringGenerated": 0,
                        "TargetsTestCasePairs": "{}",
                    },
                    index=[0],
                )
                # df = df.append(newRow, ignore_index=True)
                self.logsDf = pd.concat([self.logsDf, newRow])
                # Save the updated DataFrame back to the excel file using 'openpyxl' engine for writing
                jsondata = self.logsDf.to_dict(orient="records")
                with open(self.JSONFile, "w") as f:
                    json.dump(jsondata, f, indent=4)
                error = str(e)
                unit_tests_Code = None
                results_wrapped=None
                self.writeResults(
                    unit_tests_Code,
                    error,
                    results_wrapped,
                    FileHandle,
                    i,
                )
                continue
            if unit_tests_Code == None:
                print("ERROR in running MOSA")
                print(error)
                FileHandle.write(
                    "Test Case "
                    + str(i)
                    + " Didn't Run Due to Errorr\n=====================================\n"
                )
                newRow = pd.DataFrame(
                    {
                        "CaseNumber": i,
                        "Code": code,
                        "Error": 1,
                        "GeneratedTestFile": "Error: "+str(error),
                        "BranchExists":0,
                        "BranchCoveragePercentage": 0,
                        "CountCoveredTargets": 0,
                        "CountAllTargets": 0,
                        "TimeConsumed": 0,
                        "CountOffspringGenerated": 0,
                        "TargetsTestCasePairs": "{}",
                    },
                    index=[0],
                )
                # df = df.append(newRow, ignore_index=True)
                self.logsDf = pd.concat([self.logsDf, newRow])
                # Save the updated DataFrame back to the excel file using 'openpyxl' engine for writing
                jsondata = self.logsDf.to_dict(orient="records")
                with open(self.JSONFile, "w") as f:
                    json.dump(jsondata, f, indent=4)
                self.writeResults(
                    unit_tests_Code,
                    error,
                    results_wrapped,
                    FileHandle,
                    i,
                )
                continue
            # NonSucceedingCasesNames = getNonSucceedingTestcases(feedback)
            NonSucceedingCasesNamesList=None
            # NonSucceedingCasesNamesList = (
            #     NonSucceedingCasesNames["failed"] + NonSucceedingCasesNames["error"]
            # )
            self.writeResults(
                unit_tests_Code,
                error,
                results_wrapped,
                FileHandle,
                i,
            )
            newRow = pd.DataFrame(
                {
                    "CaseNumber": i,
                    "Code": code,
                    "Error": 0,
                    "GeneratedTestFile": unit_tests_Code,
                    "BranchExists":results_wrapped.get_is_branch_exists(),
                    "BranchCoveragePercentage":results_wrapped.branch_coverage_percent,
                    "CountCoveredTargets":results_wrapped.count_covered_targets,
                    "CountAllTargets":results_wrapped.all_targets_count,
                    "TimeConsumed":results_wrapped.time_consumed_min,
                    "CountOffspringGenerated":results_wrapped.count_offspring_generated,
                    "TargetsTestCasePairs": json.dumps(results_wrapped.targets_best_solutions_dict),
                },
                index=[0],
            )
            self.logsDf = pd.concat([self.logsDf, newRow])
            # Save the updated DataFrame back to the excel file using 'openpyxl' engine for writing
            jsondata = self.logsDf.to_dict(orient="records")
            with open(self.JSONFile, "w") as f:
                json.dump(jsondata, f, indent=4)
        FileHandle.close()

        self.printResults()
        return

    def extractInfo(self, i):
        """
        Extract the description and code from the example in addition to prepending the function header
        Args: i (int): The index of the example in the JSON file
        Return: description (str): The description of the example
                code (str): The code of the example
        """
        # description = self.data_JsonObj.iloc[i]["text"]
        code = self.data_JsonObj.iloc[i]["canonical_solution"]
        # remove initial spaces in extracted code
        code = code.strip()
        # extract the function definition and utility code
        funcDefiniton = self.data_JsonObj.iloc[i]["prompt"]
        funcDefiniton, Utility = getFunctionName( 
            funcDefiniton
        )  # does not need entry point at the end of the day
        code = Utility + "\n" + funcDefiniton + code
        return code

    def checkPaths(self):
        """
        Check if these directories and files exist, if not create them
        Args: None
        Return: None
        """
        if not os.path.exists(self.OutputFolder):
            try:
                os.makedirs(self.OutputFolder)
                print(f"Directory {self.OutputFolder} created successfully!")
            except Exception as e:
                print(f"Error creating directory {self.OutputFolder}: {e}")
                exit()

        if not os.path.exists(self.CasesJSONFile):
            try:
                # Create a new empty JSON file with an empty list structure
                with open(self.CasesJSONFile, "w") as f:
                    json.dump([], f)
                    print(f"File {self.CasesJSONFile} created successfully!")
            except Exception as e:
                print(f"Error creating file {self.CasesJSONFile}: {e}")
                exit()

        if not os.path.exists(self.JSONFile):
            try:
                # Create a new empty JSON file with an empty list structure
                with open(self.JSONFile, "w") as f:
                    json.dump([], f)
                    print(f"File {self.JSONFile} created successfully!")
            except Exception as e:
                print(f"Error creating file {self.JSONFile}: {e}")
                exit()

    def writeResults(
        self,
        unit_tests_Code,
        error_msg,
        results_wrapped,
        FileHandle,
        i,
    ):
        """
        Responsible for writing results to cases.txt and cases.json

        Args: feedbackparsed (str): The parsed feedback from the test case


        """
        # IF Succeded EXAMPLE
        if error_msg == "" and unit_tests_Code != None:
            # in case of OK
            self.successfulExamplesNum += 1
            print(
                f"Test example {i} succeeded\n======================================\n"
            )
            FileHandle.write("Test example " + str(i) + " succeeded\n")
            newCaseRow = pd.DataFrame(
                {
                    "CaseNumber": i,
                },
                index=[0],
            )
            self.casesDf = pd.concat([self.casesDf, newCaseRow])
            casejsondata = self.casesDf.to_dict(orient="records")
            with open(self.CasesJSONFile, "w") as f:
                json.dump(casejsondata, f, indent=4)
            self.totalCoverageTargetsNum += results_wrapped.all_targets_count
            self.totalCoveredTargetsNum += results_wrapped.count_covered_targets

        else:
            self.failedExamplesNum += 1
            print(f"Test example {i} failed\n======================================\n")
            FileHandle.write("Test example " + str(i) + " failed\n")
            newCaseRow = pd.DataFrame(
                {
                    "CaseNumber": i,
                },
                index=[0],
            )
            self.casesDf = pd.concat([self.casesDf, newCaseRow])
            casejsondata = self.casesDf.to_dict(orient="records")
            with open(self.CasesJSONFile, "w") as f:
                json.dump(casejsondata, f, indent=4)
        #write the contet of the log_file.txt in the file Cases.text (FileHandle)
        #read the content of the log_file.txt
        #get working directory
        # cwd = os.getcwd()
        with open("D:/CUFE/grad project/gp2/classical/Unit-Tests-Generation/src/outputtests/log_file.txt", "r") as f:
            content = f.read()
            FileHandle.write(content)
        f.close()

    def printResults(self):
        """
        Prints the remaining results and create Res.txt which includes a summary of the overall run

        """
        print("\n End of Test Cases \n")
        print("Total succeeded examples : ", self.successfulExamplesNum)
        print("Total targets : ", self.totalCoverageTargetsNum)
        print(
            "Total Covered targets : ",
            self.totalCoveredTargetsNum
        )
        print("Total failed examples : ", self.failedExamplesNum)
        with open(self.OutputFolder + "Res.txt", "w") as f:
            f.write(
                "Total succeeded examples : " + str(self.successfulExamplesNum) + "\n"
            )
            f.write("Total targets : " + str(self.totalCoverageTargetsNum) + "\n")
            f.write(
                "Total Covered targets : "
                + str(
                    self.totalCoveredTargetsNum
                )
                + "\n"
            )
            f.write("Total failed examples : " + str(self.failedExamplesNum) + "\n")

def benchmark_main():
    #test
    #read json file
    # json_file = open("D:/CUFE/grad project/gp2/classical/Unit-Tests-Generation/src/datasets/coverage-eval/0.json")
    HEval_JsonObj = pd.read_json(path_or_buf=f"{os.getcwd()}/src/datasets/humaneval.jsonl",lines=True)#notypehints
    generator_inst=UnitTestsGenerator(HEval_JsonObj,globals())
    #open a txt file
    # txt_file = open(f"{os.getcwd()}/src/benchmark/experiments/examples100.txt", "w")
    # for i in range(0,100):
    #     txt_file.write(f"\n\nExtracting example {i}")
    #     txt_file.write(generator_inst.extractInfo(i))
    #call generate
    generator_inst.generate()

if __name__ == '__main__':
    benchmark_main()