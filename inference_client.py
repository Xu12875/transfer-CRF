import re
from openai import OpenAI, AzureOpenAI
from typing import List, Dict, Tuple, Any, Optional
from logger import CustomLogger
from transformers import AutoTokenizer

## local inference model
class InferenceClient:
    def __init__(self, model_name: str, api_key: str, base_url: str):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.client = self._initialize_client()

    def _initialize_client(self):
        openai_sdk = OpenAI(
            api_key = self.api_key, 
            base_url = self.base_url
        )
        return openai_sdk


class local_inference_client(InferenceClient):
    def __init__(self, model_name:str, api_key:str, base_url:str, clogger:CustomLogger):
        self.clogger = clogger
        super().__init__(model_name=model_name, api_key=api_key, base_url=base_url)
        super()._initialize_client()
        self.client = self._initialize_client()
        # self.model_name = model_name
    
    @classmethod
    def _get_reasoning_content(self, response:str) -> str:
        reasoning_content = ''
        think_start_idx = response.find('<think>')
        think_end_idx = response.find('</think>')
        if think_start_idx != -1 and think_end_idx != -1:
            reasoning_content = response[think_start_idx:think_end_idx]
            reasoning_content = re.sub('<think>', '', reasoning_content)
            reasoning_content = re.sub('</think>', '', reasoning_content)
        return reasoning_content

    @classmethod
    def _get_answer(self, response: str) -> str:
        answer_content = ''
        answer_start_idx = response.find(r"```json")
        answer_end_idx = response.find(r"```", answer_start_idx + 1)
        if answer_start_idx != -1 and answer_end_idx != -1:
            answer_content = response[answer_start_idx:answer_end_idx]
            answer_content = re.sub(r'```json', '', answer_content)
            answer_content = re.sub(r'```', '', answer_content)
        return answer_content

    def get_tokenizer(self):
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            return tokenizer
        except Exception as e:
            self.clogger.error(f"Failed to load tokenizer for model {self.model_name}: {e}")
            return None

    def get_response(self, prompt: str, **kwargs) -> Tuple[str, str, str]:
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                # qwen3 no-thinking
                extra_body={
                    # "top_k": 20, 
                    "chat_template_kwargs": {"enable_thinking": False},
                },
                **kwargs
            )
            response = completion.choices[0].message.content
            self.clogger.info(f"Response: {response}")
            answer_content = self._get_answer(response)
            reasoning_content = self._get_reasoning_content(response)
            # self.clogger.info(f"answer_content: {answer_content}, reasoning_content: {reasoning_content}")
            return reasoning_content, answer_content
        except Exception as e:
            self.clogger.error(f"Error occurred: {e}")
            self.clogger.error(f"answer_content: {answer_content}, reasoning_content: {reasoning_content}")
            return None, None
  

class online_inference_client(InferenceClient):
    ### QWQ-32B online inferece -> https://dashscope.aliyuncs.com/compatible-mode/v1
    def __init__(self, model_name:str, api_key:str, base_url:str, clogger:CustomLogger,Azure_interface:Optional[bool]):
        self.Azure_interface = Azure_interface 
        self.clogger = clogger
        super().__init__(model_name=model_name, api_key=api_key, base_url=base_url)
        # self.model_name = model_name
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        if self.Azure_interface:
            self.clogger.info("Initializing Azure OpenAI Client...")
            openai_Azure_sdk = AzureOpenAI(
                azure_endpoint = self.base_url,
                api_key = self.api_key,
                api_version = "2024-02-01"
            )
            return openai_Azure_sdk
        else:
            self.clogger.info("Initializing Default OpenAI Client...")
            return super()._initialize_client()
        
    @classmethod
    def _process_answer_content(self, response:str) -> str:
        answer_content = ''
        try:
            answer_start_idx = response.find(r"```json")
            answer_end_idx = response.find(r"```", answer_start_idx + 1)
            if answer_start_idx != -1 and answer_end_idx != -1:
                answer_content = response[answer_start_idx:answer_end_idx]
                answer_content = re.sub(r'```json', '', answer_content)
                answer_content = re.sub(r'```', '', answer_content)
                return answer_content
        except Exception as e:
            self.clogger.error(f"Error processing answer content: {e}")
            self.clogger.error(f"Response content: {response}")

    def _combine_ChunkResponse_(self,completion) -> Tuple[str, str]:
        if self.Azure_interface:
            reasoning_content = ""
            answer_content = ""
            response = completion.choices[0].message.content
            # print(response)
            answer_content = self._process_answer_content(response)
            # print(answer_content)
            return reasoning_content,answer_content
        
        else:
            try:
                reasoning_content = ""
                answer_content = ""     
                is_answering = False  

                if hasattr(completion, '__iter__'):
                    for chunk in completion:
                        if not chunk.choices:
                            continue
                        else:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                                reasoning_content += delta.reasoning_content
                            else:
                                if delta.content != "" and is_answering is False:
                                    is_answering = True
                                # print(delta.content, end='', flush=True)
                                answer_content += delta.content
                    answer_content = self._process_answer_content(answer_content)
                    return reasoning_content, answer_content
                
                else:
                    response = completion.choices[0].message.content
                    # print(response)
                    answer_content = self._process_answer_content(response)
                    # print(answer_content)
                    return reasoning_content,answer_content
                
            except Exception as e:
                self.clogger.error(f"Error occurred: {e}")
                return None, None
                

    def get_response(self, prompt:str, **kwargs)-> Tuple[str, str]:
        try:
            completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user", 
                    "content": f"{prompt}"
                }
            ],
            stream = True,
            **kwargs
            )
            reasoning_content,answer_content = self._combine_ChunkResponse_(completion)
            return reasoning_content,answer_content
        except Exception as e:
            self.clogger.error(f"Error occurred: {e}")
            return None, None 