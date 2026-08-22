import json
from Function import Function
from llm_sdk import Small_LLM_Model

llm = Small_LLM_Model()

def get_functions():
    functions_list = []
    with open("data/input/functions_definition.json", "r", encoding="utf-8") as f:
        functions_json = json.load(f)
    for function in functions_json:
        tokens = llm.encode(function['name']).tolist()[0]
        # print(tokens)
        new_function = Function(
            name=function["name"],
            tokenized_name=tokens,
            description=function["description"],
            parameters=function["parameters"],
            return_type=function["returns"],
        )
        functions_list.append(new_function)
    return functions_list
    
def get_prompt_for_function_name(input, functions: list[Function]):
    prompt=""
    prompt+="Available functions:\n"
    for function in functions:
        prompt+=function.get_name_description() + "\n"
    # prompt += f"User's question: {input}\n"
    prompt+=f"Select the single function best suited to answer: {input}"
    return prompt

def get_prompt_for_parameters(input: str, function: Function) -> str:
    prompt = f"Function name: {function.name}\n"
    prompt += f"Description: {function.description}\n\n"

    prompt += "Parameters:\n"

    for name, info in function.parameters.items():
        prompt += f"- {name}: {info['type']}"
        
        
        prompt += "\n"

    prompt += "\n"
    prompt += f"User request: {input}\n\n"
    prompt += "Extract the values for the function parameters from the user request.\n"
    # prompt += "Return only a JSON object containing the parameter names and their values."
    print(prompt)
    return prompt