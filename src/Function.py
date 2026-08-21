from pydantic import BaseModel

class Function(BaseModel):
    name: str
    tokenized_name: list[int]
    description: str
    parameters: dict[str, dict[str, str]]
    return_type: dict[str, str]


    def get_name_description(self):
        return f"name: {self.name}() - description: {self.description}"
