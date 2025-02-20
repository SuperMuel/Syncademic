from functions import settings
from functions.ai.types import RulesetOutput
import uuid
from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    ToolMessage,
)

from .prompts import EXAMPLE_COMPRESSION_1, EXAMPLE_OUTPUT_1, SYSTEM_PROMPT
from functions.settings import settings


def format_structured_output_examples(
    input: str,
    output: RulesetOutput,
    *,
    tool_message_content: str = "The ruleset is valid !",
) -> list[BaseMessage]:
    """Convert an example into a list of messages that can be fed into an LLM.

    This code is an adapter that converts our example to a list of messages
    that can be fed into a chat model.

    The list of messages per example corresponds to:

    1) HumanMessage: contains the content from which content should be extracted.
    2) AIMessage: contains the extracted information from the model
    3) ToolMessage: contains confirmation to the model that the model requested a tool correctly.

    The ToolMessage is required because some of the chat models are hyper-optimized for agents
    rather than for an extraction use case.
    """

    tool_call = {
        "id": str(uuid.uuid4()),
        "args": output.model_dump(),
        # The name of the function right now corresponds
        # to the name of the pydantic model
        # This is implicit in the API right now,
        # and will be improved over time.
        "name": output.__class__.__name__,
    }

    return [
        HumanMessage(content=input),
        AIMessage(content="", tool_calls=[tool_call]),
        ToolMessage(content=tool_message_content, tool_call_id=tool_call["id"]),
    ]


class RulesetBuilder:
    llm: BaseChatModel

    def __init__(self, llm: BaseChatModel | str = settings.RULES_BUILDER_LLM):
        if isinstance(llm, str):
            self.llm = init_chat_model(llm)
        else:
            self.llm = llm

    def create_chain(self) -> Runnable[dict, RulesetOutput]:
        llm = self.llm.with_structured_output(RulesetOutput)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder("examples"),
                ("human", "{compressed_schedule}"),
            ]
        )

        return (prompt | llm).with_config(run_name="simple_ruleset_builder")  # type: ignore

    def generate_examples(self) -> list[BaseMessage]:
        examples = [(EXAMPLE_COMPRESSION_1, EXAMPLE_OUTPUT_1)]

        messages = []
        for input_text, output in examples:
            messages.extend(format_structured_output_examples(input_text, output))

        return messages

    def generate_ruleset(
        self,
        compressed_schedule: str,
        *,
        metadata: dict | None = None,
    ) -> RulesetOutput:
        chain = self.create_chain()

        examples = self.generate_examples()

        result = chain.invoke(
            {
                "compressed_schedule": compressed_schedule,
                "examples": examples,
            },
            config={"metadata": metadata} if metadata else None,
        )

        assert isinstance(result, RulesetOutput)

        return result
