def some_nested_conditions(x: int, y: int, z: float,x_must_be_greater:bool) :
    if x>40:
        print("x>40 yes") 
        if x_must_be_greater:
            if x>y and x>z:
                return "x is the gratest"
            else:
                return "x is not the gratest"
        return "x must not be greater "
    else: 
        return "no x is not >40" 
    