import builtins
from typing import List,Tuple
import typing

print(eval('Tuple[int,int]'))
print(Tuple[int,int]==eval('Tuple[int,int]'))
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
                    }
print(convert_type['List[int]'])