"""This module contains utility functions for the main and benchmark module."""
import time
import re
from .coverage.coverageresults import CovergaeResults
from .generationAlg.utils import create_final_test_file

def test_cases_for_branchless_module(test_cases_list, test_cluster,log_file):
    """If the input code has no branches, return random test cases."""
    if not test_cluster.get_contains_conditions():
        log_file.write("No branch exists in the module under test.\n")
        print("No branch exists in the module under test.")
        # Final reporting 
        time_consumed_minutes = (time.time() - test_cluster.get_start_time()) / 60
        log_file.write(f"Time consumed: {time_consumed_minutes:.2f} minutes\n")
        log_file.write(f"Number of offsprings generated:0\n")
        # create object of CoverageResults class
        results_wrapper=CovergaeResults(time_consumed_minutes,0)
        results_wrapper.set_statistics(100,0,0)
        results_wrapper.set_is_branch_exists(0)
        test_file_string,results_wrapper,err_msg=create_final_test_file(test_cases_list,test_cluster,log_file,results_wrapper)
        return test_file_string,results_wrapper, err_msg
    return None, None, None

def getFunctionName(funcDefinition):
    """Get the name of the function from its definition."""
    rs = re.search(r"\"\"\".*\"\"\"", funcDefinition, re.DOTALL)
    if rs == None:
        rs = re.search(r"\'\'\'.*\'\'\'", funcDefinition, re.DOTALL)

    allMatches = re.findall(r"def ", funcDefinition)
    if len(allMatches) == 1:
        end = rs.span()[0]
        funcHeader = funcDefinition[:end]
        UtilityFunction = ""
    else:
        *_, last = re.finditer(r"def ", funcDefinition)
        begin = last.span()[0]
        secondPart = funcDefinition[begin:]
        rs = re.search(r"\"\"\".*\"\"\"", secondPart, re.DOTALL)
        if rs == None:
            rs = re.search(r"\'\'\'.*\'\'\'", secondPart, re.DOTALL)
        end = rs.span()[0]
        funcHeader = funcDefinition[begin : end + begin]
        UtilityFunction = funcDefinition[:begin]
    return funcHeader, UtilityFunction