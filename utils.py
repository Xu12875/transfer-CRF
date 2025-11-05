import json
import os
import time
from tqdm import tqdm
from typing import List, Dict, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from json_repair import repair_json
from functools import wraps



def load_alpaca_data(file_path:str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_config(file_path:str) -> Dict[str, Any]:
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
        try:
            repaired_json = repair_json(answer_content)
            return json.loads(repaired_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parse error after repair: {e}")
    


## process multi request to inference server ==> max-workers = workers 
def process_prompt_to_client(
    all_prompt_list: List[Dict[str, Any]],
    inference_client: Any,
    inference_logger: Any,
    max_workers: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:

    CRCDEs_alpaca_data = []

    def process_single_prompt(index: int, item: Dict[str, Any]) -> Dict[str, Any]:
        combine_response_dict = {}
        article_id = item.get('article_id', "")
        text = item.get('group_text', "")
        prompt_list = item.get('prompt_list', [])

        for prompt in prompt_list:
            try:
                _, answer_content = inference_client.get_response(prompt, **kwargs)
                answer_json = process_answer_content_to_json(str(answer_content))

                # 累积相同 key
                for key, value in answer_json.items():
                    if key in combine_response_dict:
                        if isinstance(combine_response_dict[key], list):
                            combine_response_dict[key].append(value)
                        else:
                            combine_response_dict[key] = [combine_response_dict[key], value]
                    else:
                        combine_response_dict[key] = value

                inference_logger.info(f"current prompt: {prompt}")
                inference_logger.info(f"Processed prompt {index+1}/{len(all_prompt_list)}")
                inference_logger.info(f"Current keys: {list(combine_response_dict.keys())}")

            except Exception as e:
                inference_logger.error(f"Error processing prompt {index+1}: {e}")
                inference_logger.info(f"Last answer content: {answer_content if 'answer_content' in locals() else 'N/A'}")
                continue

        return {
            'article_id': article_id,
            'text': text,
            'output': combine_response_dict
        }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_prompt, i, item): i for i, item in enumerate(all_prompt_list)}
        for future in tqdm(as_completed(futures), desc='Processing Prompts', total=len(all_prompt_list), unit='prompts'):
            try:
                result = future.result()
                CRCDEs_alpaca_data.append(result)
            except Exception as e:
                inference_logger.error(f"Error in thread execution: {e}")

    return CRCDEs_alpaca_data


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行耗时: {end_time - start_time:.2f} 秒")
        return result
    return wrapper