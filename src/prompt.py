import json
from Function import Function
from model import llm
import argparse


def get_functions(path: str):
    functions_list = []
    with open(path, "r", encoding="utf-8") as f:
        functions_json = json.load(f)
    for function in functions_json:
        tokens = llm.encode(function['name']).tolist()[0]
        # print(tokens)
        parameters = {key:value["type"] for key,value in function["parameters"].items()}
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




def get_prompt_for_function_name(input, functions: list[Function]):
    prompt=""
    prompt+=f'Select the single best function to answer : {input}\n'
    prompt+="Available functions:\n"
    for function in functions:
        prompt+=function.get_name_description() + "\n"
    # prompt += f"User's question: {input}\n"
    # print(prompt)
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
        prompt += """
Regex rules:
- Return only the regex pattern: no /.../ delimiters, explanation, or surrounding text.
- Match exactly the text that the user wants replaced. Prefer the simplest correct pattern.
- Do not use parentheses/capture groups unless a captured group is explicitly needed. For vowels, use [AEIOUaeiou], not ([AEIOUaeiou]).
- Use regex syntax when appropriate: numbers -> \\d+, whitespace -> \\s+, and one or more repetitions -> +.
- Escape literal regex metacharacters: a literal period is \\.; a literal plus is \\+.
- To match a complete word, use word boundaries: \\bcat\\b matches the whole word cat.

JSON escaping is required:
- The answer is JSON, so every regex backslash must be written as two backslashes in the JSON value.
- Correct JSON values: digits is "\\\\d+"; whole-word cat is "\\\\bcat\\\\b".
- Never use "\\bcat\\b" with one backslash in a JSON value: JSON treats \\b as a backspace escape, not a regex word boundary.

Exact examples:
- Replace all numbers: "regex": "\\\\d+"
- Replace all vowels: "regex": "[AEIOUaeiou]"
- Replace the whole word cat: "regex": "\\\\bcat\\\\b"
- Replace a literal period: "regex": "\\\\."
"""

    prompt += "Do not use placeholders such as 'description', 'string', or 'value'.\n"
    prompt += "Return only one JSON object, without an explanation or Markdown.\n"
    prompt += f"Use exactly this structure: {{{schema}}}\n\n"
    prompt += "JSON:\n"
    print(prompt)
    return prompt
