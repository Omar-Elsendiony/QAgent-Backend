import inspect   
import random
import string
import threading
import typing
import json
from typing import List,Dict,Set,Tuple,Any
# from .constants import LIST_OF_TYPES
from ..analysis.analysemodule import TestCluster
from .testcase import TestCase
from ..coverage.runcoveragepy import run_coveragepy


def generate_int_value(min,max):
    return random.randint(min, max)

def generate_str_value():
    str1=''.join(random.choices(string.ascii_lowercase, k = random.randint(0, 10)))
    str2=''.join(random.choices(string.ascii_uppercase, k = random.randint(0, 10)))
    str3=''.join(random.choices(string.ascii_uppercase+ string.ascii_lowercase + string.digits, k = random.randint(0, 10)))
    str4=''.join(random.choices(string.ascii_lowercase + ' ', k = random.randint(0, 10)))
    str5=''.join(random.choices(string.ascii_uppercase + '[]()<>?!#@%^&*_+', k = random.randint(0, 10)))
    str6=''.join(random.choices('**//+-', k = random.randint(0, 10)))
    str7=''.join(random.choices('[]', k = random.randint(0, 10)))
    str8=''.join(random.choices('()', k = random.randint(0, 10)))
    return random.choice([str1,str2,str3,str4,str5,str6,str7,str8])

def create_statement(test_cluster:TestCluster,test_case:TestCase,log_file):
    #get the min and max values for random generation
    min_rand_val,max_rand_val=test_cluster.get_min_max_rand_values()
    func_call=test_cluster.func_name+"("
    variables_init_stmts=[]
    temp_func_call=["func_call",test_cluster.func_name,[],[]]#the 2 lists: one for types of parameters, and the other for the variable names
    #loop on parameter dict and create variable for each parameter
    for param in test_cluster.function_signature.parameters:
        #get the type annotation of the parameter
        param_annotation=test_cluster.function_signature.parameters[param].annotation
        if param_annotation==inspect._empty and test_cluster.use_type4py==True: 
            #no type is specified
            #use the parameter types infered by type4py
            param_annotation=test_cluster.types_infered_dict[param]
        #check on the type of the parameter if exists in the dict
        if param_annotation not in test_case.variables_dict:
            #if the type is not in the dict, add it, create new list
            test_case.variables_dict[param_annotation]=[[],[]] #list of names and list of values
        # if param_annotation==Any:
            #choose random type for the parameter
            # param_annotation=random.choice(LIST_OF_TYPES)
        #this variable temp_param_name will be used to satisfy the function call with the created parameter in each itteration
        temp_param_name_index=len(test_case.variables_dict[param_annotation][0])
        temp_param_name=param_annotation.__name__+"_"+str(temp_param_name_index)
        if param_annotation==str:
            #list of strings values
            example_strings = []#["hello", "world", "foo", "bar", "python", "example","hi","aba","level",""]
            #generate random string value
            rand_str= generate_str_value()
            rand_value=random.choice(example_strings+[rand_str])
        elif param_annotation==int:
            #generate random int value between 0 and 100
            rand_value=random.randint(min_rand_val, max_rand_val)
        elif param_annotation==float:
            #generate random float value between 0 and 100
            rand_value=random.uniform(min_rand_val, max_rand_val)
        elif param_annotation==bool:
            #generate random boolean value
            rand_value=random.choice([True, False])
        elif param_annotation==list[int] or param_annotation==List[int]:
            #generate random list of integers 
            rand_value=[ generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))]
            temp_param_name=param_annotation.__name__+"_int_"+str(temp_param_name_index)
        elif param_annotation==list or List:
            #generate random list of integers or random list of strings
            if random.choice([0,1])==0:
                #generate random list of integers
                rand_value=[ generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))]
            else:
                rand_value=[ generate_str_value() for i in range(0,random.randint(0, 6))]
        elif param_annotation==list[str] or param_annotation==List[str]:
            #generate random list of strings
            rand_value=[ generate_str_value() for i in range(0,random.randint(0, 6))]
            temp_param_name=param_annotation.__name__+"_str_"+str(temp_param_name_index)
        elif param_annotation==list[float] or param_annotation==List[float]:
            #generate random list of floats
            rand_value=[ random.uniform(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))]
            temp_param_name=param_annotation.__name__+"_float_"+str(temp_param_name_index)
        elif param_annotation==list[bool] or param_annotation==List[bool]:
            #generate random list of booleans
            rand_value=[ random.choice([True, False]) for i in range(0,random.randint(0, 6))]
            temp_param_name=param_annotation.__name__+"_bool_"+str(temp_param_name_index)
        elif param_annotation==dict[str,int]:
            #generate random dict
            rand_value={ generate_str_value(): generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            temp_param_name=param_annotation.__name__+"_str_int_"+str(temp_param_name_index)
        elif param_annotation==dict[str,str]:
            #generate random dict
            rand_value={ generate_str_value(): generate_str_value() for i in range(0,random.randint(0, 6))}
            temp_param_name=param_annotation.__name__+"_str_str_"+str(temp_param_name_index)
        elif param_annotation==dict[int,int]:
            #generate random dict
            rand_value={ generate_int_value(min_rand_val, max_rand_val): generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            temp_param_name=param_annotation.__name__+"_int_int_"+str(temp_param_name_index)
        elif param_annotation==dict[int,str]:
            #generate random dict
            rand_value={ generate_int_value(min_rand_val, max_rand_val): generate_str_value() for i in range(0,random.randint(0, 6))}
            temp_param_name=param_annotation.__name__+"_int_str_"+str(temp_param_name_index)
        elif param_annotation==dict:
            #generate random dict of integers or random dict of strings
            if random.choice([0,1])==0:
                #generate random dict of integers
                rand_value={ generate_int_value(min_rand_val, max_rand_val): generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            else:
                rand_value={ generate_str_value(): generate_str_value() for i in range(0,random.randint(0, 6))}
        elif param_annotation==set or param_annotation==Set:
            #generate random set
            if random.choice([0,1])==0:
                #generate random set of integers
                rand_value={ generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            else:
                rand_value={ generate_str_value() for i in range(0,random.randint(0, 6))}
        elif param_annotation==set[int]:
            #generate random set
            rand_value={ generate_int_value(min_rand_val, max_rand_val) for i in range(0,random.randint(0, 6))}
            temp_param_name=param_annotation.__name__+"_int_"+str(temp_param_name_index)
        elif param_annotation==set[str]:
            #generate random set
            rand_value={ generate_str_value() for i in range(0,random.randint(0, 6))}
            temp_param_name=param_annotation.__name__+"_str_"+str(temp_param_name_index)
        elif param_annotation==tuple[int,int]:
            #generate random tuple
            rand_value=( generate_int_value(min_rand_val, max_rand_val), generate_int_value(0, 100))
            temp_param_name=param_annotation.__name__+"_tuple_"+str(temp_param_name_index)
        else:
            print (f"unsupported type {str(param_annotation)}")
            log_file.write("Error: Unsupported type: "+str(param_annotation)+"\n")
            return None,str(param_annotation)
        #add the variable to the dict
        # add the value to the list of values of the type
        test_case.variables_dict[param_annotation][0].append(temp_param_name)
        test_case.variables_dict[param_annotation][1].append(rand_value)
        #add the statement of the variable initialization to the list of statements
        test_case.generated_var_values.append([param_annotation,temp_param_name,rand_value])
        var_init="\t\t"+temp_param_name+"="+ str(rand_value)
        if param_annotation==str:
            var_init="\t\t"+temp_param_name+"='" + rand_value + "'"
        variables_init_stmts.append(var_init)
        #concatenate the variable name to the function call
        func_call=func_call+temp_param_name+","
        #append the type and the value of the parameter of the function call
        temp_func_call[2].append(param_annotation)
        temp_func_call[3].append(temp_param_name)
    #add the function call  to the list of generated values
    test_case.generated_var_values.append(temp_func_call)
    func_call=func_call[:-1]
    func_call=func_call+")"
    test_case_str="\n"
    test_case_str += '\n'.join(variables_init_stmts) + "\n" 
    assert_statement=get_expected_output_stmt(test_case_str,func_call,test_cluster)
    if assert_statement==None:
        test_case.failed=True
        return None,None
    #assign the expected output to the test case
    test_case.expected_output=assert_statement
    test_case_str += "\t\t" +assert_statement+'\n'
    return test_case,test_case_str

def get_expected_output_stmt(test_case_str,func_call,test_cluster):
    #remove \t in the test_case_str
    test_case_str='\n'.join(line.strip() for line in test_case_str.splitlines())
    test_case_str+= "\n"+"expected_output="+func_call
    code_to_run=test_cluster.source_code+test_case_str
    result = {}
    def run_code():
        nonlocal result
        try:
            exec(code_to_run, globals(), result)
        except Exception as e:
            result['exception'] = e
    try:
        thread = threading.Thread(target=run_code)
        thread.start()
        thread.join(timeout=2)
        if thread.is_alive():
            # Thread did not complete within the timeout
            result['timeout'] = True
            thread.join()  # Ensure the thread terminates
        #expected_output=result.get('expected_output')
        if 'timeout' in result:
            print(f"Error: Could not execute the code within {timeout} seconds +\n"+code_to_run+"\n")
            return None
        return_val=result.get('expected_output')
        if return_val==None:
            return None
        if 'exception' in result:
            print(f"Error: Could not execute the code to get expected output.\n"+str(result['exception'])+"\n"+code_to_run+"\n")
            return None
        return_type=test_cluster.function_signature.return_annotation
        # if the return type annotation does not exist in the function signature
        if return_type==inspect._empty and test_cluster.use_type4py==True:
            #get the type of the return from the infered types
            return_type=test_cluster.types_infered_dict["return"] 
        if return_type==str:
            return_value="'"+return_val+"'"
        else:
            return_value=str(return_val)
        assert_statement='self.assertEqual('+return_value+','+func_call+')'
    except Exception as e:
        print("Error: Could not execute the code!\n"+str(e)+"\n"+code_to_run+"\n")
        return None
    return assert_statement 

def create_testcase(index,test_cluster:TestCluster,log_file):
        #create the test case
        test_case=TestCase()
        test_case.project_path=test_cluster.project_path
        unit_test = f'''\tdef test_case_{index}(self):\n'''
        test_case,test_case_str=create_statement(test_cluster,test_case,log_file)
        if test_case== None:
            return None,None
        test_case.lines_count=len(test_case.generated_var_values)
        return test_case,unit_test+test_case_str

def generate_unit_tests(test_cluster:TestCluster,log_file):
    test_cases_list=[]
    testClass="import unittest\n\n"+ test_cluster.source_code 
    testClass+="""\n\nclass TestClass(unittest.TestCase):\n"""
    for i in range(0,test_cluster.tests_count_needed):
        test_case,test_case_str=create_testcase(i,test_cluster,log_file)
        # If the test case is None, then the code did not execute correctly (maybe the code is problematic or test case inputs are not supported by the code)
        # So generate another test case with tolerance of 5 trials, using the following loop
        # If the code itself is problematic so,
        # at maximum we would try to generate 5*test_cluster.tests_count_needed test cases then stop
        n_trials=0
        while test_case==None and test_case_str==None and n_trials<5:
            test_case,test_case_str=create_testcase(i,test_cluster,log_file)
            n_trials+=1
            # If we are using type4py, then we could try other types infered by the model
            if test_cluster.use_type4py==True:
                # we have 2 dicts for infered types
                # one has one type (value) for each param (key)
                # and the other has all types infered (value) (as list) for each param (key)
                # so we will change the dict infered_types values with random values (types) from the other dict all_param_types_infered 
                for param in test_cluster.types_infered_dict:
                    #get the list of all types infered for the parameter
                    all_types=test_cluster.all_param_types_infered[param]
                    #get the current infered type
                    infered_type=test_cluster.types_infered_dict[param]
                    #get the new type
                    new_type=random.choice(all_types)
                    #change the type in the dict infered_types
                    test_cluster.types_infered_dict[param]=new_type
        # If still the test case is None, continue
        if test_case==None and test_case_str==None:
            continue
        testClass+=test_case_str
        testClass+="\n"
        test_cases_list.append(test_case)
    testClass+="""if __name__ == '__main__':
    unittest.main()
    """
    if len(test_cases_list)==0:
        log_file.write("Error: No test cases have been generated\n")
        print("Error: No test cases have been generated")
        return None
    # Write the resulting string to a file
    with open(f'{test_cluster.project_path}/classical/outputtests/randomtest.py', 'w') as file:
        file.write(testClass)
    print("Test file 'randomtest.py' has been created.")
    # run the coverage py to get the branches count from coverage.json file 
    # so that if the input code has no branches, return random test cases to the user
    # else run the MOSA algorithm to find the best test case
    is_branchless_module(test_cluster)
    return test_cases_list

def is_branchless_module(test_cluster:TestCluster):
    """If the input code has no branches, return true else false."""
    #run coverage py
    run_coveragepy(test_cluster.project_path,"randomtest.py")
    branches_count=0
    coverage_file = open(f"{test_cluster.project_path}/classical/coverage/coverage.json")
    
    # dictionary
    data = json.load(coverage_file)
    branches_count= data['files']['classical/outputtests/randomtest.py']['summary']['num_branches']
     
    # Closing file
    coverage_file.close()
    if branches_count>2: # 2 because of  the "if __name__ == '__main__': unittest.main()"
        #it has branches
        test_cluster.set_actual_targets_count(branches_count-2)
        test_cluster.set_contains_conditions(True)
        return False
    # it is branchless
    test_cluster.set_actual_targets_count(0)
    test_cluster.set_contains_conditions(False)
    return True

def generate_random_test_case(test_cluster:TestCluster,unit_test_index,log_file):
    test_case,test_case_str=create_testcase(unit_test_index,test_cluster,log_file)
    # If the test case is None, then the code did not execute correctly (maybe the code is problematic or test case inputs are not supported by the code)
    # So generate another test case with tolerance of 2 trials, using the following loop
    # If the code itself is problematic so,
    # at maximum we would try to generate 2 test cases then stop
    test_case,test_case_str=create_testcase(i,test_cluster,log_file)
        
    # if still the test case is None, return None
    if test_case==None and test_case_str==None:
        return None
    return test_case

def convert_testcase_to_string(test_case,index,test_cluster:TestCluster,log_file):
    test_case_def = f'''\tdef test_case_{index}(self):\n'''
    test_case_stmts=""
    for var in test_case.generated_var_values:
        if var[0]=="func_call":
            func_call=var[1]+"("
            for i in range(0,len(var[2])):
                if var[2][i]==str:
                    func_call=func_call+"'"+var[3][i]+"',"
                else:
                    func_call=func_call+str(var[3][i])+","
            func_call=func_call[:-1]
            func_call=func_call+")"
            if test_case.expected_output==None:
                #calculate the expected output
                expected_output=get_expected_output_stmt(test_case_stmts,func_call,test_cluster)
                if expected_output==None:
                    print("Error: Could not execute the code.")
                    log_file.write("Error: Could not execute the code.\n"+test_cluster.source_code+test_case_stmts+func_call+"\n")
                    test_case.failed=True
                    return None
                test_case.expected_output=expected_output
            else:
                #retrieve the expected output from the test case
                expected_output=test_case.expected_output
            test_case_stmts += "\t\t" +expected_output+'\n'
        else:
            if var[0]==str:
                var_init="\t\t"+var[1]+"='" + var[2] + "'"
            else:
                var_init="\t\t"+var[1]+"="+ str(var[2])
            test_case_stmts += var_init + "\n"
    return test_case_def+test_case_stmts

def create_test_file_from_testcase_string(project_path,file_name,method_under_test,test_case_str):
    testClass="import unittest\n\n"
    testClass+=method_under_test
    testClass+="""\n\nclass TestClass(unittest.TestCase):\n"""
    testClass+=test_case_str
    testClass+="""if __name__ == '__main__':
    unittest.main()
    """
    file_path = f'{project_path}/classical/outputtests/{file_name}'
    # Write the resulting string to a file
    with open(file_path, 'w') as file:
        file.write(testClass)
    return testClass

def export_test_cases_to_file(file_name,test_cases_list,test_cluster:TestCluster,log_file):
    tests_string=""
    for index,test_case in enumerate(test_cases_list):
        test_case_str=convert_testcase_to_string(test_case,index,test_cluster,log_file)
        if test_case_str==None:
            continue
        tests_string+=test_case_str
        tests_string+="\n"

    test_file_string=create_test_file_from_testcase_string(test_cluster.project_path,file_name,test_cluster.source_code,tests_string)
    return test_file_string