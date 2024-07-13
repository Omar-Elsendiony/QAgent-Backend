import random
import string
import ast
import astunparse
import os

# def generate_str_value():
#     example_strings = ["hello", "world", "foo", "bar", "python", "example","hi","aba","level","exam",""]
#     rand_str= ''.join(random.choices(string.ascii_uppercase+ string.ascii_lowercase + string.digits, k = random.randint(0, 7)))
#     rand_value=random.choice(example_strings+[rand_str])
#     return rand_value
# print(generate_str_value())
# print(generate_str_value())

# print("""def count_up_to(n):\n        primes = []\n    for i in range(2, n):\n        is_prime = True\n        for j in range(2, i):\n            if i % j == 0:\n                is_prime = False\n                break\n        if is_prime:\n            primes.append(i)\n    return primes""")
# print("    \n    if isinstance(x,int) and isinstance(y,int) and isinstance(z,int):\n        if (x+y==z) or (x+z==y) or (y+z==x):\n            return True\n        return False\n    return False\n")
code="""def check(choose_num):\n    if x > y:\n        return -1\n    if y % 2 == 0:\n        return y\n    if x == y:\n        return -1\n    return y - 1\n"""
# convert code to ast
code="def check(numbers:list[int],threshold:int):\n    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n\n    return False\n"
ccc="""def check(choose_num):
    if x > y:
        return -1
    if y % 2 == 0:
        return y
    if x == y:
        return -1
    return y - 1"""

code ="""def largest_smallest_integers(lst: list[int])->tuple:
    smallest = list(filter(lambda x: x < 0, lst))
    largest = list(filter(lambda x: x > 0, lst))
    ret_largest=None
    ret_smallest=None
    if smallest!=[]:
        ret_largest=max(smallest) 
    else:
        ret_largest=None
    if largest!=[]:
        ret_smallest=min(largest) 
    else:
        ret_smallest=None
    
    return (ret_largest, ret_smallest)"""

code_ast = ast.parse(code)
#print ast
print(astunparse.dump(code_ast))
print(code)
print(os.getcwd())

