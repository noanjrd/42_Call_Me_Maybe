# 42_Call_Me_Maybe

Function calling from scratch with a small local LLM, using constrained
(grammar-guided) token generation instead of relying on a provider's
built-in "tool calling" + structured-output feature.

Given a list of available functions (name, description, parameters, return
type) and a natural-language prompt, the program:

1. Picks the single best-matching function.
2. Generates a JSON object with the arguments for that function, extracted
   from the prompt.

Both steps are done by generating the model's output **one token at a
time** and, at every step, restricting the next token to only the ones that
are still valid. The function name has to match one of the candidate
function names, and each parameter value has to keep matching its declared
type (`number`, `string`, `bool`) as it's generated. This avoids the model
returning malformed JSON, an unknown function name, or values of the wrong
type.

## How it works

```
prompt.json ──▶ get_prompt_for_function_name ──▶ constrained decoding ──▶ function name
                                                   (only tokens that keep
                                                   matching a known name
                                                   are allowed)

function name ─▶ get_prompt_for_parameters ────▶ constrained decoding ──▶ JSON arguments
                                                   (keys forced from the
                                                   schema, values validated
                                                   token-by-token against
                                                   their declared type)
```

- **Function selection** ([src/calls/function_name.py](src/calls/function_name.py)):
  at each step, the next token is chosen as the highest-logit token among
  those that still extend at least one candidate function name (prefix
  matching over the tokenized function names).
- **Parameter extraction** ([src/calls/function_parameters.py](src/calls/function_parameters.py)):
  the JSON keys are forced to match the function's parameter schema, and
  each value is generated token-by-token and validated on the fly by a
  small type-specific state machine (`number`, `string`, `bool` in the same
  file). For functions that take a `regex` parameter, the prompt also
  injects a set of rules constraining the model to safe, specific regex
  patterns instead of broad wildcards.
- **Model** ([src/llm_sdk](src/llm_sdk)): a small local package (`llm_sdk`)
  wrapping a Hugging Face causal LM (`Qwen/Qwen3-0.6B` by default) and
  exposing `encode`, `decode` and `get_logits_from_input_ids`, which is all
  the custom decoding logic needs.

## Project structure

```
data/
  input/functions_definition.json               list of callable functions (name, description, parameters, return type)
  input/function_calling_tests.json             prompts used by `make run`
  input/additional_tests.json                   prompts used by `make test`
  output/function_calling_results.json          generated output (prompt, chosen function, parameters)
  correction/function_calling_corrections.json  expected results for the test prompts

src/
  __main__.py                                   entry point: loads functions, runs each prompt, writes the output JSON
  arguments.py                                  CLI argument parsing (--functions_definition, --input, --output)
  Function.py                                   pydantic model describing a callable function
  model.py                                      instantiates the LLM used by the rest of the app
  prompt.py                                     builds the two prompts (function selection / parameter extraction)
  calls/
    function_name.py                            constrained decoding for picking the function name
    function_parameters.py                      constrained decoding + type validators for the arguments
  llm_sdk/                                      local package wrapping the Hugging Face model
  tests/unit_tests.py                           unit tests (no real model calls)
```

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) for dependency management
- The dependencies in [requirements.txt](requirements.txt), which include
  the local `llm_sdk` package (installed in editable mode) plus `torch`,
  `transformers` and `huggingface_hub` to run the model.

## Installation

```bash
make install
```

This installs the local `llm_sdk` package and the rest of `requirements.txt`
with `uv`.

The first run will download the default model (`Qwen/Qwen3-0.6B`) from the
Hugging Face Hub.

## Usage

Run the program on the default input file
(`data/input/function_calling_tests.json`):

```bash
make run
```

Every prompt in the input file produces an entry in
`data/output/function_calling_results.json` with the original prompt, the
chosen function name and the extracted parameters.

You can also call the module directly and override any of the default
paths:

```bash
uv run python -m src --functions_definition data/input/functions_definition.json \
                      --input data/input/function_calling_tests.json \
                      --output data/output/function_calling_results.json
```

## Testing & linting

```bash
make unit          # run the unit tests (pytest, model calls mocked out)
make lint           # flake8 + mypy on src
```

The unit tests replace `src.model.llm` with a fake before importing the
application modules, so they run fast and don't need the actual model or a
GPU.

## Debugging

```bash
make debug
```

Starts the program under `pdb`. Useful commands once inside:

| Command | Action            |
|---------|--------------------|
| `n`     | next line          |
| `s`     | step into function |
| `c`     | continue running   |
| `p var` | print a variable   |
| `l`     | show nearby code   |
| `q`     | quit               |
