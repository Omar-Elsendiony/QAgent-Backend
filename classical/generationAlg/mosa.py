#Test case generation algorithm: MOSA
import random
import copy
import time
from typing import List,Dict,Tuple,Set,Any
from .testcase import TestCase
from ..analysis.analysemodule import TestCluster
from .archive import Archive
from .utils import deal_with_separate_test_cases
from .generation import generate_int_value,generate_str_value,generate_random_test_case
from .geneticoperators import edit_list,edit_string
from ..coverage.coverageresults import CovergaeResults

class MOSA:
    """A class to represent the MOSA algorithm for test case generation."""
    def __init__(self,test_cluster):
        #self.testcluster to be added when the test cluster class is implemented
        self.stopping_criterion = 0 #0 for complete coverage, 1 for number of test cases
        self.time_limit = 60
        self.population=[]
        self.population_size=10
        self.count_offspring_generated=0
        self.uncovered_targets=[]
        self.test_cluster=test_cluster
        self.fronts_list=[]
        self.reuse_variable_probability=0.5
        self.add_subtract_change_probability=0.5
        self.power_of_quantity_of_change=1
    
    def add_statement(self, test_case, line_number):
        """Adds a statement to the given test case."""
        # the statement to be inserted is a variable initialization
        # generate a type that is already in the test case by checking the variables_dict
        get_types_in_test_case=test_case.variables_dict.keys()
        #choose a random type from this list
        rand_type=random.choice(list(get_types_in_test_case))
        # check if the count of each paramter type of the function sig. is sufficient, so no need for insert mutation
        # we may keep vars of the same type that counts double the required type in the function signature
        if len(test_case.variables_dict[rand_type][0])> 2* self.test_cluster.params_occurence_dict[rand_type]:
            #go to the edit or remove mutation
            if random.random()<0.5:
                return self.edit_statement(test_case,line_number)
            else:
                return self.remove_statement(test_case,line_number)
        # generate a new variable of the type
        var_statement=self.generate_var_with_type(rand_type,test_case)
        # add the statement to the list of generated variables
        test_case.generated_var_values.insert(line_number,var_statement)
        test_case.lines_count+=1
        # increment the count of the type
        #test_case.inc_count_vars_of_type(rand_type)
        return test_case
    
    def remove_statement(self, test_case, line_number):
        """Removes a statement from the given test case."""
        # remove the statement from the list of generated variables
        removed_statement=test_case.generated_var_values.pop(line_number)
        # if the statement is a variable initialization, remove the variable from the dict
        if removed_statement[0] in test_case.variables_dict:
            var_index=test_case.variables_dict[removed_statement[0]][0].index(removed_statement[1])
            test_case.variables_dict[removed_statement[0]][0].pop(var_index)
            test_case.variables_dict[removed_statement[0]][1].pop(var_index)
            #decrement the count of the type
            #test_case.dec_count_vars_of_type(removed_statement[0])
            #repair the dependencies
            test_case=self.repair_test_case(test_case)
        return test_case
    
    def edit_statement(self, test_case, line_number):
        """Edits a statement in the given test case."""
        # get the min and max values for the type
        min_rand_val,max_rand_val=self.test_cluster.get_min_max_rand_values() 
        #edit value of the variable at line_number
        #if the type is int, change the value
        quantity_of_change=random.randint(min_rand_val, max_rand_val)
        var_type=test_case.generated_var_values[line_number][0]
        var_value=test_case.generated_var_values[line_number][2]
        var_index=test_case.variables_dict[var_type][0].index(test_case.generated_var_values[line_number][1])
        if var_type==int:
            if self.add_subtract_change_probability>random.random():
                var_value+=int(quantity_of_change*random.random()**self.power_of_quantity_of_change)
            else:
                var_value-=int(quantity_of_change*random.random()**self.power_of_quantity_of_change)
        elif var_type==bool:
            var_value=not var_value
        elif var_type==float:
            if self.add_subtract_change_probability>random.random():
                var_value+=quantity_of_change*random.random()**self.power_of_quantity_of_change
            else:
                var_value-=quantity_of_change*random.random()**self.power_of_quantity_of_change
        elif var_type==str:
            var_value=edit_string(var_value)
        elif var_type==list[int] or var_type==List[int]:
            var_value=edit_list(var_type,var_value, min_rand_val,max_rand_val,self.power_of_quantity_of_change)
        elif var_type==list[str] or var_type==List[str]:
            var_value=edit_list(var_type,var_value, min_rand_val, max_rand_val,self.power_of_quantity_of_change)
        #make the same change in the variables dict #TODO
        test_case.variables_dict[var_type][1][var_index]=var_value
        return test_case

    def mutate(self, test_case):
        """Mutates the given test case."""
        # choose a random line to mutate
        rand_line_number=random.randint(0,test_case.lines_count-1)
        if test_case.generated_var_values[rand_line_number][0]=="func_call":
            rand_line_number-=1
        # choose a random mutation type
        mutation_type=random.choice(["insert","remove","edit"])
        if mutation_type=="insert":
            # add a new statement
            test_case=self.add_statement(test_case,rand_line_number)
        elif mutation_type=="remove":
            # remove a statement
            test_case=self.remove_statement(test_case,rand_line_number)
        elif mutation_type=="edit":
            # edit a statement
            test_case=self.edit_statement(test_case,rand_line_number)
        return test_case
    
    def generate_var_with_type(self,typ,test_case):
        """Generates a variable with the given type and adds it to the dictionary of the test case.
        Returns the statement of the varaible and the variable initialization"""
        #check if the type is already in the dict
        if typ not in test_case.variables_dict:
            # if the type is not in the dict, add it, create new list
            test_case.variables_dict[typ]=[[],[]]
        #get the min and max values for the type
        min_rand_val,max_rand_val=self.test_cluster.get_min_max_rand_values()
        rand_value=None
        var_index=len(test_case.variables_dict[typ][0])
        try:
            var_name=typ.__name__+"_"+str(var_index)
        except Exception as e:
            print("Error in generating variable of type: "+str(typ)+"\n")
            print(e)
            test_case.fail=True
            exit()
        if typ==int:
            rand_value=random.randint(min_rand_val, max_rand_val)
        elif typ==str:
            rand_value=generate_str_value()
        elif typ==float:
            rand_value=random.uniform(min_rand_val, max_rand_val)
        elif typ==bool:
            rand_value=random.choice([True, False])
        elif typ==list[int] or typ==List[int]:
            rand_value=[generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))]
            var_name=typ.__name__+"_int_"+str(var_index)
        elif typ==list or typ==List:
            #generate random list of integers or random list of strings
            if random.choice([0,1])==0:
                #generate random list of integers
                rand_value=[ generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))]
            else:
                rand_value=[ generate_str_value() for i in range(0,random.randint(0, 6))]
        elif typ==list[str] or typ==List[str]:
            #generate random list of strings
            rand_value=[ generate_str_value() for i in range(0,random.randint(0, 6))]
            var_name=typ.__name__+"_str_"+str(var_index)
        elif typ==list[float] or typ==List[float]:
            #generate random list of floats
            rand_value=[ random.uniform(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))]
            var_name=typ.__name__+"_float_"+str(var_index)
        elif typ==list[bool] or typ==List[bool]:
            #generate random list of booleans
            rand_value=[ random.choice([True, False]) for i in range(0,random.randint(0, 6))]
            var_name=typ.__name__+"_bool_"+str(var_index)
        elif typ==dict[str,int] or typ==Dict[str,int]:
            #generate random dict
            rand_value={ generate_str_value(): generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            var_name=typ.__name__+"_str_int_"+str(var_index)
        elif typ==dict[str,str] or typ==Dict[str,str]:
            #generate random dict
            rand_value={ generate_str_value(): generate_str_value() for i in range(0,random.randint(0, 6))}
            var_name=typ.__name__+"_str_str_"+str(var_index)
        elif typ==dict[int,int] or typ==Dict[int,int]:
            #generate random dict
            rand_value={ generate_int_value(min_rand_val, max_rand_val): generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            var_name=typ.__name__+"_int_int_"+str(var_index)
        elif typ==dict[int,str] or typ==Dict[int,str]:
            #generate random dict
            rand_value={ generate_int_value(min_rand_val, max_rand_val): generate_str_value() for i in range(0,random.randint(0, 6))}
            var_name=typ.__name__+"_int_str_"+str(var_index)
        elif typ==dict or typ==Dict:
            #generate random dict of integers or random dict of strings
            if random.choice([0,1])==0:
                #generate random dict of integers
                rand_value={ generate_int_value(min_rand_val, max_rand_val): generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            else:
                rand_value={ generate_str_value(): generate_str_value() for i in range(0,random.randint(0, 6))}
        elif typ==set[int] or typ==Set[int]:
            #generate random set
            rand_value={ generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            var_name=typ.__name__+"_int_"+str(var_index)
        elif typ==set[str] or typ==Set[str]:
            #generate random set
            rand_value={ generate_str_value() for i in range(0,random.randint(0, 6))}
            var_name=typ.__name__+"_str_"+str(var_index)
        elif typ==tuple[int,int] or typ==Tuple[int,int]:
            #generate random tuple
            rand_value=( generate_int_value(min_rand_val, max_rand_val), generate_int_value(min_rand_val, max_rand_val))
            var_name=typ.__name__+"_tuple_"+str(var_index)
        else:
            print("Type not supported"+str(typ)+"\n")
            test_case.fail=True
        # add the variable to the dict
        if var_name not in test_case.variables_dict[typ][0]:
            # if the variable name is not in the list of names of the type, add it
            test_case.variables_dict[typ][0].append(var_name)
            test_case.variables_dict[typ][1].append(rand_value)
        else:
            # if the variable name is already used, generate a new name
            while var_name in test_case.variables_dict[typ][0]:
                var_index+=1
                var_name=typ.__name__+"_"+str(var_index)
                if typ==list[int] or typ==List[int]:
                    var_name=typ.__name__+"_int_"+str(var_index)
            test_case.variables_dict[typ][0].append(var_name)
            test_case.variables_dict[typ][1].append(rand_value)
        return [typ,var_name,rand_value]

    def repair_test_case(self, test_case):
        """Repairs dependencies of the given test case. Either by reusing existing instances or by adding new ones."""
        # remember function call statement is like ['func_call', function_Name, list_of_types_of_parameters,list_of_names_of_parameters]
        # example  ['func_call', 'triangle', [<class 'int'>,<class 'int'>,<class 'int'>],[int_0,int_1,int_2]] 
        for line_index,line in enumerate(test_case.generated_var_values):
            if line[0]=="func_call":
                for param_index,param_type in enumerate(line[2]):
                    if param_type not in test_case.variables_dict:
                        # if the type is not in the dict, add it, create new list
                        test_case.variables_dict[param_type]=[[],[]] 
                        # generate a new variable of the type
                        var_statement=self.generate_var_with_type(param_type,test_case)
                        #add the var_statement to the list of generated variables before the function call
                        test_case.generated_var_values.insert(line_index,var_statement)
                        #edit the function call statement to include the new variable name
                        line[3][param_index]=var_statement[1]
                    else:
                        if len(test_case.variables_dict[param_type][0])>0: # variables_dict[param_type][0], the [0] indexing means the list of names of the type
                            # if the paramter name exist in the dictionary of the test cases
                            # No dependency problem
                            # so we dont need to do anything
                            if line[3][param_index] in test_case.variables_dict[param_type][0]:
                                continue
                            # here we have a dependency problem that must be solved either by reusing or generating
                            # if there exist value(s) in the list of values of the type
                            if random.random()<self.reuse_variable_probability:
                                # if the reuse probability is greater than a random number, reuse the value
                                # reuse random var from the list
                                #edit the function call statement to include the variable name
                                line[3][param_index]=random.choice(test_case.variables_dict[param_type][0])
                            else:
                                # if the reuse probability is less than a random number, generate a new value
                                # generate a new variable of the type
                                var_statement=self.generate_var_with_type(param_type,test_case)
                                #add the var_statement to the list of generated variables before the function call
                                test_case.generated_var_values.insert(line_index,var_statement)
                                #edit the function call statement to include the new variable name
                                line[3][param_index]=var_statement[1]
                        else:
                            #the list of vars of the type is empty, generate a new variable of the type
                            var_statement=self.generate_var_with_type(param_type,test_case)
                            #add the var_statement to the list of generated variables before the function call
                            test_case.generated_var_values.insert(line_index,var_statement)
                            #edit the function call statement to include the new variable name
                            line[3][param_index]=var_statement[1]
                    #repair the counts of the types
                    #test_case.repair_counts_of_types()
        #repair test case lines count
        test_case.lines_count=len(test_case.generated_var_values)
        return test_case
    
    def construct_test_case_from_statemnts(self, test_case1_lines):
        """Creates a new instance of TestCase from the given test case statements"""
        test_case=TestCase()
        test_case.project_path=self.test_cluster.project_path
        test_case.generated_var_values=test_case1_lines
        test_case.repair_generated_var_values()
        test_case.lines_count=len(test_case1_lines)
        for line in test_case1_lines:
            if line[0]=="func_call":
                continue
            if line[0] not in test_case.variables_dict:#line[0] is the type of the variable
                test_case.variables_dict[line[0]]=[[],[]]
            # add the value to the list of values of the type
            test_case.variables_dict[line[0]][0].append(line[1])
            test_case.variables_dict[line[0]][1].append(line[2])
        return test_case

    def crossover(self, test_case1:TestCase, test_case2:TestCase):
        """Performs crossover between two test cases."""
        # choose a random line number to split the test cases
        rand_cross_over_point=random.randint(1,test_case1.lines_count-1)
        rand_cross_over_point2=random.randint(1,test_case2.lines_count-1)
        # split each test case lines randomly into 2 parts
        test_case1_lines_part1=test_case1.generated_var_values[:rand_cross_over_point]
        test_case1_lines_part2=test_case1.generated_var_values[rand_cross_over_point:]
        test_case2_lines_part1=test_case2.generated_var_values[:rand_cross_over_point2]
        test_case2_lines_part2=test_case2.generated_var_values[rand_cross_over_point2:]
        #join the parts of the test cases
        new_test_case_lines1=test_case1_lines_part1+test_case2_lines_part2
        new_test_case_lines2=test_case2_lines_part1+test_case1_lines_part2
        test_case_cross_over_1=self.construct_test_case_from_statemnts(new_test_case_lines1)
        test_case_cross_over_2=self.construct_test_case_from_statemnts(new_test_case_lines2)
        #repair the test cases (the dependencies)
        test_case_cross_over_1=self.repair_test_case(test_case_cross_over_1)
        test_case_cross_over_2=self.repair_test_case(test_case_cross_over_2)
        #repair the test cases var dictionaries
        test_case_cross_over_1.repair_variables_dict(),test_case_cross_over_2.repair_variables_dict()
        return [test_case_cross_over_1,test_case_cross_over_2]

    def select(self):
        """Selects the best test cases from the population."""
        #choose the best 2 test cases from the population
        parent1=copy.deepcopy(random.choice(self.population))
        parent2=copy.deepcopy(random.choice(self.population))
        return parent1,parent2

    def generate_offspring(self):
        """Generates offspring from the given population."""
        new_population=[]
        for i in range(0,int(self.population_size/2)):
            parent1,parent2=self.select()
            test_cases_list_mosa=self.crossover(parent1,parent2)
            new_population.append(self.mutate(test_cases_list_mosa[0]))
            new_population.append(self.mutate(test_cases_list_mosa[1]))
        self.count_offspring_generated+=1
        # self.population_size+=2
        return new_population

    def assign_crowding_distance(self, front):
        """Assigns the crowding distance to the test cases in the front."""
        front = list(front) # Convert the set to a list
        size = len(front)
        if size == 0:
            return
        elif size == 1:
            front[0].crowding_distance = float('inf')
        else:
            for testcase in front:
                testcase.crowding_distance = 0
                if len(testcase.uncovered_targets)>0:
                    testcase.agg_objective_score = sum(target.branch_distance for target in testcase.uncovered_targets)  # Sum of objective scores
            front.sort(key=lambda x: x.agg_objective_score)  # Sort test cases based on objective score
            front[0].crowding_distance = front[-1].crowding_distance = float('inf')
            for i in range(1, size - 1):
                front[i].crowding_distance = (front[i + 1].agg_objective_score - front[i - 1].agg_objective_score)
            

    def sort_front_using_crowding_distance(self, front):
        """Sorts the front using the crowding distance."""
        front = list(front) # Convert the set to a list
        front.sort(key=lambda x: x.crowding_distance, reverse=True)
        return front
    def dominance_comparator(self,t1, t2):
        """Compares two test cases based on the dominance relation."""
        dominates1 = False
        dominates2 = False
        
        for ui in self.uncovered_targets:
            f1i = t1.get_objective_score_of_target(ui) # Performance of t1 on target ui
            f2i = t2.get_objective_score_of_target(ui)  # Performance of t2 on target ui
            
            if f1i < f2i:
                dominates1 = True
            elif f2i < f1i:
                dominates2 = True
            
            if dominates1 and dominates2:
                break
        
        if dominates1 == dominates2:
            return None  # Neither dominates
        elif dominates1:
            return "t1"  # t1 dominates t2
        else:
            return "t2"  # t2 dominates t1

    def fast_non_dominated_sort(self, test_cases):
        """Sorts the test cases using the fast non-dominated sort algorithm."""
        test_cases_set= set(test_cases)
        fronts = []
        dominated_count = {t: 0 for t in test_cases_set} #dict count (value) of test cases that dominate t (key)
        dominated_by = {t: [] for t in test_cases_set}#dict,  key: t, value: list of test cases that t dominates
        # loop through all pairs of test cases
        # and determine the dominance result between them using the dominance_comparator function
        for i, t1 in enumerate(test_cases_set):
            for j, t2 in enumerate(test_cases_set):
                if i == j:
                    continue
                
                result = self.dominance_comparator(t1, t2)
                if result is not None:#means that one dominates the other
                    if result == "t1":
                        dominated_count[t2] += 1
                        dominated_by[t1].append(t2)
        # determine the first front
        # the first front is the set of test cases that are not dominated by any other test case
        current_front = [t for t in test_cases_set if dominated_count[t] == 0]
        if current_front:
            fronts.append(set(current_front))
        # loop through the fronts and determine the next fronts
        while current_front:
            next_front = []
            for t1 in current_front:
                for t2 in dominated_by[t1]:
                    dominated_count[t2] -= 1
                    # if the test case is not dominated by any other test case, add it to the next front t2 is by only tests in previous front
                    if dominated_count[t2] == 0:
                        next_front.append(t2)
            current_front = next_front
            if current_front:
                fronts.append(set(current_front))
        return fronts

    def preference_sorting(self, test_cases):
        """ determines the test case with the lowest objective score (e.g., branch distance +
            approach level for branch coverage)"""
        fronts_list=[]
        F0=set()
        for ui in self.uncovered_targets:
            tbest=None
            tbest_score=float('inf')
            for test_case in test_cases:
                # get the objective score of the test case for the uncovered target ui
                # if the objective score is the lowest, set tbest to the test case
                temp_test_case_score=test_case.get_objective_score_of_target(ui)
                if temp_test_case_score<tbest_score:
                    tbest=test_case
                    tbest_score=temp_test_case_score
                # tbest = min(test_cases, key=lambda tc: self.objective_score(tc, ui))
                # rank 0 is assigned to this test case (i.e. insert into the first non-dominated front F0)
                # this gives tbest a higher chance of surviving in to the next generation
            if tbest:
                F0.add(tbest)
        if len(F0)!=0:
            fronts_list.append(F0)
        remaining_test_cases=set(test_cases)-F0
        #for speeding up the algorithm,
        # traditional non-dominated sorting algorithm is applied
        # only when the number of test cases in F0 is smaller than the population size
        if len(F0)>self.population_size:
            #if the number of test cases in F0 is greater than the population size,
            #the remaining test cases are added to the next front
            F1=set()
            F1=remaining_test_cases
            # there will be 2 fronts only in this case (F0 and F1) and we return them
            if len(F1)!=0:
                fronts_list.append(F1)
        else:
            #apply the traditional non-dominated sorting algorithm
            E=self.fast_non_dominated_sort(remaining_test_cases)
            for Ed in E:
                if len(Ed)!=0:
                    fronts_list.append(Ed)
        return fronts_list

    def calculate_objective_score_all_population(self,all_population,log_file):
        """Calculates the objective score for each test case in the given population."""
        deal_with_separate_test_cases(all_population,self.test_cluster.project_path,self.test_cluster,log_file)
    
    def revise_population_size(self):
        """Revises the count of the population. If the count is less than the population size, add random test cases."""
        remaining_population_size=self.population_size-len(self.population)
        remaining_population_size=1
        while remaining_population_size>0:
            new_test_case=generate_random_test_case(self.test_cluster)
            if new_test_case!=None:
                self.population.append(new_test_case)
            # we should proceed to not get stuck in an infinite loop
            remaining_population_size-=1
        # check if the population is empty 
        if len(self.population)==0:
            return 0
        return 1
    
    def revise_population(self):
        # loop on the population and remove the test cases that are not feasible
        # self.population = [test_case for test_case in self.population if not test_case.fail]
        if len(self.population)==0:
            return True
        return False
    
    def revise_parameters(self):
        """Revises the parameters of the algorithm according to the number of offsprings generated."""
        if self.count_offspring_generated==15:
            self.reuse_variable_probability=0.6
            self.power_of_quantity_of_change=2
            self.test_cluster.set_min_max_rand_values(0,1000)
        elif self.count_offspring_generated==20:
            self.reuse_variable_probability=0.7
            self.power_of_quantity_of_change=3
            self.test_cluster.set_min_max_rand_values(-100000,100000)
        elif self.count_offspring_generated==30:
            self.reuse_variable_probability=0.8
            self.power_of_quantity_of_change=4
            self.test_cluster.set_min_max_rand_values(-1000000,1000000)
        elif self.count_offspring_generated==40:
            self.reuse_variable_probability=0.9
            self.power_of_quantity_of_change=5
            self.test_cluster.set_min_max_rand_values(-10000000,10000000)
# Mosa1=MOSA()
# print(Mosa1.crossover("def test_case_1(self):a=65 b=72 c=30 avg(a,b,c)","def test_case_2(self):a=65 b=12 c=46 avg(a,b,c)"))
        
def use_mosa_algorithm(random_test_cases_list,test_cluster,log_file):
    """Use the MOSA algorithm to generate test cases."""
    mosa=MOSA(test_cluster)
    test_cases_list_mosa=[]
    time_start = test_cluster.get_start_time()
    # Initialize the population with random test cases
    mosa.population=random_test_cases_list
    # Deal with separate test cases     
    mosa.calculate_objective_score_all_population(random_test_cases_list,log_file)
    # Revise the test cases size
    if mosa.revise_population():
        return None,None
    # Get the global targets (covered or not covered) of all test cases
    archive=Archive(random_test_cases_list)
    # Update the archive of test cases
    archive.update_archive(random_test_cases_list)
    # Check if the search budget is consumed or not
    while mosa.time_limit > time.time()-time_start:
        if archive.is_all_covered():
            print("All coverage targets are covered")
            break
        # Generate offspring using crossover and mutation
        new_population=mosa.generate_offspring()
        all_population=mosa.population+new_population
        # Calculate the objective score for each test case
        mosa.calculate_objective_score_all_population(new_population,log_file)
        # Revise the test cases size
        if mosa.revise_population() == True:
            print("Population is empty")
            break
        # Update the archive with the new test cases
        archive.update_archive(new_population)
        # Get the uncovered targets of the archive
        mosa.uncovered_targets=archive.get_archive_uncovered_targets()
        # Apply the prefrence criterion to sort the test cases
        mosa.fronts_list=mosa.preference_sorting(all_population)
        mosa.population=[]
        d=0
        # The algorithm first selects the non-dominated test cases from the first front (F0); 
        # If the number of selected test cases is lower than the population size M,
        # The loop selects more test cases from the second front (F1),and so on.
        # The loop stops when adding test cases from current front Fd exceeds the population size M
        while len(mosa.fronts_list)>d and len(mosa.population)+len(mosa.fronts_list[d])<mosa.population_size:
            # Crowding distance assignment
            mosa.assign_crowding_distance(mosa.fronts_list[d])#TODO
            mosa.population+=mosa.fronts_list[d]
            d+=1
        # alternative mosa.fronts_list[d].sort(key=lambda x: x.objective_score)

        # if the number of selected test cases is less than the population size M,
        if len(mosa.population)<mosa.population_size:
            # the algorithm selects the test cases with the highest crowding distance from the current front Fd
            if len(mosa.fronts_list)>d :
                sorted_front=mosa.sort_front_using_crowding_distance(mosa.fronts_list[d])
                # the algorithm selects the remaining test cases from the current front Fd according
                # to the descending order of crowding distance.
                mosa.population+=sorted_front[0:mosa.population_size-len(mosa.population)]
        # Revise the parameters of the algorithm
        mosa.revise_parameters()
    # Final reporting 
    time_consumed_minutes = (time.time() - time_start) / 60
    log_file.write(f"Time consumed: {time_consumed_minutes:.2f} minutes\n")
    log_file.write(f"Number of offsprings generated: {mosa.count_offspring_generated}\n")
    # create object of CoverageResults class
    results_wrapper=CovergaeResults(time_consumed_minutes,mosa.count_offspring_generated)
    archive.calc_coverage_statistics(log_file,results_wrapper)
    archive.write_archive_report(results_wrapper)
    return archive.get_best_solutions(),results_wrapper