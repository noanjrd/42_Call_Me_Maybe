from Function import Function
from pydantic import BaseModel
from model import llm

type_constraints = {

}

class Parameters(BaseModel):
    encoded_prompt: list[int]
    keys_encoded: list[list[int]]
    types: list[str]
    lap: int
    current_parameter_index: int
    index_key_token:int
    predicting_value: bool
    current_value: str


def string(past_values, value):
    word = past_values + llm.decode(value)
    if len(word) == 0 or word[0] != '"':
        return False
    return True




def get_next_logit_for_function_parameters(p: Parameters):
    logits_list = llm.get_logits_from_input_ids(p.encoded_prompt)
    # print(logits_list)
    allowed_legits = None
    if p.predicting_value == False:
        allowed_legits = [logit for index, logit in enumerate(logits_list) if index == p.keys_encoded[p.current_parameter_index][p.index_key_token]]
    else:
        if p.types[p.current_parameter_index] == "string":
            allowed_legits = [logit for index, logit in enumerate(logits_list) if string(p.current_value, index) is True]
        else:
            allowed_legits = logits_list
    if len(allowed_legits) == 0:
        return None
    max_logit = max(allowed_legits)
    next_token = logits_list.index(max_logit)
    return next_token



def get_answer_parameters(prompt, function: Function):
    encoded_prompt = llm.encode(prompt)[0].tolist()

    answer = []
    names = [ '"' + key + '": ' for key, _ in function.parameters.items()]
    names[0] = '{' + names[0]
    keys_encoded = [llm.encode(name).tolist()[0] for name in names]
    types = [value for _, value in function.parameters.items()]
    print(names, keys_encoded, types)

    print("number parameters", function.number_parameters)
    p = Parameters(
        encoded_prompt=encoded_prompt,
        keys_encoded=keys_encoded,
        types=types,
        lap=0,
        current_parameter_index=0,
        index_key_token=0,
        predicting_value=False,
        current_value="")

    while True:
        next_token = get_next_logit_for_function_parameters(p)
        if next_token == None:
            break
        if p.predicting_value == False:
            p.index_key_token += 1
        if p.predicting_value == False and  p.index_key_token >= len(p.keys_encoded[p.current_parameter_index])- 1:
            p.index_key_token = 0
            p.predicting_value = True
            p.current_value = ""
        word = llm.decode(next_token)
        p.current_value += word
        answer.append(word)
        print(word)
        if "," in word:
            if p.current_parameter_index >= len(p.keys_encoded)-1:
                answer[-1] = answer[-1].replace(',', '}')
                print("here")
                break
            p.predicting_value = False
            p.current_parameter_index +=1
            p.current_value = ""
        p.encoded_prompt.append(next_token)
        if '}' in word:
            break
        p.lap+=1


    print("\nfinished\n")
    print("".join(answer))
    return "".join(answer)

