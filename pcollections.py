# Submitter: sue4(Su, Emily)

from keyword import kwlist
import re, traceback

def pnamedtuple(type_name, field_names, mutable = False,  defaults =  {}):
    def handle_arguments(type_name, field_names, defaults)->list:
        '''Checks if the arguments type_name, field_names, and defaults are legal.
        Returns f_field_names (list)'''
        def name_not_legal(name: str) -> bool:
            # name_not_legal returns True if name is not legal, False if name is legal
            legal_pattern = r'^[a-zA-Z]\w*$'
            if re.match(legal_pattern, name) is None or name in kwlist:
                return True
        
        
        class Unique:
            '''Author: Professor Pattis
            Unique decorator for iterables from ICS 33 Lecture Notes.'''
            def __init__(self, iterable):
                self._iterable = iterable
            
            def __iter__(self):
                class Unique_iter:
                    def __init__(self, iterable):
                        self._iterated = set()
                        self._iterator = iter(iterable)
                    
                    def __next__(self):
                        answer = next(self._iterator)        # StopIteration raised?
                        while answer in self._iterated:
                            answer = next(self._iterator)    # StopIteration raised?
                        self._iterated.add(answer)
                        return answer
        
                    def __iter__(self):
                        return self
        
                return Unique_iter(self._iterable)
        
        
        if type(type_name) is not str or name_not_legal(type_name): # check if legal_name is valid
            raise SyntaxError('pnamedtuple: ' + str(type_name) + ' is not a legal type name')
        
        
        if type(field_names) is str:
            # if field_names is a string of field names, convert it to a list of field names
            my_field_names = re.findall(r'[^, ]+', field_names)
        elif type(field_names) is list:
            my_field_names = field_names
        else:
            raise SyntaxError('pnamedtuple: ' + str(field_names) + ' must be a list or string')

        # check illegal field name and eliminate duplicate field name
        temp = []
        for field_name in Unique(my_field_names):
            if name_not_legal(field_name):
                raise SyntaxError('pnamedtuple: ' + field_name + ' is not a legal field name')
            else:
                temp.append(field_name)
        my_field_names = temp
        
        #check if the keys in defaults are valid
        for key_name in defaults.keys():
            if key_name not in my_field_names:
                raise SyntaxError('pnamedtuple: ' + key_name + ' is not a field name')
        
        return my_field_names
    
    
    def show_listing(s):
        for line_number, text_of_line in enumerate(s.split('\n'),1):         
            print(f' {line_number: >3} {text_of_line.rstrip()}')


    f_field_names = handle_arguments(type_name, field_names, defaults)

    # start to construct class
    class_template = 'class {type_name}:\n    _fields = {field_names}\n    _mutable = {mutable}\n'
    function_template = '\n    def {func}({parameter}):'
    class_definition = class_template.format(type_name=type_name, field_names=f_field_names, mutable=mutable)

    # def __init__()
    if len(defaults) != 0:
        param_str = 'self, '
        for field_name in f_field_names:
            if field_name in defaults.keys():
                param_str += str(field_name) + '=' + str(defaults[field_name]) + ', '
            else:
                param_str += str(field_name) + ', '
        class_definition += function_template.format(func = '__init__', parameter=param_str[:-2])
    else:
        class_definition += function_template.format(func = '__init__', parameter= 'self, ' + ', '.join(f_field_names))
        
    value_list = []
    init_arg_temp = '\n        self.{field_name} = {field_name}'
    for field_name in f_field_names:
        class_definition += init_arg_temp.format(field_name=field_name)
        value_list.append('self.' + field_name)

    val_list_template = '\n        self.value_list = [{value_list}]\n'  # ??? REMOVE IT
    class_definition += val_list_template.format(value_list=', '.join(value_list))

    # def __repr__()
    class_definition += function_template.format(func = '__repr__', parameter= 'self')
    repr_template_head = '\n        return \'{type_name}('
    class_definition += repr_template_head.format(type_name=type_name)

    repr_template_body = '{field_name}=\' + str(self.{field_name}) + \','
    for field_name in f_field_names:
        class_definition += repr_template_body.format(field_name=field_name)
    class_definition = class_definition[:-1] + ')\'\n' # remove last comma and add )'

    # def get_fields()
    getfields_template = '\n    def get_{field_name}(self):\n        return self.{field_name}\n'
    for field_name in f_field_names:
        class_definition += getfields_template.format(field_name=field_name)
    
    # def __getitem__()
    class_definition += function_template.format(func = '__getitem__', parameter= 'self, index')
    getitem_template = '''
        if type(index) is int:
            if 0 > index > len(self._fields) - 1:
                raise IndexError(\'{type_name}.__getitem__: index out of range\')
            else:
                key_str =  self._fields[index]
        elif type(index) is str:
            key_str = index
        else:
            raise IndexError(\"{type_name}.__getitem__: '{type_name}' indices must be a string or integer\")
            
        try:
            return self.__dict__[key_str]
        except:
            raise IndexError(\'{type_name}.__getitem__: ' + str(index) + ' index is not a field name\')\n'''
    class_definition += getitem_template.format(type_name=type_name)

    # def __eq__()
    class_definition += function_template.format(func = '__eq__', parameter= 'self, right')
    eq_template = '''
        if type(self) == type(right) and self.value_list == right.value_list:
            return True
        else:
            return False\n'''
    class_definition += eq_template

    # def _asdict()
    class_definition += function_template.format(func = '_asdict', parameter= 'self')
    asdict_template = '''
        return dict(zip({type_name}._fields, self.value_list))\n'''
    class_definition += asdict_template.format(type_name=type_name)

    # def _make()
    class_definition += function_template.format(func = '_make', parameter= 'iterable')
    make_template = '''
        iter_list = list(iterable)
        if len(iter_list) != len({type_name}._fields):
            raise TypeError('{type_name}._make(): takes 1 positional argument, but ' + str(len(iter_list)) + ' were given')
        elif len(iter_list) > 0:
            {args} = iter_list
        return {type_name}({args})\n'''
    class_definition += make_template.format(type_name=type_name, args = ', '.join(f_field_names))

    # def _replace()
    class_definition += function_template.format(func = '_replace', parameter= 'self, **kargs')
    replace_template = '''
        if len(kargs) > len({type_name}._fields):
            raise TypeError('{type_name}._replace: expected at most ' + str(len({type_name}._fields)) + ' arguments, got ' + str(len(kargs)))
            
        for k, v in kargs.items():
            if k not in {type_name}._fields:
                raise TypeError('{type_name}._replace: field name, ' + str(k) + ', does not exist')
        
        if {type_name}._mutable:
            for k, v in kargs.items():
                indx = {type_name}._fields.index(k)
                self.value_list[indx] = v
            {args} = self.value_list
            self = {type_name}({args}) 
            return            
        else:
            value_copy = self.value_list.copy()
            for k, v in kargs.items():
                indx = {type_name}._fields.index(k)
                value_copy[indx] = v
            {args} = value_copy
            return {type_name}({args})\n''' 
    class_definition += replace_template.format(type_name=type_name, args = ', '.join(f_field_names))

    # def __setattr__()
    class_definition += function_template.format(func='__setattr__', parameter='self, name, value')
    setattr_template = '''
            if 'value_list' not in self.__dict__:
                if name in [{args}, 'value_list']:
                    if name not in self.__dict__:
                        self.__dict__[name] = value
                else:
                    raise AttributeError("{type_name}.__setattr__: '{type_name}' object has no attribute " + str(name))

            else:
                if self._mutable:
                    self.__dict__[name] = value
                    self.value_list[{type_name}._fields.index(name)] = value
                else:
                    raise AttributeError("{type_name}.__setattr__: '{type_name}' object is immutable")'''
    class_definition += setattr_template.format(type_name=type_name,
                                                args=', '.join(['\'' + field_name + '\'' for field_name in f_field_names]))
    # bind class_definition (used below) to the string constructed for the class
    
    # Debugging aid: uncomment next call to show_listing to display source code
    show_listing(class_definition)
    
    # Execute str in class_definition in name_space; then bind the attribute
    #   source_code to the class_definition str; finally, return the class
    #   object created; any syntax errors will print a listing of the
    #   of class_definition and trace the error (see the except clause).
    name_space = dict( __name__ = f'pnamedtuple_{type_name}' )                  
    try:
        exec(class_definition,name_space)
        name_space[type_name].source_code = class_definition
    except (TypeError,SyntaxError):                      
        show_listing(class_definition)
        traceback.print_exc()
    return name_space[type_name]

    
if __name__ == '__main__':
    #Simple tests
    print('Point Class')
    Point = pnamedtuple('Point', 'x  y')
    p = Point(0,0)
    
    print('\n\nTriple1 Class')
    Triple1 = pnamedtuple('Triple1', ['a', 'b', 'c'],defaults={'c':2})
    t1 = Triple1(1,2,4)
    
    # #driver tests
    # import driver
    # driver.default_file_name = 'bscp3W22.txt'
    # driver.default_show_exception_message = True
    # driver.default_show_traceback = True
    # driver.driver()
