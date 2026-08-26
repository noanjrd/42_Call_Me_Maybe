from pydantic import BaseModel

class Function(BaseModel):
    name: str
    tokenized_name: list[int]
    description: str
    parameters: dict[str, str]
    number_parameters: int
    return_type: dict[str, str]


    def get_name_description(self):
        return f"Name : {self.name}, Description : {self.description}"
