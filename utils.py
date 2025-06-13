import json
import os
from tqdm import tqdm
from typing import List, Dict, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def load_alpaca_data(file_path:str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def  load_config(file_path:str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def makedirs(dir_path:str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        pass

def save_alpaca_data(data:List[Dict[str, Any]], store_dir:str, file_name:str):
    if not os.path.exists(store_dir):
        makedirs(store_dir)
    file_path = os.path.join(store_dir, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {file_path}")

def process_answer_content_to_json(answer_content: str) -> Dict[str, Any]:
    try:
        return json.loads(answer_content)
    except json.JSONDecodeError:
        pass
    try:
        # 1. clean // comment
        lines = answer_content.splitlines()
        no_comment_lines = [re.sub(r'//.*', '', line) for line in lines]
        text = '\n'.join(no_comment_lines)

        # 2. fix key-value "key: "value" -> "key": "value"
        # 
        text = re.sub(r'"([^"]+):""([^"]+)""', r'"\1": "\2"', text)

        # 3. add "" 
        text = re.sub(
            r'(?<!")\b([a-zA-Z0-9_\u4e00-\u9fa5]+)\b(?=\s*:)', r'"\1"', text
        )

        # 4. remove last item ","
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        # 5. parse json
        return json.loads(text)

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse error：{e}")
    

## process single request to inference server
def process_prompt_to_client_single(all_prompt_list: List[Dict[str, Any]], inference_client: Any, inference_logger: Any, **kwargs) -> List[Dict[str, Any]]:
    CRF_alpaca_data = []

    for index, item in enumerate(tqdm(all_prompt_list, desc='Processing Prompts', total=len(all_prompt_list), unit='prompts')): 
        combine_response_dict = {}
        article_id = item.get('article_id', "")
        instruction = ""
        text = item.get('group_text', "")
        prompt_list = item.get('prompt_list', [])

        for prompt in prompt_list:
            try:
                _, answer_content = inference_client.get_response(prompt, **kwargs)
                # print(f"response: {_}")
                # print(f"answer_content: {answer_content}")
                answer_json = process_answer_content_to_json(str(answer_content))
                
                inference_logger.info(f"Processed num {index+1} prompt")
                for key, value in answer_json.items():
                    combine_response_dict[key] = value
                    # if key in combine_response_dict:
                    #     if isinstance(combine_response_dict[key], list):
                    #         combine_response_dict[key].append(value)
                    #     else:
                    #         combine_response_dict[key] = [combine_response_dict[key], value]
                    # else:
                    #     combine_response_dict[key] = value
                inference_logger.info(f"processed part: {combine_response_dict.keys()}")
                
            except Exception as e:
                inference_logger.error(f"Error: {e}")
                inference_logger.error(f"Unexpected response format from inference_client.get_response: \n{prompt}")
                continue
            except json.JSONDecodeError:
                inference_logger.error(f"Failed to decode JSON from inference_client response: \n{answer_content}")
                continue
        
        CRF_alpaca_data.append(
            {   
                'article_id': article_id,
                'instruction': instruction,
                'input': text,
                'output': combine_response_dict
            }
        )
        inference_logger.info(f"Processing complete for input: {index+1} prompt")
        inference_logger.info(f"data lenth: {len(CRF_alpaca_data)}")

    return CRF_alpaca_data


## process multi request to inference server ==> max-workers = workers 
def process_prompt_to_client(all_prompt_list: List[Dict[str, Any]], inference_client: Any, inference_logger: Any, max_workers: int = 50, **kwargs) -> List[Dict[str, Any]]:
    CRF_alpaca_data = []
    
    def process_single_prompt(index, item):
        combine_response_dict = {}
        article_id = item.get('article_id', "")
        instruction = ""
        text = item.get('group_text', "")
        prompt_list = item.get('prompt_list', [])

        for prompt in prompt_list:
            try:
                _, answer_content = inference_client.get_response(prompt, **kwargs)
                answer_json = process_answer_content_to_json(str(answer_content))

                for key, value in answer_json.items():
                    combine_response_dict[key] = value
                    # if key in combine_response_dict:
                    #     if isinstance(combine_response_dict[key], list):
                    #         combine_response_dict[key].append(value)
                    #     else:
                    #         combine_response_dict[key] = [combine_response_dict[key], value]
                    # else:
                    #     combine_response_dict[key] = value
                # inference_logger.info(f"Processed prompt {prompt}")        
                inference_logger.info(f"Processed num {index+1} prompt")
                inference_logger.info(f"processed part: {combine_response_dict.keys()}")

            except Exception as e:
                inference_logger.error(f"Error processing prompt {index+1}: {e}")
                inference_logger.info(f"processed part: {answer_content}")
                continue
        
        return {
            'article_id': article_id,
            'instruction': instruction,
            'input': text,
            'output': combine_response_dict
        }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {executor.submit(process_single_prompt, i, item): i for i, item in enumerate(all_prompt_list)}
        for future in tqdm(as_completed(future_to_index), desc='Processing Prompts', total=len(all_prompt_list), unit='prompts'):
            try:
                result = future.result()
                CRF_alpaca_data.append(result)
            except Exception as e:
                inference_logger.error(f"Error in thread execution: {e}")
    
    return CRF_alpaca_data
