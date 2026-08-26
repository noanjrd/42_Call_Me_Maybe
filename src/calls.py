from llm_sdk import Small_LLM_Model
from Function import Function
from model import llm

def get_next_logit_for_function_name(encoded_prompt, lap,  candidates):
    logits_list = llm.get_logits_from_input_ids(encoded_prompt)

    valid_candidates = [c for c in candidates if len(c) >= lap+1]
    allowed_tokens = [candidate[lap] for candidate in valid_candidates]
    allowed_legits = [logit for token, logit in enumerate(logits_list) if token in allowed_tokens]
    # print("cand:", valid_candidates,"tokens:", allowed_tokens, "legits:", allowed_legits)
    if len(allowed_legits) == 0:
        return None
    max_logit = max(allowed_legits)
    next_token = logits_list.index(max_logit)
    return next_token


def get_answer_function_name(prompt, functions:list[Function]):
    encoded_prompt = llm.encode(prompt)[0].tolist()

    candidates = []
    for function in functions:
        candidates.append(function.tokenized_name)
    # print(functions_tokens)
    answer = []
    lap = 0

    while lap < 30:
        next_token = get_next_logit_for_function_name(encoded_prompt, lap, candidates)
        if next_token == None:
            break
        # print(test3)

        word = llm.decode(next_token)
        answer.append(word)
        print(word)
        if "()" in word:
            break
        encoded_prompt.append(next_token)
        new_candidates = []
        for c in candidates:
            if len(c) > lap and c[lap] == next_token:
                new_candidates.append(c)
        candidates = new_candidates
        lap+=1
        print(candidates)
    print("".join(answer))
    return "".join(answer)
