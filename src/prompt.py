import json
from pathlib import Path
from .Function import Function
from .model import llm


def get_functions(path: str | Path) -> list[Function]:
    functions_list = []
    with open(path, "r", encoding="utf-8") as f:
        functions_json = json.load(f)
    for function in functions_json:
        tokens = llm.encode(function['name']).tolist()[0]
        parameters = {key: value["type"] for key, value in
                      function["parameters"].items()}
        new_function = Function(
            name=function["name"],
            tokenized_name=tokens,
            description=function["description"],
            parameters=parameters,
            return_type=function["returns"],
            number_parameters=len(function['parameters'])
        )
        functions_list.append(new_function)
    return functions_list


def get_prompt_for_function_name(
    input: str, functions: list[Function]
) -> str:
    prompt = ""
    prompt = (
        "Choose the single best function for the user request.\n"
        f"User request: {input}\n\n"
        "Available functions:\n"
    )
    for function in functions:
        prompt += function.get_name_description() + "\n"
    prompt += "\nReturn only one exact function name from the list.\n"
    prompt += "Selected function:"
    return prompt


def get_prompt_for_parameters(input: str, function: Function) -> str:
    schema = ", ".join(
        f'"{name}": <{type_f} value>'
        for name, type_f in function.parameters.items()
    )

    prompt = f"Function name: {function.name}\n"
    prompt += f"Function description: {function.description}\n\n"
    prompt += "Required parameters:\n"
    for name, type_f in function.parameters.items():
        prompt += f"- {name} ({type_f})\n"

    prompt += f"\nUser request: {input}\n\n"
    prompt += "Extract each parameter value directly from the user request.\n"
    prompt += "Infer values that are clearly implied by the request.\n"

    if "regex" in function.parameters:
        prompt += (
            "REGEX GENERATION RULES\n"
            "When a regex is required, you must provide "
            "ONLY the pattern using this strict syntax:\n"
            "- To match numbers/digits: [0-9]+\n"
            "- To match vowels: ([aeiouAEIOU])\n"
            "- To match a complete word, use word boundaries: "
            "'\bcat\b' matches only the word cat, "
            "not catalog or copycat.\n"
            "CRITICAL: Never use '.*' or broad wildcards. "
            "Be as specific as possible.\n"
        )

    prompt += (
        "\nReturn only one JSON object, "
        "without an explanation or Markdown.\n"
        f"Use exactly this structure: {{{schema}}}\n\n"
        "JSON:\n"
    )
    print(prompt)
    return prompt
