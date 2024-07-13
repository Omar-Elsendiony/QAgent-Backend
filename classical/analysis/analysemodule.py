import ast
from types import ModuleType
import builtins
import importlib
import inspect
import requests
import json
import sys
import ast
import time
import typing
from typing import List,Tuple,Dict,Set,Iterable,Iterator,Union,Optional,Any,Sequence
from .genericcallable import *

class TestCluster:
    """ A class that contains all information about a module, functions, classes"""
    def __init__(self,start_time):
        self.module_name = None
        self.import_module = None
        self.source_code = None
        self.func_name = None
        self.function_signature = None
        self.lines_num = None
        self.callables_list = []
        self.tests_count_needed=10
        self.use_type4py = False
        self.types_infered_dict = {}
        self.all_param_types_infered = {}
        self.project_path = None
        self.min_max_rand_values=[0,100]
        self.params_occurence_dict={}
        self.contains_conditions = True
        self.start_time=start_time
        self.actual_targets_count=0
    
    def set_data(self,project_path,module_name: str,import_module, source_code: str,lines_num:int):
        """Set the data of the test cluster"""
        self.project_path = project_path
        self.module_name = module_name
        self.import_module = import_module
        self.source_code = source_code
        self.lines_num = lines_num
    
    def set_function_data(self,function_callable:FunctionCallable,function_signature: inspect.Signature,param_types_infered:dict,all_param_types:dict):
        """Set the data of the function to be tested"""
        self.function_signature = function_signature
        self.types_infered_dict = param_types_infered
        self.all_param_types_infered = all_param_types
        self.callables_list.append(function_callable)
        self.func_name = function_callable.name
    
    def set_use_type4py(self,use_type4py:bool):
        """Set the use type4py flag"""
        self.use_type4py = use_type4py
    
    def set_contains_conditions(self,contains_conditions:bool):
        """Set the contains conditions flag"""
        self.contains_conditions = contains_conditions
    
    def get_contains_conditions(self):
        """Get the contains conditions flag"""
        return self.contains_conditions
    
    def get_all_param_types_infered(self):
        """Return the all param types infered"""
        return self.all_param_types_infered
    
    def get_start_time(self):  
        """Get the start time of the analysis"""
        return self.start_time

    def get_min_max_rand_values(self):
        """Return the min and max values for random generation"""
        return self.min_max_rand_values[0],self.min_max_rand_values[1]
    
    def set_min_max_rand_values(self,min_val:int,max_val:int):
        """Set the min and max values for random generation"""
        self.min_max_rand_values[0]=min_val
        self.min_max_rand_values[1]=max_val
    
    def get_params_info(self):
        """Return the parameters types and counts of the function to be tested"""
        return self.params_occurence_dict

    def calculate_func_params_info(self):
        """claculate the parameters types (key) and counts (value) of the function to be tested.
        This dictionary is used to limit the insertion mustation to certain extent,
        to avoid multi unused insertion mutations"""
        # iterate over the parameters of the function sinature
        for param in self.function_signature.parameters.values():
            param_type = param.annotation
            if self.use_type4py:
                # get the type from the infered types
                param_type = self.types_infered_dict[param.name]
            if param_type not in self.params_occurence_dict:
                # if the type is not in the dict, add it, create new list
                self.params_occurence_dict[param_type]=0
            # increment the count of the type
            self.params_occurence_dict[param_type]+=1
    
    def set_actual_targets_count(self,count):
        """Sets the count of actual targets, if one branch exists --> this is considered 2 targets (true, false)"""
        self.actual_targets_count=count
        
    def get_actual_targets_count(self):
        """ Returns the actual targets count"""
        return self.actual_targets_count
    
# def contains_conditions(code,test_cluster):
#     """Check if the code contains conditions or not"""
#     count=0
#     tree = ast.parse(code)
#     for node in ast.walk(tree):
#         if isinstance(node, ast.If) or isinstance(node,ast.While) or isinstance(node,ast.For):
#             count+=1
#     if count==0:
#         test_cluster.set_contains_conditions(False)
#         return False
#     test_cluster.set_actual_targets_count(count)
#     test_cluster.set_contains_conditions(True)
#     return True

def analyse_module(module_name:str,project_path:str,log_file):
    """Analyse the module and return the results."""
    # start the timer
    start_time = time.time()
    # create an object of the TestCluster class
    test_cluster=TestCluster(start_time)
    use_type_hints: bool = True
    use_type4py: bool = False
    # Remove the module from sys.modules to force a reload
    if module_name in sys.modules:
        del sys.modules[module_name]
    try:
        imported_module= importlib.import_module(module_name)
        importlib.reload(imported_module)
    except (ModuleNotFoundError,TypeError, OSError,ImportError,NameError) as e:
        print("Error: Could not import the module")
        print(e)
        log_file.write("Error: Could not import the module")
        log_file.write(str(e))
        return None,"Error: Could not import the module"
    except SyntaxError as e:
        print("Error: Syntax error in the module")
        print(e)
        log_file.write("Error: Syntax error in the module")
        log_file.write(str(e))
        return None,"Error: Syntax error in the module"
    module_code = inspect.getsource(imported_module)
    # get number of lines
    lines = module_code.split("\n")
    lines_num = len(lines)
    # set the attributes of the test_cluster
    test_cluster.set_data(project_path,module_name,imported_module,module_code,lines_num)
    
    # iterate over the attributes of the module
    for name in dir(imported_module):
        attr = getattr(imported_module, name)
        if inspect.isfunction(attr):
            print("Module analysed successfully")
            log_file.write("Module analysed successfully\n")
            print(f"{name} is a function")
            log_file.write(f"Function found: {name}\n")
            function_signature = inspect.signature(attr)
            # Before we proceed we need to check if the input code has branches or not
            # if not contains_conditions(module_code,test_cluster):
            #     print("No branches (conditions) in the input code")
            #     log_file.write("No branches (conditions) in the input code\n")
            #check if any paramater does not have type annotation
            param_types = {}
            all_param_types= {}
            for param in function_signature.parameters.values():
                if param.annotation == inspect.Parameter.empty or function_signature.return_annotation == inspect._empty:
                    log_file.write("Function signature has no type hints, trying to infere types...\n")
                    print("Function signature has no type hints, trying to infere types...")
                    use_type4py = True
                    param_types,all_param_types=infere_types(project_path,log_file)
                    if param_types!=None:
                        log_file.write("Types inferred successfully\n")
                    else:
                        log_file.write("Error: Could not infer types\n")
                        return None,"Error: Could not infer types\n"
                    break
            #create a function callable object
            function_callable = FunctionCallable(name, None, function_signature, 0)
            # set the attributes of the test_cluster
            test_cluster.set_function_data(function_callable,function_signature,param_types,all_param_types)
            break
        elif inspect.isclass(attr):
            print(f"{name} is a class")
            log_file.write("Error: Classes are not supported")
            return None,"Error: Classes are not supported"

    if use_type4py:
        test_cluster.set_use_type4py(True)
    
    #calculate the parameters types and counts of the function to be tested
    test_cluster.calculate_func_params_info()

    # Return the results , empty error message 
    return test_cluster,""

def infere_types(project_path,log_file)->bool:
    """Infere the types of the function parameters and return type"""
    #send request to the server
    with open(f"{project_path}/classical/inputfunction.py") as f:
        try:
            r=requests.post("http://localhost:5001/api/predict?tc=0", f.read())
        except Exception as e:
            print("Error: Could not infer types, server is not running")
            return None,None
        
        if r.status_code == 200:
            param_types = {}
            all_param_types = {}
            response_json=r.json()
            #create a json file to store the response_json
            with open(f"{project_path}/classical/analysis/typesinfered.json", "w") as json_file:
                json.dump(response_json, json_file)
            json_file.close()
            # Extract values of 'params_p' and 'ret_type_p'
            params_p_values = response_json['response']['funcs'][0]['params_p']
            ret_type_p_values = response_json['response']['funcs'][0]['ret_type_p']
            convert_type = {
                'int': int,
                'float': float,
                'bool': bool,
                'str': str,
                'list': list,
                'tuple': tuple,
                'dict': dict,
                'set': set,
                'None': None,
                'list[int]': list[int],
                'List[int]': list[int],
                'list[float]': list[float],
                'List[float]': list[float],
                'list[bool]': list[bool],
                'List[bool]': list[bool],
                'list[str]': list[str],
                'List[str]': list[str],
                'Iterable[int]': list[int],
                'Iterable[float]': list[float],
                'Iterable[bool]': list[bool],
                'Iterable[str]': list[str],
                'Iterable':list,
                'List':list,
                'Dict':dict,
                'Tuple':tuple,
                'Set':set,
                'Set[int]':set[int],
                'Dict[int,int]':dict[int,int],
                'Dict[str,int]':dict[str,int],
                'Dict[int,str]':dict[int,str],
                'Dict[str,str]':dict[str,str],
                'NoneType':None,
                'None':None,
                None: None
            }
            # delete args and kwargs attributes from the dictionaries
            if 'args' in params_p_values:
                del params_p_values['args']
            if 'kwargs' in params_p_values:
                del params_p_values['kwargs']
            try: 
                for param_name, type_probabilities in params_p_values.items():
                # Store all types infered for current parameter
                    try:
                        all_param_types[param_name] = [convert_type[type_name] for type_name, _ in type_probabilities]
                    except Exception as e:
                        print(f"Error: Could not convert type for parameter {param_name}")
                        print(e)
                        try:
                            all_param_types[param_name] = [eval(type_name) for type_name, _ in type_probabilities]
                        except Exception as e:
                            print(f"Error: Could not convert type again for parameter {param_name}")
                            print(e)
            except Exception as e:
                print("Error: in loop for all parameters")
                print(e)
                return None,None
            try:
                # Extract the return type
                all_param_types['return'] = [convert_type[type_name] for type_name, _ in ret_type_p_values if type_name in convert_type]
            except Exception as e:
                print(f"Error: Could not convert return type infered:")
                print(e)
                try:
                    all_param_types['return'] = [eval(type_name) for type_name, _ in ret_type_p_values if type_name in convert_type]
                except Exception as e:
                    print(f"Error: Could not convert return type infered again: ")
                    print(e)
            try:
                for param_name, type_probabilities in params_p_values.items():
                    # Find type with maximum probability for current parameter
                    max_type = None
                    max_probability = 0.0

                    for type_info in type_probabilities:
                        type_name, probability = type_info
                        if probability > max_probability:
                            max_type = type_name
                            max_probability = probability

                    # Store parameter name and its corresponding max probability type
                    try:
                        param_types[param_name] = convert_type[max_type]
                    except Exception as e:
                        print(f"Error: Could not convert type for parameter {param_name}")
                        print(e)
                        try:
                            param_types[param_name] = eval(max_type)
                        except Exception as e:
                            print(f"Error: Could not convert type again for parameter {param_name}")
                            print(e)
                            return None,None
            except Exception as e:
                print("Error: in loop for parameters")
                print(e)
                return None,None
            try:
                #extract the return type
                max_type = None
                max_probability = 0.0
                for type_info in ret_type_p_values:
                    type_name, probability = type_info
                    if probability > max_probability:
                        max_type = type_name
                        max_probability = probability
            except Exception as e:
                print("Error: in loop for return type")
                print(e)
                return None,None
            # Store the return type
            try:
                param_types['return'] = convert_type[max_type]
            except Exception as e:
                print("Error: Could not convert return type infered")
                print(e)
                try:
                    param_types['return'] = eval(max_type)
                except Exception as e:
                    print("Error: Could not convert return type infered again")
                    print(e)
                    return None,None
            return param_types,all_param_types
        else:
            print("Error: response status code is not 200")
            return None,None
        