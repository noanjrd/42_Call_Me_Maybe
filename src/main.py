import sys
from prompt import get_functions, get_prompt_for_function_name, get_prompt_for_parameters
from calls import get_answer_function_name
from parameters import get_answer_parameters



def main():
    argv = sys.argv
    question = argv[1]
    functions = get_functions()
    # print(prompt)
    prompt = get_prompt_for_function_name(question, functions)
    # print(functions)
    function_name = get_answer_function_name(prompt, functions)
    f = [function for function in functions if function.name == function_name]
    prompt = get_prompt_for_parameters(question, f[0])
    get_answer_parameters(prompt, f[0])
    


    # print(test, test3)
    return

if __name__ == "__main__":
    main()