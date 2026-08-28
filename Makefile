py=python3

run:
	uv run $(py) src/main.py $(ARGS)
	
install:
	uv pip install -r requirements.txt

debug:
	uv run $(py) -m pdb src/main.py

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	flake8 src & mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . and mypy . --strict