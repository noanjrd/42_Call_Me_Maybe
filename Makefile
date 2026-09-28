py=python

run:
	uv run 42-call-me-maybe $(ARGS)



pytest:
	uv run $(py) -m pytest -q --basetemp=.pytest_tmp

test:
	uv run 42-call-me-maybe --input data/input/additional_tests.json
	
install:
	uv sync

debug:
	uv run $(py) -m pdb src

clean:
	sudo find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf data/output .pytest_cache .pytest_tmp .mypy_cache

lint:
	uv run flake8 src && uv run mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs