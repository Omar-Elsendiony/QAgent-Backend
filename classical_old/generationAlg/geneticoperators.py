""" All genetic operators functions"""
import random 
import string

def edit_string(string_value):
    """edits a string with 3 probabilities, 1 add new character,2 delete an existing character,3 edit an existing character"""
    random_new_char=random.choice(string.ascii_uppercase+ string.ascii_lowercase + string.digits + ' ' + '[]()<>?!#@%^&*_+')
    choice=random.choice([1,2,3])
    if len(string_value)!=0:  
        rand_index=random.randint(0, len(string_value)-1)
        if choice==1:#add new character
            string_value=string_value[:rand_index]+random_new_char+string_value[rand_index:]
        elif choice==2:#delete an existing character
            string_value=string_value[:rand_index]+string_value[rand_index+1:]
        elif choice==3:#edit an existing character
            try:
                if random.random()<0.5:
                    edited_char=chr(ord(string_value[rand_index])+1)
                else:
                    edited_char=chr(ord(string_value[rand_index])-1)
            except:
                edited_char=random.choice(string.ascii_uppercase+ string.ascii_lowercase + string.digits + string.punctuation + ' ')
            string_value=string_value[:rand_index]+edited_char+string_value[rand_index+1:]
    else:#if the string is empty, add a new character
        string_value+=random_new_char
    return string_value
def edit_list(type, list_value, min_rand_val, max_rand_val, power_of_quantity_of_change):
    """edits a list with 3 probabilities, 1 add new element,2 delete an existing element,3 edit an element"""
    choice=random.choice([1,2,3])
    rand_value=random.randint(min_rand_val, max_rand_val)
    if len(list_value)!=0:  
        rand_index=random.randint(0, len(list_value)-1)
        if choice==1:
            random_new_element=rand_value
            list_value.insert(rand_index,random_new_element)
        elif choice==2:
            list_value.pop(rand_index)
        elif choice==3:
            if random.random()<0.5:
                list_value[rand_index]+=int(rand_value*random.random()**power_of_quantity_of_change)
            else:
                list_value[rand_index]-=int(rand_value*random.random()**power_of_quantity_of_change)
    return list_value