from .generation import convert_testcase_to_string,create_test_file_from_testcase_string,export_test_cases_to_file
from ..coverage.runcoveragepy import run_coveragepy,final_report_html
from .coveragetarget import CoverageTarget
from .testcase import TestCase
from ..coverage.coverageresults import CovergaeResults
from ..fitness.annotate import get_executed_lines_percent

def deal_with_separate_test_cases(test_cases_list,project_path,test_cluster,log_file):
    for index,test_case in enumerate(test_cases_list):
        test_case_str=convert_testcase_to_string(test_case,index,test_cluster,log_file)
        if test_case_str==None:#if the test case is not valid, try another one
            #remove the test case from the list
            test_case.fail=True
            continue
        file_name ="test.py"
        create_test_file_from_testcase_string(project_path,file_name,test_cluster.source_code,test_case_str)
        try:
            run_coveragepy(project_path,file_name)# this function writes coverage.json in coverage folder + .coverage file in the project folder
        except Exception as e:
            print("Error in running coverage.py")
            log_file.write("Error in running coverage.py for the following test case:"+test_case_str+"\n")
            log_file.write(str(e)+"\n")
            test_case.fail=True
            continue
        try:
            # get the coverage targets and calculate the fitness scores
            test_case.get_coverage_targets(log_file)
        except Exception as e:
            print("Error in getting coverage targets")
            log_file.write("Error in getting coverage targets for the following test case:"+test_case_str+"\n")
            log_file.write(str(e)+"\n")
            test_case.fail=True
            continue

def combine_coverage_targets(test_cases_list):#for initialisation of archive
    """combine all the coverage targets of all the test cases into 1 set"""
    all_targets=set()
    for test_case in test_cases_list:
        for target in test_case.covered_targets:
            all_targets.add((target.target_string,target.target_type))
        for target in test_case.uncovered_targets:
            all_targets.add((target.target_string,target.target_type))
    return all_targets

def calculate_statement_coverage(project_path):
    """Calculate the statement coverage from the coverage.json file."""
    try:
        statement_coverage_percent=get_executed_lines_percent(project_path)
        return statement_coverage_percent
    except Exception as e:
        print("Error in calculating statement coverage.")
        print(str(e))
        log_file.write("Error in calculating statement coverage.\n")
        log_file.write(str(e)+"\n")
        return None

def create_final_test_file(test_cases_list,test_cluster,log_file,results_wrapped:CovergaeResults):
    file_name ="test.py"
    # if there is no branch in the module under test, return a test case from random test cases
    # if not results_wrapped.get_is_branch_exists():
    #     print("No branch exists in the module under test.")
    #     log_file.write("No branch exists in the module under test.\n")
    #     return "No branch exists in the module under test.\n",""
    test_file_string=export_test_cases_to_file(file_name,test_cases_list,test_cluster,log_file)
    #final report
    try:
        run_coveragepy(test_cluster.project_path,file_name)
        results_wrapped.set_statement_coverage(calculate_statement_coverage(test_cluster.project_path))
        results_wrapped.set_actual_targets_count(test_cluster.get_actual_targets_count())
        final_report_html(test_cluster.project_path,file_name)
        print("Final test file has been created.")
        log_file.write("Final test file -test.py- has been created.\n")
        return test_file_string,results_wrapped,""
    except Exception as e:
        print("Error in running coverage.py for the final test file.")
        log_file.write("Error in running coverage.py for the final test file.\n")
        log_file.write(str(e)+"\n")
        return None,None,"Error in running coverage.py for the final test file.\n"
    
