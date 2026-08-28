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
        prompt += "\nRegex parameter rules:\n"
        prompt += "- Write only the regex pattern, without /.../ delimiters or surrounding commentary.\n"
        prompt += "- Make the pattern match exactly the text the user wants replaced.\n"
        prompt += "- Translate descriptions into regex syntax: digits/numbers -> \\d+, whitespace -> \\s+, and vowels -> [AEIOUaeiou].\n"
        prompt += "- Use character classes, quantifiers, groups, alternation, anchors, and word boundaries when needed.\n"
        prompt += "- Escape regex metacharacters when the user means them literally (for example, \\. matches a literal period).\n"
        # prompt += "- The regex is a JSON string, not a Python string literal. Escape every backslash for JSON: write \\\\d+ for the regex \\d+, and \\\\bcat\\\\b for \\bcat\\b.\n"
        prompt += "- Prefer the simplest pattern that satisfies the request; do not add capture groups or anchors unless required.\n"
        prompt += """
Regex examples:
- "all numbers" -> "\\\\d+"
- "all vowels" -> "[AEIOUaeiou]"
- "the whole word cat" -> "\\\\bcat\\\\b"
- "asterisks" as a replacement -> "*"
The regex field must contain a regex pattern, not a description or a plain list of characters.
"""

    prompt += "Do not use placeholders such as 'description', 'string', or 'value'.\n"
    prompt += "Return only one JSON object, without an explanation or Markdown.\n"
    prompt += f"Use exactly this structure: {{{schema}}}\n\n"
    prompt += "JSON:\n"
    # print(prompt)
    return prompt
