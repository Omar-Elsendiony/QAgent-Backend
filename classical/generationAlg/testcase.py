from .coveragetarget import CoverageTarget
from ..fitness.annotate import get_uncovered_targets_data,objective_score_uncovered_targets,get_excluded_targets_indices,get_targets_string
import sys
class TestCase:
    """class to represent a test case."""
    
    def __init__(self):
        self.lines_count = 0
        self.max_lines=15
        self.fail=False
        self.variables_dict=dict() #example {<class 'int'>: [['int_0', 'int_1'], [77, 88]],<class 'str'>}
        self.generated_var_values=list() #example [['int_0', 77], ['int_1', 88],["func_call","add",[<class 'int'>, <class 'int'>],[int_0,int]]
        self.uncovered_targets=list()
        self.covered_targets=list()
        self.crowding_distance=0
        self.project_path=""
        self.expected_output=None
        self.agg_objective_score=sys.maxsize

    def repair_variables_dict(self):
        #remove duplicates vars of each type if found
        for key in self.variables_dict:
            #know the index of var name so that we can remove the value of the same index
            for var_name in self.variables_dict[key][0]:
                if self.variables_dict[key][0].count(var_name)>1:
                    index=self.variables_dict[key][0].index(var_name)
                    self.variables_dict[key][0].pop(index)
                    self.variables_dict[key][1].pop(index)
    
    def repair_generated_var_values(self):
        #remove lines if found duplicate names (names are in generated_var_values[1])
        for index,line in enumerate(self.generated_var_values):
            for line2 in self.generated_var_values[index+1:-1]:
                if line[1]==line2[1]:
                    self.generated_var_values.pop(index)
                    break

    def get_coverage_targets(self,log_file):
        """get the uncovered targets of the test case and the local variables values just before the uncovered target."""
        #segment the uncovered targets based on the evaluation
        uncovered_dict,missing_branches_indices,covered_branches_indices=get_uncovered_targets_data(self.project_path,log_file)
        if uncovered_dict !=None or missing_branches_indices!=None:
            missing_branches_indices=sorted(missing_branches_indices)
            #excluded_branches_indices=get_excluded_targets_indices(missing_branches_indices,self.project_path)
            index=0
            for target, locals_dict in uncovered_dict.items():
                try:
                    self.segment_uncovered_target_and_calc_scores(target,locals_dict,missing_branches_indices[index],[])
                except Exception as e:
                    print("Error in segmenting the uncovered branch: "+target+" using locals:"+locals_dict+" (calculating objective score)")
                    log_file.write("Error in segmenting the uncovered branch: "+target+" using locals:"+locals_dict+" (calculating objective score)\n")
                    log_file.write(str(e)+"\n")
                index+=1
            self.get_fully_covered_targets(covered_branches_indices)

    def segment_uncovered_target_and_calc_scores(self,target_string,locals_dict:dict,line_number:int,excluded_branches_indices):#excluded to be removed
        """given a uncovered target segment it into true and false targets and calculate the objective score of each target."""
        target_true,target_false=objective_score_uncovered_targets(target_string,locals_dict,line_number,excluded_branches_indices)
        target_true.line_number=line_number
        target_false.line_number=line_number
        #if the true target is covered -> add it to the covered targets list else add it to the uncovered targets list
        if target_true.is_covered:
            self.covered_targets.append(target_true)
        else:
            self.uncovered_targets.append(target_true)
        #if the false target is covered -> add it to the covered targets list else add it to the uncovered targets list
        if target_false.is_covered:
            self.covered_targets.append(target_false)
        else:
            self.uncovered_targets.append(target_false)

    def get_covered_targets_string_with_type():
        """get the covered targets of the test case with the type of the target."""
        covered_targets_tuples=[]
        for target in self.covered_targets:
            covered_targets_tuples.append((target.target_string,target.target_type))
        return covered_targets_tuples
    def is_target_with_type_covered(self,target_string:str,target_type:bool):
        """check if the target is covered."""
        for target in self.covered_targets:
            if target.target_string==target_string and target.target_type==target_type:
                return True
        return False
    def get_objective_score_of_target(self,uncovered_target_tuple):
        """get the objective score of the test case."""
        for target in self.uncovered_targets:
            if target.target_string==uncovered_target_tuple[0] and target.target_type==uncovered_target_tuple[1]:
                return target.branch_distance
        # it is covered
        return 0
    #def get_covered
    def get_fully_covered_targets(self,covered_branches_indices:set):
        """get the fully covered targets of the test case."""
        if len(covered_branches_indices)!=0:
            covered_branches_indices=sorted(covered_branches_indices)
            # covered_branches_indices=get_covered_targets_indices(missing_branches_indices)
            covered_branches_strings=get_targets_string(covered_branches_indices,self.project_path)
            for index,target in enumerate(covered_branches_strings):
                #target object for the true target
                target_true=CoverageTarget()
                target_true.target_string=target
                target_true.line_number=covered_branches_indices[index]
                target_true.is_covered=True
                target_true.branch_distance=0
                target_true.target_type=True
                self.covered_targets.append(target_true)
                #target object for the false target
                target_false=CoverageTarget()
                target_false.target_string=target
                target_false.line_number=covered_branches_indices[index]
                target_false.is_covered=True
                target_false.branch_distance=0
                target_false.target_type=False
                self.covered_targets.append(target_false)
        
