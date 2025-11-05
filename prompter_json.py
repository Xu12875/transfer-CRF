import json
import os
from typing import List, Dict, Tuple, Any, Optional
from logger import CustomLogger
from prompt_info.base_json.CReDEs_Prompter import BasePrompter
from transformers import AutoTokenizer
from tqdm import tqdm
from string import Template
from inference_client import local_inference_client
from utils import process_answer_content_to_json
from abc import ABC, abstractmethod


class CRCDEsModel(ABC):
    @abstractmethod
    def get_process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Interface method to be implemented by subclasses -> get grouped entity data 
        pass


class CRCDEsModel_PreGroup(CRCDEsModel):
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
                labeled_article_id = item.get("article_id","")
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
                single_data_dict = {
                    "article_id": labeled_article_id,
                    "text": labeled_origin_text,
                    "entity_grouped_result": group_result
                }
                all_data_group_result.append(single_data_dict)
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

    def get_process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.match_grouped_label_data(data)


class CRCDEsModel_PostGroup(CRCDEsModel):
    def __init__(self,entity_grouped_prompt:str,inference_logger:CustomLogger,inference_client:local_inference_client):
        self.entity_grouped_prompt = entity_grouped_prompt
        self.inference_logger = inference_logger
        self.inference_client = inference_client

    def _construct_post_process_grouped_prompt(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Implement post-grouping prompt construction logic here
        prompt_info_list = []
        for item in data:
            article_id = item.get("article_id","")
            origin_text = item.get("input","")
            inference_output = item.get("output","")
            process_prompt = self.entity_grouped_prompt.format(
                origin_text=origin_text,
                annotation_text=inference_output
            )
            prompt_dict = {
                "article_id": article_id,
                "text": origin_text,
                "prompt": process_prompt
            }

            prompt_info_list.append(prompt_dict)
        return prompt_info_list

    def _process_grouped_entity_prompt_to_client(self, all_prompt_list: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        grouped_entity_alpaca_data_list = []
        for index, item in enumerate(tqdm(all_prompt_list, desc='Processing Entity Grouped Prompts', total=len(all_prompt_list), unit='prompts')):
            article_id = item.get('article_id', "")
            text = item.get('text', "")
            prompt = item.get('prompt')
            try:
                _, answer_content = self.inference_client.get_response(prompt, **kwargs)
                # print(f"response: {_}")
                # print(f"answer_content: {answer_content}")
                try:
                    answer_json = process_answer_content_to_json(str(answer_content))
                except json.JSONDecodeError:
                    self.inference_logger.error(f"Failed to decode JSON from inference_client response: \n{answer_content}")
                    continue
                self.inference_logger.info(f"Processed Entity Grouped num {index+1} prompt")
                self.inference_logger.info(f"processed part: {answer_json}")

                entity_grouped_info = {
                    'article_id': article_id,
                    'text': text,
                    'entity_grouped_result': answer_json
                }
                grouped_entity_alpaca_data_list.append(entity_grouped_info)
            except Exception as e:
                self.inference_logger.error(f"Error processing prompt article_id:{article_id}: {e}")
                self.inference_logger.error(f"Unexpected response format from inference_client.get_response: \n{prompt}")
                continue

        return grouped_entity_alpaca_data_list

    def get_process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_prompt_list = self._construct_post_process_grouped_prompt(data)
        grouped_entity_data = self._process_grouped_entity_prompt_to_client(all_prompt_list)
        return grouped_entity_data
        

class CRCDEs_Prompter(ABC):
    @abstractmethod
    def generate_prompt(self,alpaca_data:List[Dict[str, Any]],grouped:bool=False) -> List[Dict[str, Any]]:
        pass


class CRCDEs_Prompter_Pre(CRCDEs_Prompter,CRCDEsModel_PreGroup):
    def __init__(self, label_list_dict:Dict[str,List[str]], text_type:str, 
                 basic_prompt:str,logger:CustomLogger,baseprompter_obj:BasePrompter,
                 tokenizer:AutoTokenizer,max_token_len:int):
        super().__init__(label_list_dict, text_type)
        self.logger = logger
        self.basic_prompt = basic_prompt
        self.baseprompter = baseprompter_obj #update: BasePrompter 
        self.tokenizer = tokenizer
        self.max_token_len = max_token_len
        #fixed: pre-grouped label data
        self.grouped_label_data = super()._group_labels(label_list_dict, text_type)
    
    def _get_base_prompt_dict(self, only_json:bool=False) -> Dict[str, str]:
        return self.baseprompter.get_group_prompt_dict(only_json)
    
    def _substr_json(self,json_prompt:str) -> str:
        """
        ```json
        {
            "foo": List[string],  // a list of strings
            "bar": string  // a string
        }
        ```
        """
        temp_json_str = str(json_prompt).split("```json")[1].split("```")[0]
        col_str = str(temp_json_str).split("\n{")[1].split("\n}")[0]
        lines =  col_str.splitlines()
        return [line for line in lines if line.strip()]      


    def _process_grouped_json(self,prompt_group_json:List[str]) -> str:
        json_str_format = """```json\n{{\n{combine_json_str}\n}}\n```"""
        json_prompt_list = []
        for json_prompt in prompt_group_json:
            json_prompt_list.extend(self._substr_json(json_prompt))
        combine_json_str = "\n".join(json_prompt_list)
        return json_str_format.format(combine_json_str=combine_json_str)

    
    def _grouped_data(self, data_json_list: List[Dict[str, Any]]) -> List[str]:
        prompt_list = []
        current_group_data = []
        current_group_json = []
        current_origin_text = ""
        
        for item in data_json_list:
            group_data = item.get("group_data", [])
            json_prompt = item.get("json_prompt", "")
            origin_text = item.get("text", "")
            
            temp_group_data = current_group_data + group_data
            temp_group_json = current_group_json + [json_prompt]
            temp_prompt = self.basic_prompt.format(
                origin_text=origin_text,
                annotation_text=temp_group_data,
                grouped_json=self._process_grouped_json(temp_group_json)
            )
            token_count = len(self.tokenizer(temp_prompt)["input_ids"])
            
            ## token limit -> max_token_len/2 (could be adjusted)
            if token_count <= (self.max_token_len)/2:
                current_group_data = temp_group_data
                current_group_json = temp_group_json
                current_origin_text = origin_text
            else:
                if current_group_data:
                    final_prompt = self.basic_prompt.format(
                        origin_text=current_origin_text,
                        annotation_text=current_group_data,
                        grouped_json=self._process_grouped_json(current_group_json)
                    )
                    prompt_list.append(final_prompt)
                current_group_data = group_data
                current_group_json = [json_prompt]
                current_origin_text = origin_text

        if current_group_data:
            final_prompt = self.basic_prompt.format(
                origin_text=current_origin_text,
                annotation_text=current_group_data,
                grouped_json=self._process_grouped_json(current_group_json)
            )
            prompt_list.append(final_prompt)

        return prompt_list


    def generate_prompt(self,alpaca_data:List[Dict[str, Any]],grouped:bool=False) -> List[Dict[str, Any]]:
        all_data_group_result = self.match_grouped_label_data(alpaca_data)
        # self.logger.info(all_data_group_result)
        grouped_prompt_dict = self._get_base_prompt_dict(grouped)
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
            try:
                if grouped:
                    ## group optimization and only json
                    ## prompt_key = group_name
                    data_json_list = []                        
                    for prompt_key, _ in grouped_prompt_dict.items():
                        # for group_name, group_data in group_result.items():
                            json_unit_prompt = grouped_prompt_dict[prompt_key]
                            data_json_dict = {
                                "text": origin_text,
                                "group_data":group_result[prompt_key],
                                "json_prompt":json_unit_prompt
                            }
                            data_json_list.append(data_json_dict)

                    # grouped_prompt
                    single_part_prompt_dict["prompt_list"] = self._grouped_data(data_json_list)
                else:
                    for group_name, group_data in group_result.items():
                        # Loop format each key in basic prompt (every key)
                        for prompt_key, _ in grouped_prompt_dict.items():
                            basic_prompt = ''
                            json_unit_prompt = ''
                            # Loop format each key in basic prompt (every key)
                            ## prompt_list contain all the key in basic prompt(not grouped)
                            # if prompt_key in grouped_prompt_dict:
                            json_unit_prompt = f"{grouped_prompt_dict[prompt_key]}"
                            basic_prompt = self.basic_prompt.format(
                                origin_text=origin_text,
                                annotation_text=group_data, 
                                grouped_json=json_unit_prompt
                                )
                            single_part_prompt_dict["prompt_list"].append(basic_prompt)
            except Exception as e:
                self.logger.error(f"Error processing item {item}: {e}")
                continue
            all_prompt_list.append(single_part_prompt_dict)

        return all_prompt_list


class CRCDEs_Prompter_Post(CRCDEs_Prompter,CRCDEsModel_PostGroup):
    def __init__(self,grouped_entity_data:List[Dict[str, Any]],text_type:str, 
                 crcdes_prompt:str,logger:CustomLogger,
                 baseprompter_obj:BasePrompter,
                 tokenizer:AutoTokenizer,max_token_len:int):
        self.grouped_entity_data = grouped_entity_data
        self.text_type = text_type
        self.logger = logger
        self.crcdes_prompt = crcdes_prompt
        self.baseprompter = baseprompter_obj 
        self.tokenizer = tokenizer
        self.max_token_len = max_token_len

    def _get_target_grouped_QA_json(self) -> List[List[str]]:
        grouped_QA_json_dict = self.baseprompter.get_group_prompt_dict()
        target_grouped_QA_json_list = grouped_QA_json_dict.get(self.text_type, [])
        return target_grouped_QA_json_list
    

    def _split_questions_by_token_limit(self,questions: List[str], base_template: str, limit: int) -> List[str]:
        """
        按 token 数量拆分 questions 列表，每个拆分块不超过 max_token_len
        """
        chunks = []
        current_chunk = []
        for q in questions:
            candidate_chunk = current_chunk + [q]
            temp_prompt = base_template.format(questions="\n".join(candidate_chunk))
            token_count = len(self.tokenizer(temp_prompt)["input_ids"])
            if token_count <= limit:
                current_chunk.append(q)
            else:
                if current_chunk:
                    chunks.append(base_template.format(questions="\n".join(current_chunk)))
                # 如果单条问题太长，直接单独生成
                temp_prompt = base_template.format(questions=q)
                token_count = len(self.tokenizer(temp_prompt)["input_ids"])
                if token_count <= limit:
                    current_chunk = [q]
                else:
                    chunks.append(temp_prompt)
                    current_chunk = []
        if current_chunk:
            chunks.append(base_template.format(questions="\n".join(current_chunk)))
        return chunks

    def generate_prompt(self, grouped: bool = False) -> List[Dict[str, Any]]:
        target_grouped_QA_json_lists = self._get_target_grouped_QA_json()
        all_prompt_list = []

        for item in self.grouped_entity_data:
            article_id = item.get("article_id", "")
            origin_text = item.get("text", "")
            entity_grouped_result = item.get("entity_grouped_result", "")

            # safe str for adopting json format
            safe_origin_text = str(origin_text).replace("{", "{{").replace("}", "}}")
            safe_grouped_entity_text = json.dumps(entity_grouped_result, ensure_ascii=False).replace("{", "{{").replace("}", "}}")

            # basic prompt -> except {questions}
            base_template = self.crcdes_prompt.format(
                origin_text=safe_origin_text,
                grouped_entity_text=safe_grouped_entity_text,
                questions="questions_replace_str"
            )

            prompt_list: List[str] = []

            for grouped_QA_json_list in target_grouped_QA_json_lists:
                if grouped:
                    prompts = self._split_questions_by_token_limit(
                        grouped_QA_json_list,
                        base_template,
                        self.max_token_len // 2
                    )
                    prompt_list.extend(prompts)
                else:
                    # Replace literal \n in JSON strings with actual newlines for proper formatting
                    grouped_QA_str = "\n".join([q.replace('\\n', '\n') for q in grouped_QA_json_list])
                    prompt_list.append(base_template.replace('questions_replace_str', grouped_QA_str))

            all_prompt_list.append({
                "article_id": article_id,
                "text": origin_text,
                "prompt_list": prompt_list
            })

        return all_prompt_list