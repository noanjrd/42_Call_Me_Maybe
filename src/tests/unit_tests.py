"""Fast unit tests that do not call the real LLM.

Run from the project root with:
    .venv\\Scripts\\python.exe -m pytest
"""

import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
import pytest


fake_model = ModuleType("src.model")
fake_model.llm = SimpleNamespace()  # type: ignore[attr-defined]
sys.modules["src.model"] = fake_model

from src import prompt  # noqa: E402
from src.Function import Function  # noqa: E402
from src.__main__ import export_json, open_prompts  # noqa: E402
from src.calls import function_name, function_parameters  # noqa: E402


def make_function(
    name: str = "fn_greet", parameters: dict[str, str] | None = None
) -> Function:
    """Create a small Function object reused by the tests below."""
    return Function(
        name=name,
        tokenized_name=[10, 11],
        description="Generate a greeting.",
        parameters=parameters or {"name": "string"},
        number_parameters=1,
        return_type={"type": "string"})


class TestFunction:
    def test_get_name_description_returns_name_and_description(
        self,
    ) -> None:
        function = make_function()

        assert function.get_name_description() == (
            "Name : fn_greet, Description : Generate a greeting."
        )


class TestPrompts:
    def test_function_name_prompt_lists_each_available_function(
        self,
    ) -> None:
        text = prompt.get_prompt_for_function_name(
            "Say hello to Ada", [make_function(), make_function("fn_goodbye")]
        )

        assert "Choose the single best function for the user request." in text
        assert "User request: Say hello to Ada" in text
        assert "Name : fn_greet" in text
        assert "Name : fn_goodbye" in text
        assert "Return only one exact function name from the list." in text
        assert text.endswith("Selected function:")

    def test_parameter_prompt_includes_schema(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        text = prompt.get_prompt_for_parameters(
            "Say hello to Ada",
            make_function(parameters={"name": "string"}),
        )

        assert '"name": <string value>' in text
        assert "User request: Say hello to Ada" in text
        assert "Return only one JSON object" in text

    def test_regex_prompt_includes_current_generation_rules(
        self,
    ) -> None:
        text = prompt.get_prompt_for_parameters(
            "Replace vowels with asterisks",
            make_function(parameters={
                "source_string": "string",
                "regex": "string",
                "replacement": "string",
            }),
        )

        assert "REGEX GENERATION RULES" in text
        assert "To match numbers/digits: [0-9]+" in text
        assert "To match vowels: ([aeiouAEIOU])" in text
        assert "Never use '.*' or broad wildcards." in text

    def test_get_functions_reads_json_and_encodes_names(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:  # tmp_path is a temporary empty folder for test files
        class EncodedTokens:
            def tolist(self) -> list[list[int]]:
                return [[42, 43]]

        class FakeLlm:
            def encode(self, name: str) -> EncodedTokens:
                assert name == "fn_double"
                return EncodedTokens()

        definitions = [{
            "name": "fn_double",
            "description": "Double a number.",
            "parameters": {"value": {"type": "number"}},
            "returns": {"type": "number"},
        }]
        path = tmp_path / "functions.json"
        # '/' means join path when using pathlib.Path
        path.write_text(json.dumps(definitions), encoding="utf-8")
        monkeypatch.setattr(prompt, "llm", FakeLlm())
        # replace the llm variable inside the prompt module with FakeLlm().

        functions = prompt.get_functions(path)

        assert len(functions) == 1
        assert functions[0].tokenized_name == [42, 43]
        assert functions[0].parameters == {"value": "number"}


class TestFunctionNameSelection:
    def test_next_logit_is_largest_allowed_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class FakeLlm:
            def get_logits_from_input_ids(
                self, encoded_prompt: list[int]
            ) -> list[float]:
                assert encoded_prompt == [99]
                return [0.1, 0.8, 0.4, 0.9]

        monkeypatch.setattr(function_name, "llm", FakeLlm())

        next_token = function_name.get_next_logit_for_function_name(
            encoded_prompt=[99], lap=0, candidates=[[1, 2], [3, 2]]
        )

        assert next_token == 3

    def test_next_logit_is_none_when_candidates_are_finished(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class FakeLlm:
            def get_logits_from_input_ids(
                self, *args: object
            ) -> list[float]:
                return [1.0]
        fake_llm = FakeLlm()
        monkeypatch.setattr(function_name, "llm", fake_llm)

        result = function_name.get_next_logit_for_function_name([1], 1, [[0]])

        assert result is None


class TestParameterValidation:
    def test_number_accepts_integer_and_decimal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class FakeLlm:
            def decode(self, token: str) -> str:
                return token

        fake_llm = FakeLlm()
        monkeypatch.setattr(function_parameters, "llm", fake_llm)

        # FakeLlm.decode is an identity function, so the fake "token"
        # passed here is really the already-decoded text under test.
        assert function_parameters.number(
            "", "42"  # type: ignore[arg-type]
        ) is True
        assert function_parameters.number(
            "", "-3.5"  # type: ignore[arg-type]
        ) is True
        assert function_parameters.number(
            "", "three"  # type: ignore[arg-type]
        ) is False

    def test_string_requires_opening_quote(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class FakeLlm:
            def decode(self, token: str) -> str:
                return token

        fake_llm = FakeLlm()
        monkeypatch.setattr(function_parameters, "llm", fake_llm)

        assert function_parameters.string(
            "", '"Ada'  # type: ignore[arg-type]
        ) is True
        assert function_parameters.string(
            "", "Ada"  # type: ignore[arg-type]
        ) is False

    def test_bool_accepts_true_and_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class FakeLlm:
            def decode(self, token: str) -> str:
                return token

        fake_llm = FakeLlm()
        monkeypatch.setattr(function_parameters, "llm", fake_llm)

        assert function_parameters.bool(
            "", "true"  # type: ignore[arg-type]
        ) is True
        assert function_parameters.bool(
            "", "false"  # type: ignore[arg-type]
        ) is True
        assert function_parameters.bool(
            "", "maybe"  # type: ignore[arg-type]
        ) is False


class TestJsonHelpers:
    def test_export_json_creates_directory_and_open_prompts_reads_it(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "nested" / "answers.json"
        expected = [{"prompt": "Hello", "name": "fn_greet"}]

        export_json(path, expected)

        assert open_prompts(path) == expected
