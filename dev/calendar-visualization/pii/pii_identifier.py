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
        description="Read again the text and try to identify names that you missed. If you are sure that there are no more names, set this to []",
    )


# Create a prompt template for extracting names
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert name extraction algorithm. "
            "Extract all person names from the following text and return them as a list.",
        ),
        ("human", "{text}"),
    ]
)

funny_teacher_names = [
    "Professor Al G. Bra",
    "Dr. Ima Phailure",
    "Professor Anita Break",
    "Dr. Polly Tician",
    "Professor Ben Dover",
    "Dr. Frank N. Stein",
    "Professor Hugh Jass",
    "Dr. Oliver Sudden",
    "Professor Justin Time",
    "Dr. Ella Mentary",
    "Profesor/a Consuelo Nada",
    "Dr. Phil McCracken",
    "Professor Barb Dwyer",
    "Docteur Jean Jacte",
    "Professor Stan Still",
    "Dr. Rick O'Shea",
    "Professor Paige Turner",
    "Prof. C. Howitt Works",
    "Professor Sue Flay",
    "Herr Doktor Hans Off",
    "Professor Juan en Millón",
    "Dr. Bella Donna",
    "Professeur Rémy Niscence",
    "Professor Ugo Fasta",
    "Señor/a Manuel Labor",
    "Dr. Otto Correcto",
    "Professor Herb O’Logy",
    "Docteur Hugo Miséricorde",
    "Professor Heinz Ketchup",
    "Dr. Anita Patente",
    "Profesor/a Silvia Risas",
    "Professeur Emile Ité",
    "Professor Luke Warm",
    "Docteur Avril Détour",
    "Professor Juan Moretime",
    "Dr. Al Dente",
    "Prof. Will Power",
    "Herr Professor Otto Graph",
    "Docteur Claire Voyance",
    "Profesor/a Serio Noes",
    "Professor Skip Class",
    "Dottor/a Gia Notate",
    "Professor Rosa Tería",
    "Dr. Pascal Trouble",
    "Prof. Anne Teak",
    "Señor/a Adela Esperanza",
    "Docteur Pierre Papier",
    "Professor Ella Vate",
    "Herr Doktor Karl Ding",
    "Dr. Beatrice Ilusión",
]


def extract_names(text: str, llm: BaseChatModel) -> list[Person]:
    if not text:
        return []

    chain = llm.with_structured_output(People)

    result = chain.invoke(text)

    assert isinstance(result, People)

    return result.people + [Person(name=name) for name in result.forgotten]
