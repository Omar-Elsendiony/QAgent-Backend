import json
import re
import ast
import astunparse
import subprocess
import sys
import astunparse
from subprocess import PIPE
import threading
from ..generationAlg.coveragetarget import CoverageTarget
from .insertionlocalsprint import insert_print_locals_using_ast,insert_print_locals_lineno_using_ast
def get_executed_lines_percent(project_path:str):
    executed_lines_percent=0
    coverage_file = open(f"{project_path}/classical/coverage/coverage.json")
    
    # dictionary
    data = json.load(coverage_file)
    executed_lines_percent= data['files']['classical/outputtests/test.py']['summary']['percent_covered']
        
    # Closing file
    coverage_file.close()
    return executed_lines_percent
def get_uncovered_targets_indices(project_path:str):
    missing_branches_index=[]
    coverage_file = open(f"{project_path}/classical/coverage/coverage.json")
    # dictionary
    data = json.load(coverage_file)
    
    # Iterating through the json
    # list
    for branch in data['files']['classical/outputtests/test.py']['missing_branches']:
        missing_branches_index.append(branch[0])
    #remove the branch of __main__, (it is the last branch)
    missing_branches_index=missing_branches_index[:-1]
    # Closing file
    coverage_file.close()
    return set(missing_branches_index)
def get_executed_branches_indices(project_path:str):
    executed_branches_indices=[]
    coverage_file = open(f"{project_path}/classical/coverage/coverage.json")
    
    # dictionary
    data = json.load(coverage_file)
    
    # Iterating through the json
    # list
    for branch in data['files']['classical/outputtests/test.py']['executed_branches']:
        executed_branches_indices.append(branch[0])
    #remove the branch of __main__, (it is the last branch)
    executed_branches_indices=executed_branches_indices[:-1]

    # Closing file
    coverage_file.close()
    return set(executed_branches_indices)
def get_excluded_targets_indices(missing_branches_indices:set,project_path:str):
    #excluded means that the branch is missing (did not cover true and false targets) and did not even tried to reach it 
    #which means that the test case did not evaluate it to true nor false
    excluded_branches_indices=[]
    executed_branches_indices=get_executed_branches_indices(project_path)
    
    # Iterating through the json
    # list
    for branch in missing_branches_indices:
        #check if the branch is not in the missing branches
        if branch not in executed_branches_indices:
            excluded_branches_indices.append(branch)
    return set(excluded_branches_indices)
def get_fully_covered_targets_indices(missing_branches_indices:set,executed_branches_indices:set):
    #fully covered means that the branch has covered both targets (true and false)
    #it would be the intersection executed set - missing set
    #branch is executed as it is covered, it is not missing as it is not in the missing set
    fully_covered_branches_indices=executed_branches_indices - missing_branches_indices
    return fully_covered_branches_indices
def get_partial_covered_targets_indices(missing_branches_indices:set,executed_branches_indices:set):
    #partialy covered means that the branch has covered one of the 2 targets (true or false) but not both
    #it would be the intersection between the missing branches and the executed branches
    #it is missing as it did not cover both targets, but it is executed as it covered one of them
    # and so i already reached this branch
    partial_covered_branches_indices=missing_branches_indices & executed_branches_indices
    return partial_covered_branches_indices
# get_fully_covered_targets_indices({1,2,3,4,5,999},{1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16})

# missing_branches_index=get_uncovered_targets_indices(project_path)
# get_excluded_targets_indices=get_excluded_targets_indices(missing_branches_index,project_path)
# insert print locals() before the uncovered targets
def insert_print_locals(missing_branches_index:set,project_path):
    #create a file to write the locals() in it
    # file = open(f"{project_path}classical/fitness/testforlocals.py", "w")
    uncovered_targets = []
    test_file_string=""
    with open(f"{project_path}/classical/outputtests/test.py", "r") as f:
        # file.write("")
        for i, line in enumerate(f):
            test_file_string+=line
            if i+1 in missing_branches_index:
                
                #remove the leading spaces
                line=line.lstrip()
                # #insert the print locals() before the start of if block 
                # if re.match(r'^\s*if\s', line):
                #     file.write(write_to_json_string+ "\n")
                # #remove the \n at the end of the line
                # # if line[-1] == '\n':
                # #     line=line[:-1]
                uncovered_targets.append(line)
            # file.write(line)
            # #if the line contains the definition of the function, insert the print locals() after it
            # if line.find("def")!=-1:
            #     file.write(after_definition+ "\n")
    f.close()
    new_test_file_string,new_test_file_string2=insert_print_locals_lineno_using_ast(test_file_string,missing_branches_index,project_path)
    with open(f"{project_path}/classical/fitness/localsfiles/testforlocals.py", 'w') as file:
        file.write(new_test_file_string)
    file.close()
    with open(f"{project_path}/classical/fitness/localsfiles/testforlocals2.py", 'w') as file2:
        file2.write(new_test_file_string2)
    file2.close()
    return uncovered_targets

def get_targets_string(branches_index:set,project_path:str):
    f = open(f"{project_path}/classical/outputtests/test.py", "r")
    targets = [] 
    if len(branches_index)==0:
        return []
    for i, line in enumerate(f):
        if i+1 in branches_index:
            #remove the leading spaces
            line=line.lstrip()
            #remove the \n at the end of the line
            # if line[-1] == '\n':
            #     line=line[:-1]
            targets.append(line)
    f.close()
    return targets
def get_locals_dict(project_path):
    # Initialize an empty list to store dictionaries
    list_of_dicts = []
    list_of_lineno=[]
    # Path to the text file containing dictionaries
    file_path = f"{project_path}/classical/fitness/localsfiles/localsdictionary.txt"
    file_path2=f"{project_path}/classical/fitness/localsfiles/localslineno.txt"
    # Read the file line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Parse each line as a dictionary using eval() or json.loads()
            # Here we assume each line contains a JSON-encoded dictionary
            # If your dictionaries are in a different format, adjust accordingly
            #remove new line at end
            if line[-1] == '\n':
                line=line[:-1]
            # Remove the 'f' key and its value from the line
            pattern1 = r", 'anotate_f':.*?>"
            # pattern2 = r", 'currentframe':.*?>"
            # pattern3=r", 'getframeinfo':.*?>"
            modified_line = re.sub(pattern1, "", line)
            # modified_line = re.sub(pattern2, "", modified_line)
            # modified_line = re.sub(pattern3, "", modified_line)
            # Parse each modified line as a dictionary using eval()
            try:
                dictionary = eval(modified_line)
            except Exception as e:
                print("Error in parsing the locals dictionary from the file")
                print(str(e))
            #remove the JSONFile key from the dict
            try:
                del dictionary['JSONFile']
            except Exception as e:
                print("Error key JSONFile does not exist in the dictionary of locals")
            # Append the parsed dictionary to the list
            list_of_dicts.append(dictionary)
            
    with open(file_path2, 'r') as file2:
        #get the 'aha' and its value from the line
        for line in file2:
            pattern = r"'aha':\s*(\d+)"
            match = re.search(pattern, line)
            if match:
                list_of_lineno.append(match.group(1))
    # Print the list of dictionaries
    # print(list_of_dicts)
    return list_of_dicts,list_of_lineno
# list_of_dicts=get_locals_dict(project_path)
def get_uncovered_targets_with_locals_dict(uncovered_targets,list_of_dicts,list_of_lineno):
    uncovered_targets_dict=dict()
    index=0
    current_line_number=0
    for i in range(0,len(uncovered_targets)):
        current_line_number=int(list_of_lineno[index])
        # if uncovered_targets[i][-1] == '\n':
        #     uncovered_target=uncovered_targets[i][:-1]
        uncovered_targets_dict[uncovered_targets[i]]=list_of_dicts[index]
        #if the condition is if statement, increment the index
        if  i+1<len(uncovered_targets) and uncovered_targets[i+1].find("elif")!=-1 :
            continue
        index+=1
        #here the next line is not elif 
        #but we want to check that the locals dicts are for the same line number (due to a for loop or a while loop)
        #increment the index until the line number changes
        while len(list_of_lineno)>index and current_line_number==int(list_of_lineno[index]):
            index+=1
    return uncovered_targets_dict
# dict_of_uncov_and_their_locals_dict=get_uncovered_targets_with_locals_dict(uncovered_targets,list_of_dicts)

def get_uncovered_targets_data(project_path, log_file):
    try:
        missing_branches_index=get_uncovered_targets_indices(project_path)
        executed_branches_index=get_executed_branches_indices(project_path)
    except Exception as e:
        print("Error in getting the missing branches while reading file coverage.json")
        log_file.write("Error in getting the missing branches while reading file coverage.json\n")
        log_file.write(str(e)+"\n")
        return None,None,None
    # the differnce betwwen missing branches and partially covered branches is that the partially covered branches are executed (covered on target but not the other one)
    # but the missing branches include the partially covered branches and branches that are not executed at all (not reached branches)
    # as we are DynaMOSA we are interested in the partially covered branches
    partial_branches_index=get_partial_covered_targets_indices(missing_branches_index,executed_branches_index)
    covered_branches_indices=get_fully_covered_targets_indices(missing_branches_index,executed_branches_index)
    try:
        uncovered_targets=insert_print_locals(partial_branches_index,project_path)
    except Exception as e:
        print("Error in inserting print locals() in the test file")
        log_file.write("Error in inserting print locals() in the test file\n")
        log_file.write(str(e)+"\n")
        return None,None,None
    try:
        #run file "testforlocals.py"
        subprocess.run(["python", f"{project_path}/classical/fitness/localsfiles/testforlocals.py"],timeout=2, check=True, stderr=subprocess.PIPE)
        subprocess.run(["python", f"{project_path}/classical/fitness/localsfiles/testforlocals2.py"],timeout=2, check=True, stderr=subprocess.PIPE)
    except subprocess.TimeoutExpired:
        print("Subprocess execution timed out.")
        log_file.write("Subprocess execution timed out while executing testforlocals.\n")
        return None,None,None
    except Exception as e:
        print("Error in running testforlocals.py please check this file..")
        print(str(e))
        log_file.write("Error in running testforlocals.py please check this file..\n")
        log_file.write(str(e)+"\n")
        return None,None,None
    try:
        list_of_dicts,list_of_lineno=get_locals_dict(project_path)
        uncovered_targets_dict=get_uncovered_targets_with_locals_dict(uncovered_targets,list_of_dicts,list_of_lineno)
    except Exception as e:
        print("Error in getting the locals dictionary for each uncovered branch")
        print(str(e))
        log_file.write("Error in getting the locals dictionary for each uncovered branch\n")
        log_file.write(str(e)+"\n")
        return None,None,None
    return uncovered_targets_dict,partial_branches_index,covered_branches_indices

# #calculate the objective score
# #convert each uncovered target to an ast
    
def fix_condition(condition,locals_dict):
    #remove the \n at the end of the line
    if condition[-1] == '\n':
        condition=condition[:-1]
    #if there is comments in the condition, remove them
    if condition.find("#")!=-1:
        condition=condition[:condition.find("#")]
    #if the condition is an elif or else -> make it if (just for parsing and calculating the objective score)
    #as to parse the condition using ast.parse, it must be an if statement
    # Use regex to find 'elif' or 'else' followed by a condition
    pattern = r'\b(elif|else)\b'
    match = re.search(pattern, condition)
    if match:
        # Replace 'elif' or 'else' with 'if'
        condition = re.sub(pattern, r'if', condition)
    #evaluate the condition as true or false
    #remove the spaces at the end of the condition
    condition_string=condition.rstrip()
    #remove the : at the end of the condition
    condition_string=condition_string[:-1]
    #remove the if at the beginning of the condition
    condition_string=condition_string[3:]
    try:
        true_or_false= eval(condition_string, {}, locals_dict)
    except Exception as e:
        print("Error in evaluating the condition '"+condition+"'using local dictionary:"+str(locals_dict))
        print(str(e))
        true_or_false=None
    #put an empty {} at the end 
    #as to parse the condition using ast.parse,the body must not be empty, it must be a block of code
    condition=condition+"{}"
    #if the condition was a for loop, we want to evaluate it to false as it is not covered
    pattern_for = r'^for\b'
    match = re.search(pattern_for, condition)
    if match:
        true_or_false=False
    #if the condition was a while loop, we want to evaluate it to false as it is not covered
    pattern_while = r'^while\b'
    match2 = re.search(pattern_while, condition)
    if match2:
        true_or_false=False
    return condition,true_or_false

# Define a function to parse the condition statement
def parse_condition(condition,locals_dict):
    # Fix the condition statement
    condition,true_or_false = fix_condition(condition,locals_dict)

    # Parse the condition statement using AST
    try:
        tree = ast.parse(condition)
    except Exception as e:
        print("Error in parsing the tree condition '"+condition+"'")
        print(str(e))
        tree=None
    #print the tree
    # print(astunparse.dump(tree))
    return tree,true_or_false

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]

        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)

            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]

def loop_evaluation(node, local_vars):
    # return constant branch distance for loops
    return 1

def calculate_branch_distance_Eq(result,lhs_value, rhs_value, operator):
    if result==True:
        return 0
    elif isinstance(lhs_value, (int, float)) and isinstance(rhs_value, (int, float)):
        return abs(lhs_value - rhs_value)
    elif isinstance(lhs_value, str) and isinstance(rhs_value, str):
        return levenshtein_distance(lhs_value, rhs_value)
    elif isinstance(lhs_value, bytes) and isinstance(rhs_value, bytes):
        return levenshtein_distance(lhs_value.decode(), rhs_value.decode())
    else:
        # Return infinity for other cases
        return sys.maxsize
def calculate_branch_distance_NotEq(result,lhs_value, rhs_value, operator):
    if result==True:
        return 0
    else:
        return 1
def calculate_branch_distance_Lt(result,lhs_value, rhs_value, operator):
    if result==True:
        return 0
    elif isinstance(lhs_value, (int, float)) and isinstance(rhs_value, (int, float)):
        return abs(rhs_value - lhs_value)+1
    else:
        # Return infinity for other cases
        return sys.maxsize
def calculate_branch_distance_In(result,lhs_value, rhs_value, operator):
    if result==True:
        return 0
    else:
        # Calculate the distance between the LHS value and each element in the RHS list
        #we must put False as lhs is not in rhs
        distances = [calculate_branch_distance_Eq(False,lhs_value, x) for x in rhs_value]
        return min(distances + [float('inf')])
def calculate_branch_distance_Or(result,lhs_value, rhs_value, operator):
    return min(lhs_value, rhs_value)
def calculate_branch_distance_And(result,lhs_value, rhs_value, operator):
    return max(lhs_value, rhs_value)

def calculate_objective_score(lhs_value, rhs_value, operator):
    #calculate the objective score for the branch to be evaluated to true 
    if operator == 'Eq':
        result= lhs_value == rhs_value
        branch_distance=calculate_branch_distance_Eq(result,lhs_value, rhs_value, operator)
    elif operator == 'NotEq':
        result= lhs_value != rhs_value
        branch_distance=calculate_branch_distance_NotEq(result,lhs_value, rhs_value, operator)
    elif operator == 'Lt':
        result= lhs_value < rhs_value
        branch_distance=calculate_branch_distance_Lt(result,lhs_value, rhs_value, operator)
    elif operator == 'LtE':
        result= lhs_value <= rhs_value
        branch_distance=calculate_branch_distance_Lt(result,lhs_value, rhs_value, operator)
    elif operator == 'Gt':
        result= lhs_value > rhs_value
        branch_distance=calculate_branch_distance_Lt(result,rhs_value, lhs_value, operator)
    elif operator == 'GtE':
        result= lhs_value >= rhs_value
        branch_distance=calculate_branch_distance_Lt(result,rhs_value, lhs_value, operator)
    elif operator == 'Is':
        result= lhs_value is rhs_value
        branch_distance=calculate_branch_distance_NotEq(result,lhs_value, rhs_value, operator)
    elif operator == 'IsNot':
        result= lhs_value is not rhs_value
        branch_distance=calculate_branch_distance_NotEq(result,lhs_value, rhs_value, operator)
    elif operator == 'In':
        result= lhs_value in rhs_value
        branch_distance=calculate_branch_distance_In(result,lhs_value, rhs_value, operator)
    elif operator == 'NotIn':
        result= lhs_value not in rhs_value
        branch_distance=calculate_branch_distance_NotEq(result,lhs_value, rhs_value, operator)
    elif operator == 'Or':
        result= lhs_value or rhs_value
        branch_distance=calculate_branch_distance_Or(result,lhs_value, rhs_value, operator)
    elif operator == 'And':
        result= lhs_value and rhs_value
        branch_distance=calculate_branch_distance_And(result,lhs_value, rhs_value, operator)
    # elif operator == 'Not':
    #     result= not lhs_value
    #     branch_distance=calculate_branch_distance_NotEq(result,lhs_value, True, operator)
    else:
        raise ValueError(f"Unknown operator: {operator}")
    # branch distance
    return branch_distance

def recursion_evaluation_true(node, local_vars):
    if isinstance(node, ast.Name):
        return local_vars.get(node.id, None)
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.Call):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.UnaryOp):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.Subscript):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.For):
        return loop_evaluation(node, local_vars)
    elif isinstance(node, ast.While):
        return loop_evaluation(node, local_vars)
    elif isinstance(node, ast.Compare):
        lhs = recursion_evaluation_true(node.left, local_vars)
        rhs = recursion_evaluation_true(node.comparators[0], local_vars)
        operator_list=[type(op).__name__ for op in node.ops]
        rhs_list = node.comparators
        tempNames = []
        for c in (node.comparators):
            tempNames.append(c)
        if len(tempNames) > 1:
            result1 = calculate_objective_score(lhs, rhs, operator_list[0])
            result2 = recursion_evaluation_true(tempNames[0],local_vars)
            result3 = recursion_evaluation_true(tempNames[1],local_vars)
            result4 = calculate_objective_score(result2, result3, operator_list[-1])
            return calculate_objective_score(result1, result4, 'And')
        else:
            return calculate_objective_score(lhs, rhs, operator_list[0])
    elif isinstance(node, ast.BoolOp):
        values = [recursion_evaluation_true(value, local_vars) for value in node.values]
        operator = type(node.op).__name__
        if len(values) >2:
            result1 = calculate_objective_score(values[0], values[1], operator)
            result2 = calculate_objective_score(values[1], values[2], operator)
            return calculate_objective_score(result1, result2, operator)
        return calculate_objective_score(values[0],values[1], operator)
    else:
        for child_node in ast.iter_child_nodes(node):
            result = recursion_evaluation_true(child_node, local_vars)
            if result is not None:
                return result
def recursion_evaluation_false(node, local_vars,operators_complement_dict):
    if isinstance(node, ast.Name):
        return local_vars.get(node.id, None)
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.Call):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.UnaryOp):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.Subscript):
        #evaluate the node (as a whole) without recursion
        return eval(astunparse.unparse(node), {}, local_vars)
    elif isinstance(node, ast.For):
        #as the loop was not covered (did not evaluate to true) so the false branch distance is 0 (it evaluates to false)
        return 0 
    elif isinstance(node, ast.While):
        #as the loop was not covered (did not evaluate to true) so the false branch distance is 0 (it evaluates to false)
        return 0
    elif isinstance(node, ast.Compare):
        lhs = recursion_evaluation_false(node.left, local_vars,operators_complement_dict)
        rhs = recursion_evaluation_false(node.comparators[0], local_vars,operators_complement_dict)
        operator_list=[operators_complement_dict[type(op).__name__] for op in node.ops]
        rhs_list = node.comparators
        tempNames = []
        for c in (node.comparators):
            tempNames.append(c)
        if len(tempNames) > 1:
            result1 = calculate_objective_score(lhs, rhs, operator_list[0])
            result2 = recursion_evaluation_false(tempNames[0],local_vars,operators_complement_dict)
            result3 = recursion_evaluation_false(tempNames[1],local_vars,operators_complement_dict)
            result4 = calculate_objective_score(result2, result3, operator_list[-1])
            return calculate_objective_score(result1, result4, 'And')
        else:
            return calculate_objective_score(lhs, rhs, operator_list[0])
    elif isinstance(node, ast.BoolOp):
        values = [recursion_evaluation_false(value, local_vars,operators_complement_dict) for value in node.values]
        operator = operators_complement_dict[type(node.op).__name__]
        if len(values) >2:
            result1 = calculate_objective_score(values[0], values[1], operator)
            result2 = calculate_objective_score(values[1], values[2], operator)
            return calculate_objective_score(result1, result2, operator)
        return calculate_objective_score(values[0],values[1], operator)
    else:
        for child_node in ast.iter_child_nodes(node):
            result = recursion_evaluation_false(child_node, local_vars,operators_complement_dict)
            if result is not None:
                return result
    
# # operand_values,true_or_false = parse_condition("if x+1==y==z:",locals_dict)#("elif x==0 and y==1 and z==y:")
# target_string="elif x==71 or y==0 or bl==False:"
# excluded_branches_indices=[20]
# operand_values,true_or_false = parse_condition("if x+1==y==z:",locals_dict)#("elif x==0 and y==1 and z==y:")
# Example condition statement
def objective_score_uncovered_targets(target_string,locals_dict,branch_index,excluded_branches_indices):#(uncovered_targets_dict_with_locals):
    operators_complement_dict={'Eq':'NotEq','NotEq':'Eq','Lt':'GtE','LtE':'Gt','Gt':'LtE','GtE':'Lt','Is':'IsNot','IsNot':'Is','In':'NotIn','NotIn':'In','Or':'And','And':'Or','Not':'Not'}
    # for target,locals_dict in uncovered_targets_dict_with_locals.items():
    # Parse the condition statement
    tree,true_or_false = parse_condition(target_string,locals_dict)#("elif x==0 and y==1 and z==y:")
    # Calculate the objective score
    #call recursion to evaluate the condition
    objective_score_cond_true= sys.maxsize
    objective_score_cond_false= sys.maxsize
    if tree != None:
        objective_score_cond_true = recursion_evaluation_true(tree, locals_dict)
        objective_score_cond_false = recursion_evaluation_false(tree, locals_dict,operators_complement_dict)
    # Print the objective score
    # print(target_string)
    # print("Objective Score true:", objective_score_cond_true)
    # print("Objective Score false:", objective_score_cond_false)
    # print("==================================")
    #if it evaluates to True
    #create coverageTarget object of type True and covered to be appended to the covered targets
    #set the branch distance of the target
    target_true=CoverageTarget()
    target_true.target_string=target_string
    target_true.locals_dict=locals_dict
    target_true.target_type=True
    target_true.branch_distance=objective_score_cond_true
    #create coverageTarget object of type False and uncovered to be appended to the uncovered targets
    target_false=CoverageTarget()
    target_false.target_string=target_string
    target_false.locals_dict=locals_dict
    target_false.target_type=False
    target_false.branch_distance=objective_score_cond_false

    if true_or_false:#the condition evaluates to true or false
        #check if the branch is excluded or not (means not reached)
        if branch_index not in excluded_branches_indices:
            #mark the target_true as covered
            target_true.is_covered=True
    elif not true_or_false:
        #check if the branch is excluded or not (means not reached)
        if branch_index not in excluded_branches_indices:
            #mark the target_false as covered
            target_false.is_covered=True
    #the else is redundant, as we want to keep both targets as uncovered
    return target_true,target_false
#ENTER HERE

# r=eval("x==0 and y==1 and z==y", {}, {'x': 0, 'y': 5, 'z': 9})

# s=objective_score_uncovered_targets(target_string,locals_dict,branch_index,excluded_branches_indices)
# print(s)


