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
    if len(word) == 0:
        return False
    if not past_values:
          return word.lstrip().startswith('"')
    return True

def number(past_values, value):
    word = past_values + llm.decode(value)
    word = word.lstrip()
    if not word:
        return False
    status = "START"
    # print("WORD:", repr(word), "FIRST:", repr(word[0]))
    while status != "END":
        if status == "START":
            if word[0].isdigit():
                status="BEFORE_POINT"
            elif word[0] in "+-":
                status = "BEFORE_POINT"
                word = word[1:]
            else:
                return False
        if status == "BEFORE_POINT":
            if all(letter in "0123456789" for letter in word):
                status="END"
                continue
            for index in range(len(word)):
                if word[index] == '.':
                    word = word[index+1:]
                    status = "AFTER_POINT"
                    break
                if word[index] == ',' or word[index] == ' ' or word[index] == '}':
                    word = word[index+1:]
                    status = "AFTER_COMMA_SPACE"
                    break
            else: 
                return False
        if status == "AFTER_POINT":
            if all(letter in "0123456789" for letter in word):
                status = "END"
                continue
            for index in range(len(word)):
                if word[index] == ',' or word[index] == ' ':
                    word = word[index+1:]
                    status = "AFTER_COMMA_SPACE"
                    break
            else: return False
        if status == "AFTER_COMMA_SPACE":
            if all(letter is ' ' for letter in word) or len(word) == 0:
                status = "END"
                continue
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
        elif p.types[p.current_parameter_index] == "number":
            allowed_legits = [logit for index, logit in enumerate(logits_list) if number(p.current_value, index) is True]
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
    names = [ '"' + key + '":' for key, _ in function.parameters.items()]
    names[0] = '{' + names[0]
    keys_encoded = [llm.encode(name).tolist()[0] for name in names]
    types = [value for _, value in function.parameters.items()]
    # print(names, keys_encoded, types)

    # print("number parameters", function.number_parameters)
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
        word = llm.decode(next_token)
        if p.predicting_value and not p.current_value and word[0] != ' ':
            word = " " + word
        answer.append(word)
        print(word)
        p.current_value += word
        if p.predicting_value == False:
            p.index_key_token += 1
        if p.predicting_value == False and  p.index_key_token >= len(p.keys_encoded[p.current_parameter_index]):
            p.index_key_token = 0
            p.predicting_value = True
            p.current_value = ""

        comma_or_space = types[p.current_parameter_index] == "number"
        for char in word:
            if types[p.current_parameter_index] == "string" and char =='"':
                comma_or_space = True
                continue
            if comma_or_space and  char is ",":
                if p.current_parameter_index >= len(p.keys_encoded)-1:
                    answer[-1] = answer[-1].replace(',', '}')
                    word = word.replace(',', '}')
                    print("here")
                    break
                p.predicting_value = False
                p.current_parameter_index +=1
                p.current_value = ""
                break
        p.encoded_prompt.append(next_token)
        if '}' in word:
            break
        p.lap+=1


    print("\nfinished\n")
    # print("".join(answer))
    return "".join(answer)

