import json
import os
from typing import List, Dict, Tuple, Any, Optional
from prompt_info.base_pydantic.crf_model_blzd import Part_AnatomicalSiteDescription,Part_LymphNodeDescription,Part_OtherDescription
from prompt_info.base_pydantic.crf_model_grs import HealthHistory
from prompt_info.base_pydantic.crf_model_hys import MarriageFertilityHistory
from prompt_info.base_pydantic.crf_model_jws import MedicalHistory
from prompt_info.base_pydantic.crf_model_xbs import Part_OralMucosalHistory,Part_PastMedicalHistory
from prompt_info.base_pydantic.crf_model_yxjc import Part_AnatomicalSiteDescription_image,Part_LymphNodeDescription_image
from prompt_info.base_pydantic.crf_model_zkjc import Part_AnatomicalSiteDescription_SE,Part_LymphNodeDescription_SE
from prompt_info.base_pydantic.crf_model_ssjl import SurgeryRecord

from logger import CustomLogger


LABEL_LIST_DICT = {
    "xbs":["既往口腔病灶切除史","既往口腔病灶切除史:既往口腔病灶切除时间","既往颈淋巴结清扫史","既往颈淋巴结清扫史:既往颈淋巴结清扫时间","既往化疗史","既往化疗史:既往化疗时间","既往化疗史:既往化疗方案","既往化疗史:既往化疗次数","既往放疗史","既往放疗史:既往放疗时间","既往放疗史:既往放疗方式","既往放疗史:既往放疗次数","肿瘤病灶性质","既往黏膜病史"],
    "blzd":["分化信息","HPV","P16","切缘","神经侵犯","脉管侵犯","解剖学部位","解剖学部位:解剖学方位","解剖学部位:原发灶大小","解剖学部位:DOI","淋巴结清扫区域","淋巴结清扫区域:LN清扫方位","淋巴结清扫区域:LN数量","淋巴结清扫区域:颈清直径","淋巴结清扫区域:阳性LN数量","淋 巴结清扫区域:胞膜外侵犯"],
    "hys":["婚姻状况","生育状况"],
    "grs":["吸烟史","饮酒史","槟榔史"],
    "jws":["高血压","糖尿病","冠心病","血液系统疾病","其他肿瘤史","抗凝药物史"],
    "zkjc":["阳性淋巴结区域","阳性淋巴结区域:阳性淋巴结大小","阳性淋巴结区域:阳性淋巴结个数","阳性淋巴结区域:阳性淋巴结方位","阳性淋巴结区域:阳性淋巴结描述","阳性淋巴结区域:包膜外侵犯","病灶部位","病灶部位:病灶大小","病灶部位:病灶方位","病灶部位:累及部位"],
    "yxjc":["影像检查类型","阳性淋巴结区域","阳性淋巴结区域:阳性淋巴结大小","阳性淋巴结区域:阳性淋巴结个数","阳性淋巴结区域:阳性淋巴结方位","阳性淋巴结区域:阳性淋巴结描述","阳性淋巴结区域:包膜外侵犯","病灶部位","病灶部位:累及部位","病灶部位:病灶大小","病灶部位:病灶方位"],
    "ssjl":["手术名称","术后患者去向","主要病变","主要病变:病变部位","主要病变:病变大小","主要病变:病变影响对象","主要病变:病变影响结果","移除处理","移除处理:处理对象（删除）","移除处理:处理对象及所在部位","修复重建技术","修复重建技术:材料大小","修复重建技术:材料来源","修复重建技术:修复重建部位","修复重建技术:缺损大小","出血标志","出血标志:出血量"]
}

class CRFModel:
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

class CRFModel_Blzd_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str, logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger
        self.grouped_label_data = super()._group_labels(label_list_dict, text_type)

    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> Tuple[str, str, str]:
        class AnatomicalSiteDescription(Part_AnatomicalSiteDescription):
            def __init__(self,**data):
                super().__init__(**data)
        class LymphNodeDescription(Part_LymphNodeDescription):
            def __init__(self,**data):
                super().__init__(**data)
  
        class OtherDescription(Part_OtherDescription):
            def __init__(self,**data):
                super().__init__(**data)
        AnatomicalSiteDescription_json = cls._json_dumps_schema(AnatomicalSiteDescription.model_json_schema())
        LymphNodeDescription_json = cls._json_dumps_schema(LymphNodeDescription.model_json_schema())
        OtherDescription_json = cls._json_dumps_schema(OtherDescription.model_json_schema())
        return AnatomicalSiteDescription_json, LymphNodeDescription_json, OtherDescription_json
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        # self.logger.info(all_data_group_result)
        AnatomicalSiteDescription_json,LymphNodeDescription_json,OtherDescription_json = self._generate_group_json_schema()
        basic_prompt = """[任务]\n
        请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的中文电子病历文本进行信息抽取，需要抽取信息的文本在最后，请按照[要求]的内容进行信息抽取：\n
        [要求]\n
        1. 我将会给你两部分数据，一部分数据是标注后的数据文本-[标注数据]，是由实体和属性组成的一段数据，组成的格式为"实体:属性"，其中如果没有":"连接就是只有实体没有属性，反之则既有实体又有属性。另一部分数据是病例原文-[病例原文]，你需要从这些数据中抽取关键信息填写json schema\n
        2. 给你的实体与属性如下：分化信息，HPV，P16，切缘，神经侵犯，脉管侵犯，解剖学部位，解剖学部位:解剖学方位，解剖学部位:原发灶大小，解剖学部位:DOI，淋巴结清扫区域，淋巴结清扫区域:LN清扫方位，淋巴结清扫区域:LN数量，淋巴结清扫区域:颈清直径，淋巴结清扫区域:阳性LN数量，淋巴结清扫区域:胞膜外侵犯\n
        3.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n
        4.严格按照json shcema每个条目的要求进行填写，不得出现填写非json schema的内容,json shcema的每个字段都需出现，请按照[填写要求]完成json schema的填写\n
        [填写要求]
        1."解剖学部位信息"字段，包含两部分信息需要填写\n
        [1]"解剖学部位"字段，当出现解剖学部位的相关信息，利用str数据类型进行判断和填写\n
        [2]"属性信息"字段，里面包含三个字段，\n
        [2.1]"解剖学方位"字段，当出现解剖学部位的解剖方位信息，则利用str数据类型进行判断并按照json schema中对这个字段的约束条件进行填写\n
        [2.2]"DOI值"字段，当解剖学部位的出现DOI（浸润深度）的相关描述,则利用str数据类型进行判断并按照json schema中对这个字段的约束条件进行填写\n
        [2.3]"原发灶大小"，当解剖学部位出现解剖的原发灶大小的相关描述，则利用str数据类型进行判断并按照json schema中对这个字段的约束条件进行填写\n
        2."阳性淋巴结信息"字段，有两部分信息需要填写，填写这个字段需注意，"阳性淋巴结描述"这个字段一定要返回，需要计算其中的淋巴结数量\n
        [1] "阳性淋巴结描述"字段，里面包含 7 个字段：\n 
        [1.1] "阳性淋巴结清扫区域"字段，当出现清扫阳性淋巴结的区域的相关信息时，注意转换, 例如在 "I区左侧" 发现阳性淋巴结, 则填写为 "左1" 以此类推，利用 str 数据类型进行判断并填写。\n
        [1.2] "阳性颈清部位"字段，当出现阳性淋巴结的颈清部位的相关信息时，则利用 str 数据类型进行判断并按照 json schema 中对这个字段的约束条件进行填写。\n 
        [1.3] "阳性颈清侧位"字段，当出现阳性淋巴结的颈清侧位的相关信息时，则利用 str 数据类型进行判断并按照 json schema 中对这个字段的约束条件进行填写。\n 
        [1.4] "阳性淋巴结数量"字段，是指文本中出现阳性淋巴结的总数，需要进行计算利用整数类型（0-999）进行填写。 
        [1.5] "阳性颈清直径"字段，是指文中出现阳性淋巴结所出现的颈清直径，则利用 str 数据类型进行判断并按照 json schema 中对这个字段的约束条件进行填写。\n
        [1.6] "淋巴结数量"，是指在"阳性淋巴结分区描述"中"淋巴结"数量的和，需要进行计算，利用整数类型（0-999）进行填写。\n 
        [1.7] "胞膜外侵犯"字段，判断阳性淋巴结是否胞膜外侵犯，利用布尔类型（"true" / "false"）进行判断。\n
        [2] "阳性淋巴结分区描述"字段，包含5个子字段： 每个分区（I、II、III、IV、V）只有当阳性淋巴结出现在上述区域时，才填写所在区域的阳性淋巴结信息，下设 "左"、"右"、"不详" 三个字段，每个字段包括： \n[2.1] "阳性颈清直径"字段，选项为 "≤3"、"3-6 (>3)"、" >6"。 \n[2.2] "阳性淋巴结数量"字段，利用整数类型（0-999）进行填写。 \n[2.3] "胞膜外侵犯"字段，布尔类型（"true" / "false"）。\n
        3. "基本信息描述"字段中有5个子字段需要填写\n
        [1]分化信息、HPV、P16、切缘：从以下选项中选择一个值：`"阴性"`、`"阳性"`、`"无"`。  
        [2]神经侵犯、脉管侵犯：布尔值（`true` / `false`）。
        [标注数据]\n
        {input_text}\n
        [病例原文]\n
        {origin_text}\n
        [json schema]\n
        {json_schema}\n
        """

        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            AnatomicalSiteDescription_prompt = ""
            LymphNodeDescription_prompt = ""
            OtherDescription_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "解剖学部位":
                        if not group_data:
                            AnatomicalSiteDescription_prompt = basic_prompt.format(json_schema=AnatomicalSiteDescription_json,input_text="\" \"",origin_text=group_data) 
                        else:
                            input_text = group_data
                            AnatomicalSiteDescription_prompt = basic_prompt.format(json_schema=AnatomicalSiteDescription_json,input_text=input_text,origin_text=group_data)
                        
                    elif group_name == "淋巴结清扫区域":
                        if not group_data:
                            LymphNodeDescription_prompt = basic_prompt.format(json_schema=LymphNodeDescription_json,input_text="\" \"",origin_text=group_data)
                        else:
                            input_text = group_data
                            LymphNodeDescription_prompt = basic_prompt.format(json_schema=LymphNodeDescription_json,input_text=input_text,origin_text=group_data)
                    else:
                        if not group_data:
                            OtherDescription_prompt = basic_prompt.format(json_schema=OtherDescription_json,input_text="\" \"",origin_text=group_data)
                        else:
                            input_text = "\n".join(group_data)
                            OtherDescription_prompt = basic_prompt.format(json_schema=OtherDescription_json,input_text=input_text,origin_text=group_data)
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e

            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list":[AnatomicalSiteDescription_prompt, LymphNodeDescription_prompt, OtherDescription_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list


class CRFModel_Grs_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str,logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger
        self.grouped_label_data = super()._group_labels(label_list_dict, text_type)

    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> str:
        class PersonlHistory(HealthHistory):
            def __init__(self,**data):
                super().__init__(**data)

        PersonlHistory_json = cls._json_dumps_schema(PersonlHistory.model_json_schema())

        return [PersonlHistory_json]       
    
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        PersonlHistory_json = self._generate_group_json_schema()
        basic_prompt = """"### 任务\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的病理诊断的中文医疗文本进行信息抽取，需要标注的文本在最后，下面是标注的要求：\n### 要求\n1. 我将会给你一段标注后的文本数据，你需要从这些数据中抽取关键信息填写json schema\n2. 给你的实体标签如下：吸烟史,饮酒史,槟榔史\n3.若没有文本输入则全部判断为当前json schema 数据为空\n4.严格按照json shcema进行填写，不得出现填写非json schema的内容\n5.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n6.请你根据以上要求以及JSON schema对输入的文本进行信息抽取\nJSON schema 如下：\n{json_schema}\n### 输入文本\n{input_text}"""
        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            PersonlHistory_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "non_attr_entities":
                        if not group_data:
                            PersonlHistory_prompt = basic_prompt.format(json_schema=PersonlHistory_json,input_text="\" \"")
                        else:
                            input_text = group_data
                            PersonlHistory_prompt = basic_prompt.format(json_schema=PersonlHistory_json,input_text=input_text)
                    else:
                        break
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e
                
            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list": [PersonlHistory_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list 


class CRFModel_Hys_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str,logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger
        self.grouped_label_data = super()._group_labels(label_list_dict, text_type)

    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> str:
        class MarriageFertilityHistory_(MarriageFertilityHistory):
            def __init__(self,**data):
                super().__init__(**data)

        MarriageFertilityHistory_json = cls._json_dumps_schema(MarriageFertilityHistory_.model_json_schema())

        return MarriageFertilityHistory_json      
    
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        MarriageFertilityHistory_json = self._generate_group_json_schema()
        basic_prompt = """"### 任务\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的病理诊断的中文医疗文本进行信息抽取，需要标注的文本在最后，下面是标注的要求：\n### 要求\n1. 我将会给你一段标注后的文本数据，你需要从这些数据中抽取关键信息填写json schema\n2.给你的实体标签如下：婚姻状况,生育状况\n3.若没有文本输入则全部判断为当前json schema 数据为空\n4.严格按照json shcema进行填写，不得出现填写非json schema的内容\n5.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n6.请你根据以上要求以及JSON schema对输入的文本进行信息抽取\nJSON schema 如下：\n{json_schema}\n### 输入文本\n{input_text}"""
        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            MarriageFertilityHistor_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "non_attr_entities":
                        if not group_data:
                            MarriageFertilityHistor_prompt = basic_prompt.format(json_schema=MarriageFertilityHistory_json,input_text="\" \"")
                        else:
                            input_text = group_data
                            MarriageFertilityHistor_prompt = basic_prompt.format(json_schema=MarriageFertilityHistory_json,input_text=input_text)
                    else:
                        break
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e
                
            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list": [MarriageFertilityHistor_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list 

class CRFModel_Jws_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str,logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger
        self.grouped_label_data = super()._group_labels(label_list_dict, text_type)

    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> str:
        class MedicalHistory_(MedicalHistory):
            def __init__(self,**data):
                super().__init__(**data)

        MedicalHistory_json = cls._json_dumps_schema(MedicalHistory_.model_json_schema())

        return MedicalHistory_json      
    
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        MedicalHistory_json = self._generate_group_json_schema()
        basic_prompt = """[任务]\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的中文电子病历文本进行信息抽取，需要抽取信息的文本在最后，请按照[要求]的内容进行信息抽取：\n[要求]\n1. 我将会给你两部分数据，一部分数据是标注后的数据文本-[标注数据]，是由实体和属性组成的一段数据，组成的格式为"实体:属性"，其中如果没有":"连接就是只有实体没有属性，反之则既有实体又有属性。另一部分数据是病例原文-[病例原文]，你需要从这些数据中抽取关键信息填写json schema\n2. 给你的实体与属性如下：高血压,糖尿病,冠心病,血液系统疾病,其他肿瘤史,抗凝药物史\n3.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n4.严格按照json shcema每个条目的要求进行填写，不得出现填写非json schema的内容,json shcema的每个字段都需出现，请按照[填写要求]完成json schema的填写\n[填写要求]\n1."高血压"字段，若文中出现高血压的相关内容，则利用bool数据类型进行判断并填写\n2."糖尿病"字段，若文中出现糖尿病的相关内容，则利用bool数据类型进行判断并填写\n3."冠心病"字段，若文中出现冠心病的相关内容，则利用bool数据类型进行判断并填写\n4."血液系统疾病"字段，若文中出现血液系统疾病的记录或者病史的相关内容，则利用str数据类型进行判断并填写，若没有出现相关内容则用bool数据类型进行判断并填写\n5."抗凝药物史"字段，若文中出现抗凝药物史的记录或者病史的相关内容，则利用str数据类型进行判断并填写，若没有出现相关内容则用bool数据类型进行判断并填写\n6."其他肿瘤史"字段，若文中出除了口腔癌之外的肿瘤史记录或者病史的相关信息，则利用bool数据类型进行判断并填写\n[标注数据]\n{input_text}\n[病例原文]\n{origin_text}\n[json schema]\n{json_schema}\n"""
        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            MedicalHistory_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "non_attr_entities":
                        if not group_data:
                            MedicalHistory_prompt = basic_prompt.format(json_schema=MedicalHistory_json,input_text="\" \"",origin_text=group_text)
                        else:
                            input_text = group_data
                            MedicalHistory_prompt = basic_prompt.format(json_schema=MedicalHistory_json,input_text=input_text,origin_text=group_text)
                    else:
                        break
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e
                
            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list": [MedicalHistory_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list


class CRFModel_Xbs_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str, logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger

    @classmethod
    def _group_labels(cls,label_list_dict:Dict[str,Any], text_type:str) -> Dict[str, List[str]]:
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
        
    @classmethod
    def _recombine_grouped_label_data(cls,all_grouped_label_data:List[Dict[str, List[str]]]) -> List[Dict[str, Dict[str, List[str]]]]:
        recombined_all_grouped_label_data = []
        for item in all_grouped_label_data:
            text = item["text"]
            grouped_label_data = item["group_result"]
            recombined_grouped_label_data_item = {"non_attr_entities":[], "手术史":[], "放化疗史":[]}
            for key, value in grouped_label_data.items():
                if key == "non_attr_entities":
                    recombined_grouped_label_data_item[key] = value
                elif key == "既往口腔病灶切除史" or key == "既往颈淋巴结清扫史":
                    recombined_grouped_label_data_item["手术史"].extend(value)
                elif key == "既往化疗史" or key == "既往放疗史":
                    recombined_grouped_label_data_item["放化疗史"].extend(value)
            data_item = {
                "text": text,
                "group_result": recombined_grouped_label_data_item
            }
            recombined_all_grouped_label_data.append(data_item)
        return recombined_all_grouped_label_data
        
    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> Tuple[str, str, str]:
        class PastMedicalHistory(Part_PastMedicalHistory):
            def __init__(self,**data):
                super().__init__(**data)
  
        class OralMucosalHistory(Part_OralMucosalHistory):
            def __init__(self,**data):
                super().__init__(**data)
        PastMedicalHistory_json = cls._json_dumps_schema(PastMedicalHistory.model_json_schema())
        OralMucosalHistory_json = cls._json_dumps_schema(OralMucosalHistory.model_json_schema())
        return PastMedicalHistory_json, OralMucosalHistory_json
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        temp_data_group_result = self.match_grouped_label_data(alpaca_data)
        all_data_group_result = self._recombine_grouped_label_data(temp_data_group_result)
        # self.logger.info(all_data_group_result)
        PastMedicalHistory_json,OralMucosalHistory_json = self._generate_group_json_schema()
        basic_prompt = """[任务]\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的中文电子病历文本进行信息抽取，需要抽取信息的文本在最后，请按照[要求]的内容进行信息抽取：\n[要求]\n1. 我将会给你一段标注后的数据文本，是由实体和属性组成的一段数据，组成的格式为"实体:属性"，其中如果没有":"连接就是只有实体没有属性，反之则既有实体又有属性，你需要从这些数据中抽取关键信息填写json schema\n2. 给你的实体与属性如下：既往口腔病灶切除史,既往口腔病灶切除史:既往口腔病灶切除时间,既往颈淋巴结清扫史,既往颈淋巴结清扫史:既往颈淋巴结清扫时间,既往化疗史,既往化疗史:既往化疗时间,既往化疗史:既往化疗方案,既往化疗史:既往化疗次数,既往放疗史,既往放疗史:既往放疗时间,既往放疗史:既往放疗方式,既往放疗史:既往放疗次数,肿瘤病灶性质,既往黏膜病史\n3.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n4.严格按照json shcema每个条目的要求进行填写，不得出现填写非json schema的内容,json shcema的每个字段都需出现，请按照[填写要求]完成json schema的填写\n[填写要求]1."既往手术史"字段，若文中出现既往的手术记录的相关内容，则利用bool数据类型进行判断并填写\n2."既往化疗史"字段，若文中出现有关以往的化疗治疗的记录或者方案的内容，则利用bool数据类型进行判断并填写\n3."既往化疗史"字段，若文中出现有关以往的放疗治疗的记录或者方案的内容，则利用bool数据类型进行判断并填写\n4."既往口腔黏膜病史"字段，若文中出现以往的口腔黏膜病的记录或者病史的相关内容，则利用bool数据类型进行判断并填写\n5."既往颈清史"字段，若文中出现以往的颈部淋巴清扫的记录或者病史的相关内容，则利用bool数据类型进行判断并填写\n6."原发复发"字段，若文中出现该疾病的原发还是复发的相关信息，则利用str数据类型进行判断并填写\n7."复发时间"字段，若文中出现该疾病的复发时间的相关内容，则利用str数据类型进行判断并填写，若"原发复发"字段的描述信息是原发,则该字段可以判断为空\n[标注数据]\n{input_text}\n[病例原文]\n{origin_text}\n[json schema]\n{json_schema}"""
        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            SurgeryHistory_prompt = ""
            RadiationTherapyHistory_prompt = ""
            OralMucosalHistory_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "手术史" or group_name == "放化疗史":
                        if not group_data:
                            SurgeryHistory_prompt = basic_prompt.format(json_schema=PastMedicalHistory_json,input_text="\" \"",origin_text=group_text)
                        else:
                            input_text = group_data
                            SurgeryHistory_prompt = basic_prompt.format(json_schema=PastMedicalHistory_json,input_text=input_text,origin_text=group_text)
                    else:
                        if not group_data:
                            OralMucosalHistory_prompt = basic_prompt.format(json_schema=OralMucosalHistory_json,input_text="\" \"",origin_text=group_text)
                        else:
                            input_text = "\n".join(group_data)
                            OralMucosalHistory_prompt = basic_prompt.format(json_schema=OralMucosalHistory_json,input_text=input_text,origin_text=group_text)
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e

            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list":[SurgeryHistory_prompt, RadiationTherapyHistory_prompt, OralMucosalHistory_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list

class CRFModel_Yxjc_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str, logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger

    @classmethod
    def _recombine_grouped_label_data(cls,all_data_group_result:Dict[str, List[str]]) -> Dict[str, List[str]]:
        for item in all_data_group_result:
            group_result = item["group_result"]
            non_attr_entities = group_result.pop("non_attr_entities", [])
            for group_name, _ in group_result.items():
                if group_name == "阳性淋巴结区域":
                    item["group_result"][group_name].append(non_attr_entities)
                elif group_name == "病灶部位":
                    item["group_result"][group_name].append(non_attr_entities)

        return all_data_group_result
        
    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> Tuple[str, str, str]:
        class AnatomicalSiteDescription_image(Part_AnatomicalSiteDescription_image):
            def __init__(self,**data):
                super().__init__(**data)
        class LymphNodeDescription_image(Part_LymphNodeDescription_image):
            def __init__(self,**data):
                super().__init__(**data)
  
        AnatomicalSiteDescription_image_json = cls._json_dumps_schema(AnatomicalSiteDescription_image.model_json_schema())
        LymphNodeDescription_image_json = cls._json_dumps_schema(LymphNodeDescription_image.model_json_schema())
        return AnatomicalSiteDescription_image_json, LymphNodeDescription_image_json
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        all_data_group_result = self._recombine_grouped_label_data(all_data_group_result)
        # self.logger.info(all_data_group_result)
        AnatomicalSiteDescription_image_json,LymphNodeDescription_image_json = self._generate_group_json_schema()
        basic_prompt = """### 任务\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的病理诊断的中文医疗文本进行信息抽取，需要标注的文本在最后，下面是标注的要求：\n### 要求\n1. 我将会给你一段标注后的数据文本，是由实体和属性组成的一段数据，组成的格式为"实体:属性"你需要从这些数据中抽取关键信息填写json schema\n2. 给你的实体与属性如下：影像检查类型,阳性淋巴结区域,阳性淋巴结区域:阳性淋巴结大小,阳性淋巴结区域:阳性淋巴结个数,阳性淋巴结区域:阳性淋巴结方位,阳性淋巴结区域:阳性淋巴结描述,病灶部位,病灶部位:累及部位,病灶部位:病灶大小,病灶部位:病灶方位\n3.若没有提及"阳性LN数量"其个数就是为0，由于阳性淋巴结数量为0，因此所有区域均不符合记录条件，最终"阳性淋巴结描述信息"数组为空\n4.注意：淋巴结清扫区域:颈清直径中给的是一组范围的数据，通常以厘米为单位作为判断，例如"0.3-1.3cm",取其最大值"1.3cm"作为判断来填写json schema，注意在填写这一项时："≤3"是指颈清直径小于等于厘米，"≤6（＞3）"是指颈清直径大于3厘米小于等于6厘米，"＞6"是指颈清直径大于6厘米\n5.注意:病灶部位:病灶大小，通常以厘米为单位作为判断，取其最大值作为判断来填写json schema\n6.若没有文本输入则全部判断为当前json schema 数据为空\n7.严格按照json shcema进行填写，不得出现填写非json schema的内容\n8.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n9.请你根据以上要求以及JSON schema对输入的文本进行信息抽取\nJSON schema 如下：\n{json_schema}\n### 输入文本\n{input_text}"""
        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            AnatomicalSiteDescription_image_prompt = ""
            LymphNodeDescription_image_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "病灶部位":
                        if not group_data:
                            AnatomicalSiteDescription_image_prompt = basic_prompt.format(json_schema=AnatomicalSiteDescription_image_json,input_text="\" \"")
                        else:
                            input_text = group_data
                            AnatomicalSiteDescription_image_prompt = basic_prompt.format(json_schema=AnatomicalSiteDescription_image_json,input_text=input_text)
                    else:
                        if not group_data:
                            LymphNodeDescription_image_prompt = basic_prompt.format(json_schema=LymphNodeDescription_image_json,input_text="\" \"")
                        else:
                            input_text = group_data
                            LymphNodeDescription_image_prompt = basic_prompt.format(json_schema=LymphNodeDescription_image_json,input_text=input_text)
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e

            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list":[AnatomicalSiteDescription_image_prompt, LymphNodeDescription_image_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list

class CRFModel_Zkjc_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str, logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger

    @classmethod
    def _recombine_grouped_label_data(cls,all_data_group_result:Dict[str, List[str]]) -> Dict[str, List[str]]:
        for item in all_data_group_result:
            group_result = item["group_result"]
            non_attr_entities = group_result.pop("non_attr_entities", [])
            for group_name, _ in group_result.items():
                if group_name == "阳性淋巴结区域":
                    item["group_result"][group_name].append(non_attr_entities)
                elif group_name == "病灶部位":
                    item["group_result"][group_name].append(non_attr_entities)

        return all_data_group_result
        
    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> Tuple[str, str, str]:
        class AnatomicalSiteDescription_SE(Part_AnatomicalSiteDescription_SE):
            def __init__(self,**data):
                super().__init__(**data)
        class LymphNodeDescription_SE(Part_LymphNodeDescription_SE):
            def __init__(self,**data):
                super().__init__(**data)
  
        AnatomicalSiteDescription_SE_json = cls._json_dumps_schema(AnatomicalSiteDescription_SE.model_json_schema())
        LymphNodeDescription_SE_json = cls._json_dumps_schema(LymphNodeDescription_SE.model_json_schema())
        return AnatomicalSiteDescription_SE_json, LymphNodeDescription_SE_json
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        all_data_group_result = self._recombine_grouped_label_data(all_data_group_result)
        # self.logger.info(all_data_group_result)
        AnatomicalSiteDescription_SE_json,LymphNodeDescription_SE_json = self._generate_group_json_schema()
        basic_prompt = """### 任务\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的病理诊断的中文医疗文本进行信息抽取，需要标注的文本在最后，下面是标注的要求：\n### 要求\n1. 我将会给你一段标注后的数据文本，是由实体和属性组成的一段数据，组成的格式为"实体:属性"你需要从这些数据中抽取关键信息填写json schema\n2. 给你的实体与属性如下：阳性淋巴结区域,阳性淋巴结区域:阳性淋巴结大小,阳性淋巴结区域:阳性淋巴结个数,阳性淋巴结区域:阳性淋巴结方位,阳性淋巴结区域:阳性淋巴结描述,病灶部位,病灶部位:病灶大小,病灶部位:病灶方位,病灶部位:累及部位\n3.若没有提及"阳性淋巴结个数"其个数就是为0，由于阳性淋巴结数量为0，因此所有区域均不符合记录条件，最终"阳性淋巴结描述信息"数组为空\n4.注意：淋巴结清扫区域:颈清直径中给的是一组范围的数据，通常以厘米为单位作为判断，例如"0.3-1.3cm",取其最大值"1.3cm"作为判断来填写json schema，注意在填写这一项时："≤3"是指颈清直径小于等于厘米，"≤6（＞3）"是指颈清直径大于3厘米小于等于6厘米，"＞6"是指颈清直径大于6厘米\n5.注意:病灶部位:病灶大小，通常以厘米为单位作为判断，取其最大值作为判断来填写json schema\n6.若没有文本输入则全部判断为当前json schema 数据为空\n7.严格按照json shcema进行填写，不得出现填写非json schema的内容\n8.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n9.请你根据以上要求以及JSON schema对输入的文本进行信息抽取\nJSON schema 如下：\n{json_schema}\n### 输入文本\n{input_text}"""
        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            AnatomicalSiteDescription_SE_prompt = ""
            LymphNodeDescription_SE_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "病灶部位":
                        if not group_data:
                            AnatomicalSiteDescription_SE_prompt = basic_prompt.format(json_schema=AnatomicalSiteDescription_SE_json,input_text="\" \"")
                        else:
                            input_text = group_data
                            AnatomicalSiteDescription_SE_prompt = basic_prompt.format(json_schema=AnatomicalSiteDescription_SE_json,input_text=input_text)
                    else:
                        if not group_data:
                            LymphNodeDescription_SE_prompt = basic_prompt.format(json_schema=LymphNodeDescription_SE_json,input_text="\" \"")
                        else:
                            input_text = group_data
                            LymphNodeDescription_SE_prompt = basic_prompt.format(json_schema=LymphNodeDescription_SE_json,input_text=input_text)
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e

            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list":[AnatomicalSiteDescription_SE_prompt, LymphNodeDescription_SE_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list



class CRFModel_Ssjl_Prompter(CRFModel):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str, logger:CustomLogger):
        super().__init__(label_list_dict, text_type)
        self.text_type = text_type
        self.logger = logger

    @classmethod
    def _recombine_grouped_label_data(cls,all_data_group_result:Dict[str, List[str]]) -> Dict[str, List[str]]:
        for item in all_data_group_result:
            group_result = item["group_result"]
            group_result.pop("主要病变",[])
            group_result.pop("移除处理",[])
            for key in list(group_result.keys()):
                if key != "non_attr_entities":
                    group_result["non_attr_entities"].extend(group_result.pop(key))
        return all_data_group_result
        
    @classmethod
    def _json_dumps_schema(cls,json_schema:Dict[str, Any]) -> str:
        return json.dumps(json_schema, indent=2, ensure_ascii=False)
    
    @classmethod
    def _generate_group_json_schema(cls) -> Tuple[str, str, str]:
        class SurgeryRecord_(SurgeryRecord):
            def __init__(self,**data):
                super().__init__(**data)
  
        SurgeryRecord_json = cls._json_dumps_schema(SurgeryRecord_.model_json_schema())

        return SurgeryRecord_json
    
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]]) -> str:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        all_data_group_result = self._recombine_grouped_label_data(all_data_group_result)
        # self.logger.info(all_data_group_result)
        SurgeryRecord_json = self._generate_group_json_schema()

        basic_prompt = """[任务]\n请你使用中文回答，你是一位出色的信息抽取专家，目前需要对关于口腔鳞状细胞癌的中文电子病历文本进行信息抽取，需要抽取信息的文本在最后，请按照[要求]的内容进行信息抽取：\n[要求]\n1. 我将会给你一段标注后的数据文本，是由实体和属性组成的一段数据，组成的格式为"实体:属性"，其中如果没有":"连接就是只有实体没有属性，反之则既有实体又有属性，你需要从这些数据中抽取关键信息填写json schema\n2. 给你的实体与属性如下：手术名称,术后患者去向,修复重建技术,修复重建技术：材料大小,修复重建技术：材料来源,修复重建技术：修复重建部位,出血标志,出血标志：出血量\n3.给你的文本是一组python 的list[list[str]],每一组list[str]都是这个组的内容，请综合填写\n4.严格按照json shcema每个条目的要求进行填写，不得出现填写非json schema的内容,json shcema的每个字段都需出现，请按照[填写要求]完成json schema的填写\n[填写要求]\n1."颈部淋巴清扫"字段，若文中没有出现颈部淋巴清扫的相关内容，则利用bool数据类型进行判断并填写，若文中出现颈部淋巴清扫的相关内容，则利用str数据类型填写相关的内容\n2."皮瓣修复"字段，若文中出现有关皮瓣修复的内容，则利用bool数据类型进行判断并填写\n3."气切"字段，若文中出现气管切开的相关信息，则利用bool数据类型进行判断并填写\n4."输血"字段，若文中出现与输血相关的信息，则利用bool数据类型进行判断并填写\n5."ICU"字段，若文中出现病患的最终去处有ICU的相关内容，则利用bool数据类型进行判断并填写\n[标注数据]\n{input_text}\n[病例原文]\n{origin_text}\n[json schema]\n{json_schema}"""
        all_prompt_list = []
        for item in all_data_group_result:
            group_text = item["text"]
            group_data = item["group_result"]
            SurgeryRecord_prompt = ""
            try:
                for group_name, group_data in group_data.items():
                    if group_name == "non_attr_entities":
                        if not group_data:
                            SurgeryRecord_prompt = basic_prompt.format(json_schema=SurgeryRecord_json,input_text="\" \"", origin_text=group_text)
                        else:
                            input_text = group_data
                            SurgeryRecord_prompt = basic_prompt.format(json_schema=SurgeryRecord_json,input_text=input_text, origin_text=group_text)
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.logger.error(f"Error occurred in group_text: {group_text}")
                raise e

            single_text_part_prompt_dict = {
                "group_text": group_text,
                "prompt_list":[SurgeryRecord_prompt]
            }
            all_prompt_list.append(single_text_part_prompt_dict)

        return all_prompt_list