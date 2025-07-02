from .output_structure import ResponseSchema,StructuredOutputParser
import os
import pandas as pd
import json
from typing import List, Dict, Tuple, Union, Optional


class FileProcessor:
    def __init__(self,excle_file_path:str):
        self.excle_file_path = excle_file_path
    
    def _get_label_groups_with_CReDEs(cls) -> List[str]:
        df = pd.read_excel(cls.excle_file_path, na_filter=True)

        CReDEs_dict = {}
        current_entity = None
        data_dict = {}

        for _, row in df.iterrows():
            label_name = str(row['一级标签名称']).strip()
            label_class = str(row['标签类型']).strip()

            label_desc = str(row.get('标签内容说明（描述）', '')).strip()

            # 判断是否NaN并处理为非空列表
            if pd.isna(row.get('CReDEs-数据项')):
                metadata_name = []
            else:
                metadata_name = [x.strip() for x in str(row['CReDEs-数据项']).split(',') if x.strip()]

            if pd.isna(row.get('CReDEs-值域描述')):
                metadata_type = []
            else:
                metadata_type = [x.strip() for x in str(row['CReDEs-值域描述']).split(',')]

            if pd.isna(row.get('CReDEs-值域')):
                metadata_value = []
            else:
                metadata_value = [x.strip() for x in str(row['CReDEs-值域']).split(',')]

            if label_class == '实体标签':
                if current_entity is not None:
                    CReDEs_dict[current_entity] = data_dict
                current_entity = label_name
                data_dict = {}

            if current_entity and metadata_name:
                for name, mtype, value in zip(metadata_name, metadata_type, metadata_value):
                    if name and name not in data_dict and mtype and value:
                        data_dict[name] = {
                            "metadata_type": mtype,
                            "metadata_description": f"描述信息:{label_desc}值域描述:{value}"
                        }
        if current_entity is not None:
            CReDEs_dict[current_entity] = data_dict

        return CReDEs_dict
    
    def get_CReDEs_dict(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        return self._get_label_groups_with_CReDEs()

class BasePrompter:
    def __init__(self, CReDEs_dict: Dict[str, Dict[str, Dict[str, str]]]):
        self.CReDEs_dict = CReDEs_dict
        
    def _get_response_schemas(cls) -> List[ResponseSchema]:
        response_schemas = {}
        for entity, metadata in cls.CReDEs_dict.items():
            if entity not in response_schemas:
                response_schemas[entity] = []
            for name, details in metadata.items():
                response_schemas[entity].append(
                    ResponseSchema(
                        name=name,
                        description=details['metadata_description'],
                        type=details['metadata_type']
                    )
                )
        return response_schemas

    def get_group_prompt_dict(self,only_json:bool=False) -> Dict[str, str]:
        response_schemas = self._get_response_schemas()
        grouped_prompt_dict = {}
        for entity, schemas in response_schemas.items():
            output_parser = StructuredOutputParser.from_response_schemas(schemas)
            if only_json:
                ### format not instruction
                json_prompt = output_parser.get_format_instructions(only_json)
            else:
                ### format instruction
                json_prompt = output_parser.get_format_instructions()

            grouped_prompt_dict[entity] = json_prompt
        return grouped_prompt_dict
                
