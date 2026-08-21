
import sys
from prompt import get_functions, get_prompt_for_function_name
from calls import get_answer_function_name

def main():
    argv = sys.argv
    prompt = argv[1]
    functions = get_functions()
    # print(prompt)
    prompt = get_prompt_for_function_name(prompt, functions)
    print(functions)
    get_answer_function_name(prompt, functions)


    # print(test, test3)
    return

if __name__ == "__main__":
    main()