import astunparse
import ast
from numpy import generic
from sympy import I
import copy

class CodeMutator(ast.NodeVisitor):

    def __init__(self):
        self.parents = []
        self.indices = []
        self.target_line_no = None

    def store_parent(self, index, parent):
        self.parents.append(parent)
        self.indices.append(index)

    def set_line_no(self, linenumbers):
        self.target_line_numbers = linenumbers

    @property
    def get_indices(self):
        return self.indices

    @property
    def get_parents(self):
        return self.parents

    def visit_If(self, node):
        x = node.parent
        # new_node = ast.parse("print('hello')")
        if (node.lineno in self.target_line_numbers):
            for i, nodeParent in enumerate(node.parent.body):
                # node.parent.body
                if (nodeParent is node):
                    # print("OK")
                    self.store_parent(i, node.parent)

                    # x.append(new_node)
                    # node._fields = node._fields + ("test",)
                    # setattr(node, "body", x)
                    # node.parent.body.insert(i - 1, ast.parse("print('hello')"))

            # print(node)
        return self.generic_visit(node)

    def visit_For(self, node):
        x = node.parent
        if (node.lineno in self.target_line_numbers):
            for i, nodeParent in enumerate(node.parent.body):
                if (nodeParent is node):
                    self.store_parent(i, node.parent)
        return self.generic_visit(node)
    
    def visit_While(self, node):
        x = node.parent
        if (node.lineno in self.target_line_numbers):
            for i, nodeParent in enumerate(node.parent.body):
                if (nodeParent is node):
                    self.store_parent(i, node.parent)
        return self.generic_visit(node)
        
def parentify(tree):
    tree.parent = None
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
def insert_print_locals_using_ast(code,indices,project_path,new_node_create_file,new_node):  
    code_ast = ast.parse(code)
    parentify(code_ast)
    mutator = CodeMutator()
    mutator.set_line_no(indices)
    mutator.visit(code_ast)
    code_ast_old=copy.deepcopy(code_ast)
    ##############################################################
#     create_file=f"""from inspect import currentframe, getframeinfo
# JSONFile='{project_path}classical/fitness/localsdictionary.txt'
# with open(JSONFile, 'w') as anotate_f:
#     anotate_f.write('')"""
#     write_file="""with open(JSONFile, 'a') as anotate_f:
#     frameinfo = getframeinfo(currentframe())
#     locals()['aha'] = (frameinfo.lineno)
#     anotate_f.write(str(locals()))
#     anotate_f.write('\\n')"""
#     new_node_create_file=ast.parse(create_file)
#     new_node = ast.parse(write_file)
    # mutator.parent.body.insert(mutator.index, new_node)
    # print(mutator.parent.body)
    #print(astunparse.to_source(code_ast))
    
    #dumped = astunparse.dump(code_ast)
    #print(dumped)
    for i, parent in enumerate(mutator.get_parents):
        parent.body.insert(mutator.get_indices[i], new_node.body[0])
        ast.fix_missing_locations(code_ast)
        # break
    for parent in ast.walk(code_ast):
        # print(parent)
        if isinstance(parent,ast.FunctionDef):
            parent.body.insert(0, new_node_create_file.body)
            break
    ast.fix_missing_locations(code_ast)
    #print(ast.unparse(code_ast))
    return ast.unparse(code_ast)

def insert_print_locals_lineno_using_ast(code,indices,project_path):
    old_create_file=f"""
JSONFile='{project_path}/classical/fitness/localsfiles/localsdictionary.txt'
with open(JSONFile, 'w') as anotate_f:
    anotate_f.write('')"""
    old_write_file="""with open(JSONFile, 'a') as anotate_f:
    anotate_f.write(str(locals()))
    anotate_f.write('\\n')"""
    new_node_create_file_old=ast.parse(old_create_file)
    new_node_old = ast.parse(old_write_file)
    code_print_locals1=insert_print_locals_using_ast(code,indices,project_path,new_node_create_file_old,new_node_old)
    
    create_file=f"""from inspect import currentframe, getframeinfo
JSONFile='{project_path}/classical/fitness/localsfiles/localslineno.txt'
with open(JSONFile, 'w') as anotate_f:
    anotate_f.write('')"""
    write_file="""with open(JSONFile, 'a') as anotate_f:
    frameinfo = getframeinfo(currentframe())
    locals()['aha'] = (frameinfo.lineno)
    anotate_f.write(str(locals()))
    anotate_f.write('\\n')"""
    new_node_create_file=ast.parse(create_file)
    new_node = ast.parse(write_file)  
    code_print_locals2=insert_print_locals_using_ast(code,indices,project_path,new_node_create_file,new_node)
    return code_print_locals1,code_print_locals2