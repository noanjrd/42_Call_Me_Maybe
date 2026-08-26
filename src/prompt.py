import json
from Function import Function
from model import llm

def get_functions():
    functions_list = []
    with open("data/input/functions_definition.json", "r", encoding="utf-8") as f:
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
    print(prompt)
    return prompt

def get_prompt_for_parameters(input: str, function: Function) -> str:
    prompt = f"Function name: {function.name}\n"
    prompt += f"Function description: {function.description}\n\n"

    prompt += "Function parameters:\n"

    for name, type_f in function.parameters.items():
        prompt += f"- {name}: {type_f}"
        
        
        prompt += "\n"

    prompt += "\n"
    prompt += f"User request : {input}\n\n"
    prompt += "Extract the values for the function parameters from the user request and "
    prompt += "return them using a dictionnary object."
    print(prompt)
    return prompt

