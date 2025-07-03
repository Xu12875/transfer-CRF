import json
import os
from typing import List, Dict, Tuple, Any, Optional
from logger import CustomLogger
from prompt_info.base_json.CReDEs_Prompter import BasePrompter

LABEL_LIST_DICT_JSON = {
    "blzd":["标本来源","标本来源:标本大小","标本来源:解剖肝段","主要病变","主要病变:病变大小","主要病变:病变数量","主要病变:卫星结节","主要病变:是否多灶性生长","主要病变:包膜是否完整","主要病变:是否浸润性生长","主要病变:卫星灶情况","病理学分型","病理学分型:组织学分型","病理学分型:细胞学类型","病理学分型:分化信息","病理学分型:ACJJ分期","病理学分型:病变部位","病理学分型:癌细胞形状","微血管侵犯标志","微血管侵犯标志:MVI分级","微血管侵犯标志:侵犯数量","微血管侵犯标志:侵犯部位","侵犯类型","切缘情况","切缘情况:切缘距离","染色项目及结果","免疫组化项目及结果","肝硬化情况","肝炎分期分级","淋巴结侵犯部位","淋巴结侵犯部位:淋巴结转移阳性数"],
    "ryjl":["主诉","腹壁静脉曲张标志","感染类型","感染类型:感染时间","疾病名称","疾病名称:发生时间","疾病名称:发生次数","疾病名称:治疗持续时间","疾病名称:疾病阶段","疾病名称:治疗方式","腹水情况","输血史","药物治疗","药物治疗:治疗开始时间","药物治疗:治疗停止时间","手术治疗","手术治疗:手术时间","吸烟情况","吸烟情况:吸烟量","饮酒情况","饮酒情况:饮酒量","饮酒情况:饮酒类型","饮酒情况:饮酒时间","家族疾病史","术前治疗方式","辅助检查类型","辅助检查类型:检查日期","辅助检查类型:辅助检查结果","辅助检查类型:病变数量","辅助检查类型:病变大小","辅助检查类型:解剖肝段","辅助检查类型:病变部位","辅助检查类型:检查医院","肝病并发症","多期增强扫描分期","肝癌复发","肝癌复发:肝癌复发来源","吸烟史","手术史"],
    "rcbc": ["并发症", "并发症:并发症治疗方式", "输血标志", "输血标志:输血类型", "输血标志:输血量", "静脉曲张标志", "静脉曲张标志:静脉曲张部位", "静脉曲张标志:静脉曲张程度", "静脉曲张标志:检查方式", "文书标题", "操作名称", "病灶类型", "病灶类型:病灶数目"],
    "jc": ["静脉曲张标志", "静脉曲张标志:静脉曲张部位", "静脉曲张标志:静脉曲张程度", "病灶类型", "病灶类型:病灶数目", "病灶类型:大小", "病灶类型:肝段", "病灶类型:肝叶", "淋巴结转移标志", "淋巴结转移标志:淋巴结转移部位", "血管癌栓标志", "血管癌栓标志:血管部位", "血管癌栓标志:血管分支", "脾脏大小长径", "脾门厚度", "肝硬化标志", "腹水情况", "腹水情况:腹水厚度", "多期增强扫描分期", "门脉高压标志", "脾功能亢进标志"],
    "ssjl": ["手术者", "手术开始时间", "手术结束时间", "手术名称", "术前诊断为肝内胆管癌", "淋巴结侵犯标志", "淋巴结侵犯标志:淋巴结侵犯部位", "淋巴结侵犯标志:淋巴结清扫", "淋巴结侵犯标志:淋巴结清扫范围", "淋巴结侵犯标志:淋巴结清扫数目", "病灶类型", "病灶类型:病灶数目", "病灶类型:病灶大小", "病灶类型:肝段", "病灶类型:肝叶", "胆管癌栓标志", "胆管癌栓标志:胆管分支", "血管癌栓标志", "血管癌栓标志:血管部位", "血管癌栓标志:血管分支", "血管癌栓标志:癌栓处理方式", "侵犯标志", "侵犯标志:侵犯部位", "肝硬化标志", "腹水情况", "转移标志", "转移标志:转移部位", "术中用药", "肝门阻断标志", "肝门阻断标志:肝门阻断类型", "肝门阻断标志:肝门阻断次数", "肝门阻断标志:肝门阻断时间", "放置腹腔引流管标志", "静脉曲张标志", "静脉曲张标志:静脉曲张部位", "静脉曲张标志:静脉曲张程度", "出血标志", "出血标志:出血量", "输血标志", "输血标志:输血类型", "输血标志:输血量"],
    "jrzl": ["肿瘤染色标志", "肿瘤染色标志:TAE术肿瘤范围", "肿瘤染色标志:TAE术肿瘤个数"]
}
BASIC_PROMPT = """
[任务]
请使用中文作答。你是一位出色的信息抽取专家，现需从提供的中文电子病历文本中进行信息抽取。请根据以下 [要求] 完成任务。所需处理的原始数据位于 prompt 的最后。

[要求]

1. 你将收到两部分数据：
   - [标注数据]：由“实体:属性”组成的结构化数据，其中：
     - 若无“:”，则表示该数据只有实体；
     - 若有“:”，则为“实体:属性”的格式。
   - [病例原文]：完整的电子病历原始文本。
   你需结合这两部分内容，从中抽取关键信息，并填写到指定的 JSON 中。

2. 输出结果必须严格遵循 JSON 的格式规范，具体如下：
   - (1) 所有键和值必须为字符串类型
   - (2) 使用英文冒号 ":" 作为键值对分隔符
   - (3) 使用英文逗号 "," 分隔多个键值对
   - (4) 所有键和值均使用英文双引号 " 包裹
   - (5) 使用英文花括号 包裹 JSON 对象
   - (6) 使用英文方括号 [] 表示数组（如适用）
   - (7) JSON 中不得使用任何中文符号（包括冒号、逗号、引号、括号等）
   - (8) JSON 中不得出现空格、换行或制表符，整体格式必须紧凑
   - (9) 若字段值本身采用结构如 "key=value;key2=value2"，请确保使用英文等号 "=" 和英文分号 ";"

3. 若某个字段在原文中出现多次（即多组相同字段值），请按照在原文中出现的顺序，使用英文逗号 "," 拼接各组值，并一并填写。例如：

   示例：
   "肝脏最大横径": "4.1cm,3.1cm",
   "肝脏最大纵径": "2.6cm,2.9cm"
若未出现则按照值域要求填写。
   
4. [json] 定义了所需填写的数据结构，格式为：
   "字段名": "数据类型"  // 描述信息；值域描述
   - 描述信息：用于判断原文中是否包含该字段信息
   - 值域描述：用于约束字段值的填写范围

5. 请严格按照值域描述填写字段值，遵循以下规则：
   - 若原文中信息完全匹配值域描述，则直接填写；
   - 无论是什么数据类型，病例原文中未描述的情况下，填写空字符串；
   - 若无法从文本中确定或值域无法涵盖该信息，填写空字符串。

6. 最终输出仅为 JSON 字符串，不需要解释、分析或中间过程，不要输出 "数据类型"  // 描述信息；值域描述 的信息。

[病例原文]
{origin_text}

[标注数据]
{annotation_text}

[json]
{grouped_json}

[输出]
"""


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
                # ungrouped -> non-attribute entities
                attr_groups[label] = [label]
        #         non_attr_entities.add(label)
        # non_attr_entities -= set(attr_groups.keys())
        # grouped["non_attr_entities"] = list(non_attr_entities)
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

        # Remove duplicates label
        return list(set(grouped_label_dict_key))

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
            # article_id = item.get("article_id", "")
            origin_text = item.get("text", "")
            group_result = item.get("group_result", {})
            single_part_prompt_dict = {
                # "article_id": article_id,
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
                        basic_prompt = self.basic_prompt.format(
                            origin_text=origin_text,
                            annotation_text=group_data, 
                            grouped_json=json_unit_prompt
                            )
                        single_part_prompt_dict["prompt_list"].append(basic_prompt)
                        # self.logger.info(f"Generated prompt: {basic_prompt}")

                    # entity with attribute
                    else:
                        prompt_key_list = self.get_unit_grouped_label_key(group_data)
                        for prompt_key, _ in grouped_prompt_dict.items():
                            basic_prompt = ''
                            json_unit_prompt = ''
                            # Loop format each key in basic prompt (every key)
                            # if prompt_key in grouped_prompt_dict:
                            json_unit_prompt = f"{grouped_prompt_dict[prompt_key]}\n"
                            basic_prompt = self.basic_prompt.format(
                                origin_text=origin_text,
                                annotation_text=group_data, 
                                grouped_json=json_unit_prompt
                                )
                            single_part_prompt_dict["prompt_list"].append(basic_prompt)
                except Exception as e:
                    self.logger.error(f"Error processing group {group_name}: {e}")
                    continue
            all_prompt_list.append(single_part_prompt_dict)

        return all_prompt_list
