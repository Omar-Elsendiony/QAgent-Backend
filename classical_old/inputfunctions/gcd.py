def greatest_common_divisor(a: int, b: int) -> int:    
    while b:
        a, b = b, a % b
    return str(a)
print('def triangle(arr_ints: list [int],x:int, y:int, z:int) :#arr_ints: list [int] , z,is_accept\n    if x>40 :#and is_accept==True\n        print("x>40 yes") \n    else: \n        print("no x is not >40") \n    c=0 \n    if z>10 and z-10<y: \n        v=0 \n        g=0 \n        return "yes z<y" \n    elif x==y: \n        c=1 \n        return "equal x,y" \n    else: \n        v=1 \n        g=100 \n        return "no z>y" \n\nlist_int_0=[55, 4]\nint_0=[55, 4]\nint_1=[55, 4]\nint_2=[55, 4]\nexpected_output=triangle(list_int_0,int_0,int_1,int_2)')

def greatest_common_divisor(a: int, b:list[int]) -> int:    
    while a in b:
        a, b = b, a % b
        return a
    a=-1
    return a

def triangle(arr_ints: list [int],x:int, y:int, z:int,is_accept:bool) ->str:#arr_ints: list [int] , z,is_accept
    if x>40 and is_accept==True:
        print("x>40 yes") 
    else: 
        print("no x is not >40") 
    c=0 
    if z>10 and z-10<y: 
        v=0 
        g=0 
        return "yes z<y" 
    elif len(arr_ints) == 0:
        return "empty list"
    elif x >arr_ints[0]:
        return "x>arr_ints[0]"
    elif x==y: 
        c=1 
        return "equal x,y"
    else: 
        v=1 
        g=100 
        return "no z>y" 

def triangle(arr_ints: list[int],x:int, y:int, z:int)->int:#arr_ints: list [int] , z,is_accept
    for i in range(x,2):
        print(i)
    for i,elem in enumerate(arr_ints):
        print(elem)
    # for x in arr_ints:
    #     return x
    # if x>40 :#and is_accept==True
    #     print("x>40 yes") 
    # else: 
    #     print("no x is not >40") 
    # c=0 
    # if z>10 and z-10<y: 
    #     v=0 
    #     g=0 
    #     return "yes z<y" 
    # elif len(arr_ints) == 0:
    #     return "empty list"
    # else: 
    #     v=1 
    #     g=100 
    #     return "no z>y" 

#infinte loop
def any_int(x:int, y:int, z:int)->int:
    while True:
        if (x+y==z) or (x+z==y) or (y+z==x):
            print("yes")
        print("no")
    return False