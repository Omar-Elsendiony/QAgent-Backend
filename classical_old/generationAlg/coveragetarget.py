"""A class to represent a coverage target"""
import sys
class CoverageTarget:
    """class to represent a coverage target.
    N.B: each branch has two targets (True and False) that are represented by the same line.
         we diffrentiate them using the target_type attribute."""
    
    def __init__(self):
        self.target_string = ""
        self.id = 0
        self.line_number = 0
        self.locals_dict = dict()
        self.target_type=None #will be assigned to "True" for an instance and "False" for another instance(the same branch)
        self.is_covered = False
        self.branch_distance=sys.maxsize