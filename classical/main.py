import os
from .analysis.analysemodule import analyse_module
from .generationAlg.generation import generate_unit_tests
from .generationAlg.mosa import use_mosa_algorithm
from .generationAlg.coveragetarget import CoverageTarget
from .generationAlg.testcase import TestCase
from .generationAlg.archive import Archive
from .generationAlg.utils import create_final_test_file
from .utils import test_cases_for_branchless_module

def main_function():
    """ Main function that runs the whole process of the algorithm"""
    # project_path="D:/CUFE/grad project/gp2/classical/Unit-Tests-Generation/"
    project_path=os.getcwd()
    # N.B: the module under test (module to be tested), must be in the file inputfunction.py that is under directory "{project_path}/src/"
    module_name="classical.inputfunction" 

    # Create log file file to store info during the run of the algorithm
    log_file=open(f"{project_path}/classical/outputtests/log_file.txt","w")

    # Analyse the source code
    test_cluster,err_msg=analyse_module(module_name,project_path,log_file)

    if err_msg!="":
        return None,None,err_msg

    # Generate the random unit tests
    test_cases_list=generate_unit_tests(test_cluster,log_file)

    # If no test cases are generated, return None
    if test_cases_list==None:
        return None,None,"No test cases are generated."
    
    # If the input code has no branches, return random test cases
    test_cases,results_wrapped,err_msg=test_cases_for_branchless_module(test_cases_list, test_cluster,log_file)
    if test_cases != None:
        return test_cases, results_wrapped, err_msg

    # apply search algorithm MOSA to find the best test case
    test_cases_list_mosa,results_wrapped=use_mosa_algorithm(test_cases_list,test_cluster,log_file)

    if test_cases_list_mosa==None:
        return None,None,"No test cases are generated."

    # Export test cases to file
    test_file_string,results_wrapped,err_msg=create_final_test_file(test_cases_list_mosa,test_cluster,log_file,results_wrapped)

    if err_msg!="":
        return None,None,err_msg

    log_file.close()

    return test_file_string,results_wrapped,err_msg

def main_for_api(code):
    #write the input code of the user to the file inputfunction.py
    path_to_open=os.path.join(os.getcwd(),"classical","inputfunction.py")
    print("-------------------------")
    print(os.getcwd())
    print(path_to_open)
    print("-------------------------")
    with open(path_to_open, "w") as f:
        f.write(code)
    f.close()
    test_file_string,results_wrapped,err_msg=main_function()
    if results_wrapped.branch_coverage_percent==100.0:
        results_wrapped.statement_coverage_percent=100.0
    lst=[results_wrapped.branch_coverage_percent,results_wrapped.statemt_coverage_percent,results_wrapped.time_consumed_min]
    return test_file_string,err_msg,lst

# if __name__ == "__main__":
#     main_function()
