from .prompt import get_functions, get_prompt_for_function_name, get_prompt_for_parameters
from .calls.function_name import get_answer_function_name
from .calls.function_parameters import get_answer_parameters
from .arguments import parse_args
import json
from pathlib import Path


def export_json(path, output):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=4)
    return


def start_generating_answer(question, available_functions):
    prompt = get_prompt_for_function_name(question, available_functions)
    function_name = get_answer_function_name(prompt, available_functions)
    f = [function for function in available_functions
         if function.name == function_name]
    prompt = get_prompt_for_parameters(question, f[0])
    answer = get_answer_parameters(prompt, f[0])
    output_parameters = json.loads(answer)
    try:
        output = {"prompt": question, "name": function_name,
                  "parameters": output_parameters}
        return output
    except Exception:
        return None


def open_prompts(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def main():
    try:
        args = parse_args()
        available_functions = get_functions(args.functions_definition)

        prompts = open_prompts(args.input)
        output_file = []
        for prompt in prompts:
            answer = (start_generating_answer(prompt['prompt'],
                                              available_functions))
            if answer:
                output_file.append(answer)

        export_json(args.output, output_file)
        return
    except KeyboardInterrupt:
        print("Program interrupted")
        exit(1)
    except FileNotFoundError as e:
        print("Error file not found:", e)


if __name__ == "__main__":
    main()
