from .output_structure import BaseResponseSchema,StructuredOutputParser,ResponseSchema_QALine_enum,ResponseSchema_QALine
import os
import pandas as pd
import json
from typing import List, Dict, Tuple, Union, Optional, Any


class CReDEs_FileProcessor:
    def __init__(self, label_csv_file_path: str, CReDEs_file_pathg: str):
        self.label_csv_file_path = label_csv_file_path
        self.CReDEs_file_pathg = CReDEs_file_pathg

    def _get_label_mapping_list(self) -> List[Dict[str, Any]]:
        df = pd.read_csv(self.label_csv_file_path)
        label_item_list = []
        for _, row in df.iterrows():
            label_id = str(row['标签版本']).strip()
            label_name = str(row['标签名称']).strip()
            label_desc = str(row['定义/描述']).strip()
            label_type = str(row['标签类型']).strip()
            label_attr_str = str(row.get('属性列表', '')).strip()
            label_attr_list = []

            if label_attr_str:
                label_attr = [x.strip() for x in label_attr_str.split(';') if x.strip()]
                for attr in label_attr:
                    if ':' in attr:
                        attr_name = attr.split(':')[0]
                        label_attr_list.append(attr_name)

            project_name = str(row.get('项目名称', '')).strip()
            label_temp_item = {
                "label_id": label_id,
                "label_name": label_name,
                "label_desc": label_desc,
                "label_type": label_type,
                "label_attr": label_attr_list,
                "project_name": project_name
            }
            label_item_list.append(label_temp_item)
        return label_item_list

    def _get_group_label_mapping_list(self) -> Dict[str, List[Dict[str, Any]]]:
        label_item_list = self._get_label_mapping_list()
        project_label_dict: Dict[str, List[Dict[str, Any]]] = {}
        for label_item in label_item_list:
            project_name = label_item['project_name']
            project_label_dict.setdefault(project_name, []).append(label_item)

        project_group_label_dict: Dict[str, List[Dict[str, Any]]] = {}

        for project_name, labels in project_label_dict.items():
            name_to_label = {item["label_name"]: item for item in labels}
            grouped_labels = []

            for label_item in labels:
                if label_item["label_type"] != "实体标签":
                    continue

                label_name = label_item["label_name"]
                label_attr = label_item["label_attr"]

                group_dict = {
                    label_name: {
                        "label_id": label_item["label_id"],
                        "label_desc": label_item["label_desc"]
                    }
                }

                for attr_name in label_attr:
                    attr_item = name_to_label.get(attr_name)
                    if attr_item and attr_item["label_type"] == "属性标签":
                        group_dict[attr_name] = {
                            "label_id": attr_item["label_id"],
                            "label_desc": attr_item["label_desc"]
                        }

                grouped_labels.append(group_dict)

            project_group_label_dict[project_name] = grouped_labels

        return project_group_label_dict
    
    def _get_CReDEs_basic_info(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        df = pd.read_csv(self.CReDEs_file_pathg)
        CReDEs_list = []
        for _, row in df.iterrows():
            label_id = str(row['标签版本']).strip()
            CReDEs_metadata_name = str(row['CReDEs-数据项']).strip()
            CReDEs_metadata_dataType = str(row['数据类型'])
            CReDEs_metadata_textLength = str(row['文本-长度'])
            CReDEs_metadata_numLength = str(row['数字-长度'])
            CReDEs_metadata_numPrecision = str(row['数字-精度'])
            CReDEs_metadata_numUnit = str(row['数字-单位'])
            CReDEs_metadata_dateFormat = str(row['日期/时间'])
            CReDEs_metadata_enumInfo = str(row['枚举-可选内容'])
            CReDEs_metadata_enumUnique = str(row['枚举-是否多选'])
            CReDEs_info_dict = {
                "label_id": label_id,
                "CReDEs_metadata_name": CReDEs_metadata_name,
                "CReDEs_metadata_dataType": CReDEs_metadata_dataType,
                "CReDEs_metadata_textLength": CReDEs_metadata_textLength,
                "CReDEs_metadata_numLength": CReDEs_metadata_numLength,
                "CReDEs_metadata_numPrecision": CReDEs_metadata_numPrecision,
                "CReDEs_metadata_numUnit": CReDEs_metadata_numUnit,
                "CReDEs_metadata_dateFormat": CReDEs_metadata_dateFormat,
                "CReDEs_metadata_enumInfo": CReDEs_metadata_enumInfo,
                "CReDEs_metadata_enumUnique": CReDEs_metadata_enumUnique
            }
            CReDEs_list.append(CReDEs_info_dict)
        return CReDEs_list

    def get_CReDEs_mapping_dict(self) -> Dict[str, List[List[Dict[str, Any]]]]:
        project_group_label_dict = self._get_group_label_mapping_list()
        CReDEs_list = self._get_CReDEs_basic_info()

        # 构建索引表：label_id -> 所有对应的CReDEs元数据（可能一对多）
        CReDEs_index: Dict[str, List[Dict[str, Any]]] = {}
        for item in CReDEs_list:
            CReDEs_index.setdefault(item['label_id'], []).append(item)

        CReDEs_dict: Dict[str, List[List[Dict[str, Any]]]] = {}

        for project_name, group_label_item_list in project_group_label_dict.items():
            project_group_list: List[List[Dict[str, Any]]] = []

            for group_label_item in group_label_item_list:
                group_with_metadata: List[Dict[str, Any]] = []

                for label_name, label_item in group_label_item.items():
                    label_id = label_item['label_id']
                    related_metadata_list = CReDEs_index.get(label_id, [])
                    if related_metadata_list:
                        for meta in related_metadata_list:
                            merged_info = {
                                "label_name": label_name,
                                "label_id": label_id,
                                "label_desc": label_item.get("label_desc", "")
                            }
                            merged_info.update(meta)
                            group_with_metadata.append(merged_info)
                    else:
                        group_with_metadata.append({
                            "label_name": label_name,
                            "label_id": label_id,
                            "label_desc": label_item.get("label_desc", "")
                        })

                project_group_list.append(group_with_metadata)

            CReDEs_dict[project_name] = project_group_list

        return CReDEs_dict
                    
class BasePrompter:
    def __init__(self, CReDEs_dict: Dict[str, Dict[str, Dict[str, str]]]):
        self.CReDEs_dict = CReDEs_dict
            
    def _datatype_mapping(self, datatype: str, text_length: str = "", num_precision: str = "", num_scale: str = "") -> str:
        datatype = str(datatype).strip()
        text_length = str(text_length).strip()
        num_precision = str(num_precision).strip()
        num_scale = str(num_scale).strip()

        if datatype == "文本":
            length = int(text_length) if text_length.isdigit() else 1000
            return f"VARCHAR({length})"

        elif datatype == "数字":
            if num_scale.isdigit():
                precision = int(num_precision) if num_precision.isdigit() else 10
                scale = int(num_scale)
                return f"DECIMAL({precision},{scale})"
            else:
                return "INT"

        elif datatype == "日期/时间":
            return "DATETIME"

        elif datatype == "枚举":
            return "ENUM"
        else:
            return "TEXT"


    def _transfer_str_to_bool(self, str: str) -> bool:
        str = str.strip().lower()
        if str in ["是", "yes", "true", "1"]:
            return True
        elif str in ["否", "no", "false", "0"]:
            return False
        else:
            return False
        
    def _process_CReDEs_list(self,group_CReDEsInfo_list: List[Dict[str, str]]) -> List[BaseResponseSchema]:
        group_response_schemas = []
        for CReDEs_info in group_CReDEsInfo_list:
            datatype = CReDEs_info.get("CReDEs_metadata_dataType", "")
            text_length = CReDEs_info.get("CReDEs_metadata_textLength", "")
            num_precision = CReDEs_info.get("CReDEs_metadata_numLength", "")
            num_scale = CReDEs_info.get("CReDEs_metadata_numPrecision", "")
            mapping_datatype = self._datatype_mapping(datatype, text_length, num_precision, num_scale)
            Limitation = "请根据文本内容，回答该字段应填写的内容，内容类型为" + mapping_datatype + " ，"
            if mapping_datatype == "ENUM":
                unique_opt:bool = self._transfer_str_to_bool(CReDEs_info.get("CReDEs_metadata_enumUnique", "")) 
                if not unique_opt:
                    Limitation += "只能从枚举可选内容中选择一个选项进行回答"
                else:
                    Limitation += "可以从枚举可选内容中选择多个选项进行回答，多个选项之间使用英文逗号 \",\" 分隔"
                schema_obj = ResponseSchema_QALine_enum(
                    question = CReDEs_info.get("CReDEs_metadata_name", ""),
                    label_name = CReDEs_info.get("label_name", ""),
                    label_desc = CReDEs_info.get("label_desc", ""),
                    Limitation = Limitation,
                    selections = CReDEs_info.get("CReDEs_metadata_enumInfo", "")
                )
                group_response_schemas.append(schema_obj)
            else:
                format_unit = CReDEs_info.get("CReDEs_metadata_numUnit", "")
                if format_unit is not None and format_unit != "":
                    format_unit_str = f"单位为 {format_unit}"
                    Limitation = f"{format_unit_str}。"
                else:
                    format_unit_str = ""    
                    Limitation = Limitation[::-1].replace("，", "。", 1)[::-1]
                if CReDEs_info.get("CReDEs_metadata_name") == "":
                    schema_obj = ResponseSchema_QALine(
                        question = CReDEs_info.get("label_name", ""),
                        label_name = CReDEs_info.get("label_name", ""),
                        label_desc = CReDEs_info.get("label_desc", ""),
                        Limitation = Limitation
                    )
                else:                
                    schema_obj = ResponseSchema_QALine(
                        question = CReDEs_info.get("CReDEs_metadata_name", ""),
                        label_name = CReDEs_info.get("label_name", ""),
                        label_desc = CReDEs_info.get("label_desc", ""),
                        Limitation = Limitation
                    )
                group_response_schemas.append(schema_obj)

        return group_response_schemas

                
    def _get_response_schemas(self) -> Dict[str, List[List[BaseResponseSchema]]]:
        response_schemas_dict = {}
        for project_name,CReDEs_grouped_list in self.CReDEs_dict.items():
            ### project_name:the last str of the project; eg."病理检查"
            project_name_mapping_name = project_name.split('-')[-1]
            if project_name_mapping_name not in response_schemas_dict:
                response_schemas_dict[project_name_mapping_name] = []
            ### group_CReDEsInfo_list : List[Dict[str, str]] -> Dict = CReDEsInfo
            for group_CReDEsInfo_list in CReDEs_grouped_list:
                group_response_schemas = self._process_CReDEs_list(group_CReDEsInfo_list)
                response_schemas_dict[project_name_mapping_name].append(group_response_schemas)
        return response_schemas_dict

    def get_group_prompt_dict(self,only_json:bool=True) -> Dict[str, List[List[str]]]:
        response_schemas_dict = self._get_response_schemas()
        # print(response_schemas_dict)
        grouped_prompt_dict = {}
        for project_mapping_name, group_schemas_list in response_schemas_dict.items():
            if project_mapping_name not in grouped_prompt_dict:
                grouped_prompt_dict[project_mapping_name] = []
            ### group_schemas_list : List[List[BaseResponseSchema]] -> List[BaseResponseSchema]
            for schema_list in group_schemas_list:
                # print(schema_list)
                grouped_shcema_list = []
                for schema in schema_list:
                    output_parser = StructuredOutputParser.from_response_schemas([schema])
                    QA_prompt = ""
                    if only_json:
                        ### format not instruction
                        QA_prompt = output_parser.get_format_instructions(only_json)
                    else:
                        ### format instruction
                        QA_prompt = output_parser.get_format_instructions()
                    grouped_shcema_list.append(QA_prompt)
                grouped_prompt_dict[project_mapping_name].append(grouped_shcema_list)
                
        return grouped_prompt_dict
                
