from __future__ import annotations
from typing import Any, Union, List
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.output_parsers.json import parse_and_check_json_markdown
from pydantic import BaseModel

class BaseResponseSchema(BaseModel):
    """Base response schema"""
    question: str
    label_name: str
    label_desc: str
    Limitation: str


class ResponseSchema_QALine(BaseResponseSchema):
    """问答型 schema"""
    pass


class ResponseSchema_QALine_enum(BaseResponseSchema):
    """枚举型问答 schema"""
    selections: str


def _get_sub_string(schema: BaseResponseSchema) -> str:
    if isinstance(schema, ResponseSchema_QALine_enum):
        return f'\t"Question": "请结合上述信息，从下列选项中选择恰当的内容回答：{schema.question}？",\n' \
               f'\t"Limitation":"{schema.Limitation}",\n' \
               f'\t"Additional_Information": "数据主要来源于{schema.label_name}标签，该标签的描述是{schema.label_desc}",\n' \
               f'\t"Selections": "{schema.selections}",\n' \
               f'\t"Answer":""'
    else:
        return f'\t"Question": "请结合上述信息，回答：{schema.question}？",\n' \
               f'\t"Limitation": "{schema.Limitation}",\n' \
               f'\t"Additional_Information": "数据主要来源于{schema.label_name}标签，该标签的描述是{schema.label_desc}",\n' \
               f'\t"Answer":""'


STRUCTURED_FORMAT_INSTRUCTIONS = """输出应该是一个按如下结构格式化的 Markdown 代码片段，包括开头的 "```json" 和结尾的 "```":
```json
{{
{format}
}}
```"""

STRUCTURED_FORMAT_SIMPLE_INSTRUCTIONS = """
```json
{{
{format}
}}
```"""


class StructuredOutputParser(BaseOutputParser[dict[str, Any]]):
    """Parse the output of an LLM call to a structured output."""

    response_schemas: List[BaseResponseSchema]

    @classmethod
    def from_response_schemas(
        cls, response_schemas: List[BaseResponseSchema]
    ) -> StructuredOutputParser:
        return cls(response_schemas=response_schemas)

    def get_format_instructions(self, only_json: bool = False) -> str:
        schema_str = "".join(
            [_get_sub_string(schema) for schema in self.response_schemas]
        )
        if only_json:
            return STRUCTURED_FORMAT_SIMPLE_INSTRUCTIONS.format(format=schema_str)
        else:
            return STRUCTURED_FORMAT_INSTRUCTIONS.format(format=schema_str)

    def parse(self, text: str) -> dict[str, Any]:
        expected_keys = [rs.label_name for rs in self.response_schemas]
        return parse_and_check_json_markdown(text, expected_keys)

    @property
    def _type(self) -> str:
        return "structured"
