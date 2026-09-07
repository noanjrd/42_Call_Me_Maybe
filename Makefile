py=python

run:
	uv run $(py) -m src  $(ARGS)
	
test:
	uv run $(py) -m src --input data/input/additional_tests.json
	

install:
	uv pip install -e src/llm_sdk
	uv pip install -r requirements.txt

debug:
	uv run $(py) -m pdb src

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	flake8 src & mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . and mypy . --strict