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
    prompt+=f"Select the single function best suited to answer : {input}"
    # prompt += f"User's question: {input}\n"
    return prompt
