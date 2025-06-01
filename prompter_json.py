import json
import os
from typing import List, Dict, Tuple, Any, Optional
from logger import CustomLogger
from prompt_info.base_json.CReDEs_Prompter import BasePrompter

LABEL_LIST_DICT_JSON = {
    "blzd":["标本来源","标本来源:标本大小","标本来源:解剖肝段","主要病变","主要病变:病变大小","主要病变:病变数量","主要病变:卫星结节","主要病变:是否多灶性生长","主要病变:包膜是否完整","主要病变:是否浸润性生长","主要病变:卫星灶情况","病理学分型","病理学分型:组织学分型","病理学分型:细胞学类型","病理学分型:分化信息","病理学分型:ACJJ分期","病理学分型:病变部位","病理学分型:癌细胞形状","微血管侵犯标志","微血管侵犯标志:MVI分级","微血管侵犯标志:侵犯数量","微血管侵犯标志:侵犯部位","侵犯类型","切缘情况","切缘情况:切缘距离","染色项目及结果","免疫组化项目及结果","肝硬化情况","肝炎分期分级","淋巴结侵犯部位","淋巴结侵犯部位:淋巴结转移阳性数"]
}
BASIC_PROMPT = f'[任务]\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对所提供的中文电子病历文本进行信息抽取，需要抽取信息的文本在最后，请按照[要求]的内容进行信息抽取：\n[要求]\n1. 我将会给你两部分数据，一部分数据是标注后的数据文本-[标注数据]，是由实体和属性组成的一段数据，组成的格式为"实体:属性"，其中如果没有":"连接就是只有实体没有属性，反之则既有实体又有属性。另一部分数据是病例原文-[病例原文]，你需要从这些数据中抽取关键信息填写json\n2.json中没有定义的键值对不能出现在结果中,以下是对json格式的要求\n\t(1). json的键值对必须是字符串类型，不能是数字或其他类型\n\t(2). json的键值对必须是英文冒号":"分隔，不能是中文冒号\n\t(3). json的键值对必须是英文逗号","分隔，不能是中文逗号\n\t(4). json的键值对必须是双引号""包裹，不能是单引号''\n\t(5). json的键值对必须是英文花括号"{{}}"包裹，不能是中文花括号\n\t(6). json的键值对必须是英文方括号"[]"包裹，不能是中文方括号\n\t(7). json的键值对必须是英文等于号"="分隔，不能是中文等于号\n\t(8). json的键值对必须是英文分号";"分隔，不能是中文分号\n\t(9).json中不允许出现空格或制表符或换行符，请确保格式正确无误\n\t(10).请按照[json]中的所定义的键值对进行填写\n3.[json]中定义了"{{ 键名 }}": {{ 数据类型 }}  // {{ 填写描述 }}，其中"数据类型"指的是填写当前键值对的python数据类型；"填写描述"包含两个描述，一个是"描述信息"，另一个是"值域描述"，"描述信息"指的是判断文本中的内容是否符合当前描述，"值域描述"指的是填写当前键值对的取值范围或限制条件\n4.请直接数据json，不需要额外的解释和推理，只需要填写json即可\n[病例原文]\n{origin_text}\n[标注数据]\n{annotation_text}\n[json]\n{grouped_json}\n[输出]\n'


class CReDEsModel:
    def __init__(self, label_list_dict:Dict[str,List[str]],text_type:str):
        self.label_list_dict = label_list_dict
        self.text_type = text_type
    

    @classmethod
    def _group_labels(cls,label_list_dict:Dict[str,List[str]],text_type:str) -> Dict[str, List[str]]:
        label_list = label_list_dict[text_type]
        grouped = {}
        attr_groups = {}
        non_attr_entities = set()

        for label in label_list:
            if ":" in label:
                main_entity, _ = label.split(":", 1)
                if main_entity not in attr_groups:
                    attr_groups[main_entity] = [main_entity]
                attr_groups[main_entity].append(label)
            else:
                non_attr_entities.add(label)
        non_attr_entities -= set(attr_groups.keys())
        grouped["non_attr_entities"] = list(non_attr_entities)
        for key, values in attr_groups.items():
            grouped[key] = values
        return grouped


    def match_grouped_label_data(self, alpaca_data:List[Dict[str, Any]]) -> List[Dict[str, Dict[str, List[str]]]]:
        grouped_label_data = self._group_labels(self.label_list_dict,self.text_type)
        # print(f"grouped_label_data: {grouped_label_data}")
        all_data_group_result = []
        for item in alpaca_data:
            try:
                group_result = {group_name: [] for group_name in grouped_label_data.keys()}
                labeled_origin_text = item.get("input","")
                labeled_data_list = item.get("output","").split("\n")
                for group_name, label_group in grouped_label_data.items():
                    ### collect all labels in the group
                    if group_name != "non_attr_entities":
                        i = 0
                        while i < len(labeled_data_list):
                            j = i + 1
                            entity = labeled_data_list[i]
                            entity_len = len(entity.split(":"))
                            if group_name in entity:
                                while j < len(labeled_data_list) and labeled_data_list[j].startswith(entity.split(":")[0]):
                                    if len(labeled_data_list[j].split(":")) == entity_len:
                                        break
                                    j = j + 1
                                group_result[group_name].append(labeled_data_list[i:j])
                                i = j 
                            else:
                                i += 1
                    else:
                        for entity in labeled_data_list:
                            entity_key = entity.split(":")[0]
                            if entity_key in label_group:
                                group_result[group_name].append(entity)
                single_data_ditc = {
                    "text": labeled_origin_text,
                    "group_result": group_result
                }
                all_data_group_result.append(single_data_ditc)    
            except Exception as e:
                print(e)
                return []
        return all_data_group_result
    
    def get_unit_grouped_label_key(self, unit_grouped_label_data: List[Any]) -> List[str]:
        flat_list = []
        for item in unit_grouped_label_data:
            if isinstance(item, list):
                flat_list.extend(item)
            else:
                flat_list.append(item)
        
        grouped_label_dict_key = []
        for unit_label in flat_list:
            if ":" in unit_label:
                main_entity, _ = unit_label.split(":", 1)
                grouped_label_dict_key.append(main_entity)
            else:
                grouped_label_dict_key.append(unit_label)
        return grouped_label_dict_key

class CReDEs_Prompter(CReDEsModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str, basic_prompt:str,logger:CustomLogger,baseprompter_obj:BasePrompter):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger
        self.basic_prompt = basic_prompt
        self.baseprompter = baseprompter_obj
        self.grouped_label_data = super()._group_labels(label_list_dict, text_type)
    
    def _get_base_prompt_dict(self) -> Dict[str, str]:
        return self.baseprompter.get_group_prompt_dict()
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        # self.logger.info(all_data_group_result)
        grouped_prompt_dict = self._get_base_prompt_dict()
        all_prompt_list = []
        for item in all_data_group_result:
            origin_text = item.get("text", "")
            group_result = item.get("group_result", {})
            single_part_prompt_dict = {
                "group_text": origin_text,
                "prompt_list": []
            }
            for group_name, group_data in group_result.items():
                # only entity
                try:
                    if group_name == "non_attr_entities": 
                        prompt_key_list = self.get_unit_grouped_label_key(group_data)
                        json_unit_prompt = ''
                        for prompt_key in prompt_key_list:
                            if prompt_key in grouped_prompt_dict:
                                # combine the 'only entity' prompt --> markdown json
                                json_unit_prompt += f"{grouped_prompt_dict[prompt_key]}\n"
                        basic_prompt = self.basic_prompt.format(origin_text=origin_text,annotation_text=group_data, grouped_json=json_unit_prompt)
                        single_part_prompt_dict["prompt_list"].append(basic_prompt)
                        # self.logger.info(f"Generated prompt: {basic_prompt}")

                    # entity with attribute
                    else:
                        prompt_key_list = self.get_unit_grouped_label_key(group_data)
                        for prompt_key in prompt_key_list:
                            basic_prompt = ''
                            json_unit_prompt = ''
                            if prompt_key in grouped_prompt_dict:
                                json_unit_prompt = f"{grouped_prompt_dict[prompt_key]}\n"
                                basic_prompt = self.basic_prompt.format(origin_text=origin_text,annotation_text=group_data, grouped_json=json_unit_prompt)
                                single_part_prompt_dict["prompt_list"].append(basic_prompt)
                except Exception as e:
                    self.logger.error(f"Error processing group {group_name}: {e}")
                    continue
            all_prompt_list.append(single_part_prompt_dict)

        return all_prompt_list
