class FunctionCallable:
    """A function callable object"""
    def __init__(self, func_name, returnType, function_signature, lines_num):
        self.name = func_name
        self.returnType = returnType
        self.signature = function_signature
        self.lines_num = lines_num
class ClassCallable:
    """A class callable object"""
    def __init__(self, ):
        self.name = ""
        self.methods = []
class GenericCallable:
    """A generic callable object"""
    def __init__(self, ):
        self.functions = []