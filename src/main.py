import sys
from prompt import get_functions, get_prompt_for_function_name, get_prompt_for_parameters
from calls import get_answer_function_name
from parameters import get_answer_parameters
import json
from pathlib import Path
from arguments import parse_args

def export_json(path, output):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=4)
    return

def start_generating_answer(question, available_functions):
    # print(prompt)
    prompt = get_prompt_for_function_name(question, available_functions)
    # print(functions)
    function_name = get_answer_function_name(prompt, available_functions)
    f = [function for function in available_functions if function.name == function_name]
    prompt = get_prompt_for_parameters(question, f[0])
    answer = get_answer_parameters(prompt, f[0])
    output_parameters = json.loads(answer)
    output = {"prompt": question, "name": function_name, "parameters": output_parameters}
    return output


def open_prompts(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def main():
    argv = sys.argv
    args = parse_args()
    available_functions = get_functions(args.functions_definition)
    # start_generating_answer(prompt, available_functions)

    prompts = open_prompts(args.input)
    # print(prompts)
    output_file = []
    # if len(argv) > 1:
    #     prompts = [{"prompt": argv[1]}]
    for prompt in prompts:
        output_file.append(start_generating_answer(prompt['prompt'], available_functions))
    export_json(args.output, output_file)
    return

if __name__ == "__main__":
    main()