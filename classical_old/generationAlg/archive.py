""" A representation to store the best solution found so far and the global coverge targets"""
from ..coverage.runcoveragepy import run_coveragepy
from .coveragetarget import CoverageTarget
from .utils import combine_coverage_targets
from .generation import convert_testcase_to_string
from ..coverage.coverageresults import CovergaeResults
class Archive:
    """Class to represent the archive."""
    def __init__(self,test_cases_list:list):
        """initialize the archive with the global coverage targets."""
        self.global_coverage_targets=combine_coverage_targets(test_cases_list)
        self.global_covered_targets= []
        self.global_uncovered_targets = []
        self.archive_uncovered_targets = []
        self.archive_best_solutions= {}
        #fill the archive with the global coverage targets and None as the best solution
        for target_tuple in self.global_coverage_targets:
            self.archive_best_solutions[target_tuple]=None
        
    
    def update_archive_targets(self,test_case_list:list):
        #get the current coverage targets (covered or uncovered of the new test cases population)
        current_coverage_targets=combine_coverage_targets(test_case_list)
        #get the new targets that are not in the archive
        for target in current_coverage_targets:
            if target not in self.archive_best_solutions:
                self.archive_best_solutions[target]=None

    def update_archive(self,test_case_list:list):
        """update the archive with the new test cases."""  
        #get the updated targets given the new test cases
        self.update_archive_targets(test_case_list)  
        for target,sol in self.archive_best_solutions.items():
            tbest=None
            best_length=float('inf')
            if sol:
                tbest=sol
                best_length=sol.lines_count
            for tj in test_case_list:
                if tj.is_target_with_type_covered(target[0],target[1]):
                    length=tj.lines_count
                    if length<=best_length:
                        self.archive_best_solutions[target]=tj
                        tbest=tj
                        best_length=length
    def get_archive_uncovered_targets(self):
        """get the uncovered targets of the archive."""
        self.archive_uncovered_targets = []
        for target,sol in self.archive_best_solutions.items():
            if not sol:
                self.archive_uncovered_targets.append(target)
        return self.archive_uncovered_targets

    def get_best_solutions(self):
        """get the best solutions of the archive."""
        #get the set of solutions (test cases) that are the best for each target 
        best_solutions=set()
        for target,sol in self.archive_best_solutions.items():
            if sol:
                best_solutions.add(sol)
        return best_solutions

    def is_all_covered(self):
        """check if all the targets are covered."""
        for target,sol in self.archive_best_solutions.items():
            if not sol:
                return False
        return True

    def calc_coverage_statistics(self,log_file,results_wrapper:CovergaeResults):
        """calculate the coverage statistics of the archive."""
        covered=0
        for target,sol in self.archive_best_solutions.items():
            if sol:
                covered+=1
        if len(self.archive_best_solutions)>0:
            results_wrapper.set_is_branch_exists(1)
            branch_cov_percent=covered/len(self.archive_best_solutions)*100
            results_wrapper.set_statistics(branch_cov_percent,covered,len(self.archive_best_solutions))
            log_file.write(f"Branch Coverage: {branch_cov_percent}%\n")
            log_file.write(f"Number of targets covered: {covered}/{len(self.archive_best_solutions)}\n")
        else:
            targets_count=test_cluster.get_actual_targets_count()
            results_wrapper.set_statistics(0.0,0,targets_count)
            results_wrapper.set_is_branch_exists(1)
            log_file.write(f"Branch Coverage: 0.0%\n")
            log_file.write(f"Number of targets covered: {0}/{targets_count}\n")
            
    def write_archive_report(self,results_wrapper:CovergaeResults):
        """write the archive report, containing the best solution (test case) for each target."""
        archive_report=open("./classical/outputtests/archive_report.txt","w")
        for target,sol in self.archive_best_solutions.items():
            archive_report.write(f"Target: {target[0]} {target[1]}:\n")
            if sol:
                test_case_str=convert_testcase_to_string(sol,'','','')
                archive_report.write(f"    Best solution: {test_case_str}\n")
                results_wrapper.add_target_sol_pair(target,test_case_str)
            else:
                archive_report.write("    No solution\n")
                results_wrapper.add_target_sol_pair(target,"No solution")
        archive_report.close()
        