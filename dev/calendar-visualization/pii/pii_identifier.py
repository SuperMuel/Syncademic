from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel


# Define a Pydantic model for the output
class Person(BaseModel):
    name: str = Field(..., description="The name of the person")


class People(BaseModel):
    people: list[Person]
    forgotten: list[str] = Field(
        ...,
        description="Read again the text and try to identify names that you missed "
        "or names that are written in a different form. "
        "If you are sure that there are no more names, set this to []",
    )


# Create a prompt template for extracting names
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert name extraction algorithm. "
            "Extract all person names from the following text and return them as a list. "
            "Person names can be found in any place in the text, even in URLs or email addresses, IDs, etc. "
            "You should write the names exactly as they appear in the text. "
            "If they appear under multiple forms, write them all (e.g ['Elon MUSK', 'Elon_Musk', 'Musk Elon']). ",
        ),
        ("human", "{text}"),
    ]
)


def extract_names(text: str, llm: BaseChatModel) -> list[Person]:
    if not text:
        return []

    chain = llm.with_structured_output(People)

    result = chain.invoke(text)

    assert isinstance(result, People)

    return result.people + [Person(name=name) for name in result.forgotten]


class NameReplacement(BaseModel):
    real_name: str = Field(..., description="The real name to replace")
    fictional_name: str = Field(..., description="The fictional name to replace with")


class NameReplacements(BaseModel):
    replacements: list[NameReplacement]


def create_fictional_names(
    llm: BaseChatModel, real_names: list[str]
) -> NameReplacements:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are part of a system to remove PII from a text. "
                "We will provide you with a list of real names and you will provide us with a list of fictional names. "
                "We will then replace real names with fictional names in the text. "
                "It is really important that the fictional names are different from the real names, but their length, structure and ethnicity must be similar. "
                " Provide as many fictional names as there are real names. ",
            ),
            ("human", "{real_names}"),
        ]
    )

    chain = prompt | llm.with_structured_output(NameReplacements)

    result = chain.invoke({"real_names": real_names})

    assert isinstance(result, NameReplacements)

    return result
