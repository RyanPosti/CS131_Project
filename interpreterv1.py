from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        #Intialize dictionary to contain variables and their values
        self.variable_name_to_value={}

    def run(self,program):

        #Use the parser to get the AST
        ast=parse_program(program)

        #USe recurssion to traverse ast
        functions=ast.get("functions")

        main_function=None
        for function in functions:
            func_name = function.get("name")

            #Make sure that there is a  main function 
            if func_name == "main":
                    main_function = function
                    break
        #If there is no main function Error
        if not main_function:
            self.error(ErrorType.NAME_ERROR, "No main() function was found")

        #Execute main
        self.run_func(main_function)
    

    def run_func(self,function):
        #Assign statements using the get function provided
        statements = function.get("statements")
        #Run every statement that was found
        for statements in statements:
            self.run_statement(statements)
    
    def run_statement(self,statement):
        #If the statement is a variable defintion then use run_vardef func
        if statement.elem_type == "vardef":
            self.run_vardef(statement)
        #Else if the statement is an assignment use the do_assignment function
        elif statement.elem_type == "=":
            self.do_assignment(statement)
        #Else if the statement is a function call use the fcall_func
        elif statement.elem_type == "fcall":
            self.run_fcall(statement)
        #Else error because trying to run an unexpected statement
        else:
            self.error(ErrorType.TYPE_ERROR)
    
    def run_vardef(self,statement):
        var_name = statement.get("name")
        #If a variable with this name has already been assigned error
        if var_name in self.variable_name_to_value:
            self.error(ErrorType.NAME_ERROR,f"Variable {var_name} defined more than once")
        #Set the key of the dictionary entry to the variable name
        self.variable_name_to_value[var_name]=None
    
    def do_assignment(self,statement):
        var_name = statement.get("name")
        expr = statement.get("expression")
        #Obtain the value of the expression by using the evaluate_expression func
        value = self.evaluate_expression(expr)
        #Error if trying to assign to a variable that was not previously defined
        if var_name not in self.variable_name_to_value:
            self.error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")
        #Set the value to the corresponding variable name
        self.variable_name_to_value[var_name]=value

    def evaluate_expression(self, expression):
        #If the expression is an int return the value of that int
        if expression.elem_type == "int":
            return expression.get("val")
        elif expression.elem_type == "string":
            return expression.get("val")
        #Else if the expression is another variable attempt to return the value of that variable
        elif expression.elem_type == "var":
            var_name = expression.get("name")
            if var_name not in self.variable_name_to_value:
                self.error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")
            return self.variable_name_to_value[var_name]
        #Else if the expression is an addition or subtraction attempt to find the value of the operation
        elif expression.elem_type in ["+", "-"]:
            op1 = self.evaluate_expression(expression.get("op1"))
            op2 = self.evaluate_expression(expression.get("op2"))
            #If both numbers aren't ints error
            if type(op1) == type(op2)==int:
                if expression.elem_type == "+":
                    return op1 + op2
                elif expression.elem_type == "-":
                    return op1 - op2
            else:
                self.error(ErrorType.TYPE_ERROR, "Incompatible types for specified operations")
        #Else if the expression is a function call run it
        elif expression.elem_type == "fcall":
            return self.run_fcall(expression)
        #Else error
        else:
            self.error(ErrorType.TYPE_ERROR, f"{expression.elem_type} is an unsupported expression type")
    
    def run_fcall(self, statement):
        func_name = statement.get("name")
        #If the function is a print function get the arguments in print and use output to print them
        if func_name == "print":
            args = statement.get("args")
            output = ""
            for arg in args:
                value = self.evaluate_expression(arg)
                output += str(value)
            self.output(output)
        #Next 8 lines were made with the help of ChatGPT 
        # and it's suppossed to print the prompt (if there is one) and get user input
        elif func_name == "inputi":
            args = statement.get("args")
            if len(args) > 1:
                self.error(ErrorType.NAME_ERROR, f"No inputi() function found that takes > 1 parameter")
            elif len(args) == 1:
                prompt=self.evaluate_expression(args[0])
                self.output(prompt)
            user_input = int(self.get_input())
            return user_input
        #If the function hasn't been defined error
        else:
            self.error(ErrorType.NAME_ERROR, f"Function {func_name} has not been defined")





    