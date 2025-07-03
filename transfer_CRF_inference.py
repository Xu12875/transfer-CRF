from json import load
import os
from inference_client import local_inference_client,online_inference_client
from typing import List, Dict, Any, Tuple, Optional, Union, Type
from logger import CustomLogger
from prompter import LABEL_LIST_DICT,CRFModel_Blzd_Prompter, CRFModel_Grs_Prompter,CRFModel_Hys_Prompter,CRFModel_Jws_Prompter,CRFModel_Ssjl_Prompter,CRFModel_Xbs_Prompter,CRFModel_Yxjc_Prompter,CRFModel_Zkjc_Prompter,CRFModel
from prompter_json import BASIC_PROMPT, CReDEsModel,LABEL_LIST_DICT_JSON,CReDEs_Prompter
from prompt_info.base_json.CReDEs_Prompter import FileProcessor,BasePrompter
from utils import load_alpaca_data, load_config, process_prompt_to_client, save_alpaca_data


def transfer_inference(inference_client_cls: Union[Type[local_inference_client], 
Type[online_inference_client]], 
                       prompter_cls: Union[Type[CReDEsModel], Type[CRFModel]], 
                       text_type: str,
                       label_list_dicts: Dict[str, Any],
                       prompter_logger: CustomLogger,
                       client_logger: CustomLogger,
                       inference_logger: CustomLogger,
                       config_file_path: str,
                       baseprompter: Optional[Type[BasePrompter]] = None) -> List[Dict[str, Any]]:
    ## load config
    config = load_config(config_file_path)

    if not issubclass(inference_client_cls, (local_inference_client, online_inference_client)):
        raise TypeError("Invalid inference client type")

    ## model params
    if inference_client_cls == local_inference_client:
        ## load local model config
        local_inference_config = config['local_inference']
        model_config = local_inference_config['model_config']
        model_name = model_config['model_name']
        base_url = model_config['base_url']
        api_token = model_config['api_token']
        temperature = model_config['temperature']

        ## setup local inference client
        local_inference_client_setup = inference_client_cls(model_name=model_name, base_url=base_url, api_key=api_token, clogger=client_logger)
        
        ## setup prompter and load data
        data_config =local_inference_config['data']
        alpaca_data = load_alpaca_data(data_config['transfer_data_path'][text_type])
        print(f"load {len(alpaca_data)} data from {data_config['transfer_data_path'][text_type]}")
        ## sent prompt to client 
        if not issubclass(prompter_cls, (CRFModel,CReDEsModel)):
            raise TypeError("Invalid prompter type")
        
        # json based prompter
        if issubclass(prompter_cls, CReDEsModel):
            #init CReDEs FileProcessor
            CReDEs_dict = FileProcessor(excle_file_path=data_config['CReDEs_mapping_path'][text_type]).get_CReDEs_dict()
            # init baseprompter
            baseprompter = BasePrompter(CReDEs_dict=CReDEs_dict)
            # init prompter
            prompter_logger = prompter_logger
            prompter_setup = prompter_cls(label_list_dict=label_list_dicts,text_type = text_type,logger=prompter_logger,basic_prompt=BASIC_PROMPT,baseprompter_obj=baseprompter)

            all_prompt_list = prompter_setup.generate_prompt(alpaca_data)
        
            inference_alpaca_data = process_prompt_to_client(all_prompt_list,local_inference_client_setup,inference_logger,temperature=temperature)
            inference_logger.info(f"local inference client get {len(inference_alpaca_data)} data")

        # pydantic based prompter
        else:
            prompter_logger = prompter_logger
            prompter_setup = prompter_cls(label_list_dict=label_list_dicts,text_type = text_type,logger=prompter_logger,)

            all_prompt_list = prompter_setup.generate_prompt(alpaca_data)
        
            inference_alpaca_data = process_prompt_to_client(all_prompt_list,local_inference_client_setup,inference_logger,temperature=temperature)
            inference_logger.info(f"local inference client get {len(inference_alpaca_data)} data")
        return inference_alpaca_data

    elif inference_client_cls == online_inference_client:
        ## load online model config
        online_inference_config = config['online_inference']
        model_config = online_inference_config['model_config']
        model_name = model_config['model_name']
        base_url = model_config['base_url']
        api_token = model_config['api_token']
        temperature = model_config['temperature']

        ## setup online inference client
        ## Azure_interface=True
        online_inference_client_setup = inference_client_cls(model_name=model_name, base_url=base_url, api_key=api_token, clogger=client_logger, Azure_interface=False)
        
        ## setup prompter
        data_config =online_inference_config['data']
        alpaca_data = load_alpaca_data(data_config['transfer_data_path'][text_type])
        print(f"load {len(alpaca_data)} data from {data_config['transfer_data_path'][text_type]}")

        ## sent prompt to client 
        if not issubclass(prompter_cls, (CRFModel_Blzd_Prompter, CRFModel_Grs_Prompter,CRFModel_Hys_Prompter,CRFModel_Jws_Prompter,CRFModel_Ssjl_Prompter,CRFModel_Xbs_Prompter,CRFModel_Yxjc_Prompter,CRFModel_Zkjc_Prompter)):
            raise TypeError("Invalid prompter type")
        
        prompter_logger = prompter_logger
        prompter_setup = prompter_cls(label_list_dict= label_list_dicts,text_type = text_type,logger=prompter_logger)
        all_blzd_prompt_list = prompter_setup.generate_prompt(alpaca_data[:30])
        
        inference_alpaca_data = process_prompt_to_client(all_blzd_prompt_list,online_inference_client_setup,inference_logger,temperature=temperature)
        inference_logger.info(f"online inference client get {len(inference_alpaca_data)} data")

        return inference_alpaca_data
    

def online_inference(text_class:str,log_dir_name:str,store_dir_name:str,store_file_name:str):
    ## define config file path
    config_file_path = "/home/xuhaitong/projects/temp/transfer_CRF/config.json"

    ## load log config
    log_config = load_config(config_file_path)['log']
    log_dir = log_config['log_dir']
    log_dir = os.path.join(log_dir,log_dir_name)

    # Initialize logger    
    prompter_logger = CustomLogger(log_dir=log_dir,log_file="prompter.log", log_name="prompter")
    client_logger = CustomLogger(log_dir=log_dir,log_file="client.log", log_name="client")
    inference_logger = CustomLogger(log_dir=log_dir,log_file="inference_test.log", log_name="inference")
    
    # switch CRF_model
    CRFPrompter = {
        "blzd": CRFModel_Blzd_Prompter,
        "grs": CRFModel_Grs_Prompter,
        "hys": CRFModel_Hys_Prompter,
        "jws": CRFModel_Jws_Prompter,
        "ssjl": CRFModel_Ssjl_Prompter,
        "xbs": CRFModel_Xbs_Prompter,
        "yxjc": CRFModel_Yxjc_Prompter,
        "zkjc": CRFModel_Zkjc_Prompter
    }[text_class]

    # Run the transfer_CRF_inference
    transfer_alpaca = transfer_inference(
        inference_client_cls = online_inference_client,
        prompter_cls = CRFPrompter,
        text_type = text_class,
        label_list_dicts = LABEL_LIST_DICT,
        prompter_logger = prompter_logger,
        client_logger = client_logger,
        inference_logger = inference_logger,
        config_file_path = config_file_path  
    )

    ## save transfer data
    store_transfer_data_config = load_config(config_file_path)['online_inference']['store_transfer_data']
    store_dir = store_transfer_data_config['store_transfer_data_path_dir']
    store_dir = os.path.join(store_dir,store_dir_name)
    store_file_name = store_file_name
    save_alpaca_data(transfer_alpaca, store_dir, store_file_name)
    

def local_inference_base_pydantic(text_class:str,log_dir_name:str,store_dir_name:str,store_file_name:str):
    # local inference 
    ## define config file path
    config_file_path = "/home/xuhaitong/projects/temp/transfer_CRF/config.json"

    ## load log config
    log_config = load_config(config_file_path)['log']
    log_dir = log_config['log_dir']
    log_dir = os.path.join(log_dir,log_dir_name)
    
    # Initialize logger    
    prompter_logger = CustomLogger(log_dir=log_dir,log_file="prompter.log", log_name="prompter")
    client_logger = CustomLogger(log_dir=log_dir,log_file="client.log", log_name="client")
    inference_logger = CustomLogger(log_dir=log_dir,log_file="inference.log", log_name="inference")
    
    # switch CRF_model
    CRFPrompter = {
        "blzd": CRFModel_Blzd_Prompter,
        "grs": CRFModel_Grs_Prompter,
        "hys": CRFModel_Hys_Prompter,
        "jws": CRFModel_Jws_Prompter,
        "ssjl": CRFModel_Ssjl_Prompter,
        "xbs": CRFModel_Xbs_Prompter,
        "yxjc": CRFModel_Yxjc_Prompter,
        "zkjc": CRFModel_Zkjc_Prompter
    }[text_class]

    # Run the transfer_CRF_inference
    transfer_alpaca = transfer_inference(
        inference_client_cls = local_inference_client,
        prompter_cls = CRFPrompter,
        text_type = text_class,
        label_list_dicts = LABEL_LIST_DICT,
        prompter_logger = prompter_logger,
        client_logger = client_logger,
        inference_logger = inference_logger,
        config_file_path = config_file_path  
    )

    ## save transfer data
    store_transfer_data_config = load_config(config_file_path)['local_inference']['store_transfer_data']
    store_dir = store_transfer_data_config['store_transfer_data_path_dir']
    store_dir = os.path.join(store_dir,store_dir_name)
    store_file_name = store_file_name
    save_alpaca_data(transfer_alpaca, store_dir, store_file_name)

def local_inference_base_json(text_class:str,log_dir_name:str,store_dir_name:str,store_file_name:str):
    # local inference 
    ## define config file path
    config_file_path = "/home/xuhaitong/projects/temp/transfer_CRF/config.json"

    ## load log config
    log_config = load_config(config_file_path)['log']
    log_dir = log_config['log_dir']
    log_dir = os.path.join(log_dir,log_dir_name)
    
    # Initialize logger    
    prompter_logger = CustomLogger(log_dir=log_dir,log_file="prompter.log", log_name="prompter")
    client_logger = CustomLogger(log_dir=log_dir,log_file="client.log", log_name="client")
    inference_logger = CustomLogger(log_dir=log_dir,log_file="inference.log", log_name="inference")
    
    # Run the transfer_CRF_inference
    transfer_alpaca = transfer_inference(
        inference_client_cls = local_inference_client,
        prompter_cls = CReDEs_Prompter,
        text_type = text_class,
        label_list_dicts = LABEL_LIST_DICT_JSON,
        prompter_logger = prompter_logger,
        client_logger = client_logger,
        inference_logger = inference_logger,
        config_file_path = config_file_path  
    )

    ## save transfer data
    store_transfer_data_config = load_config(config_file_path)['local_inference']['store_transfer_data']
    store_dir = store_transfer_data_config['store_transfer_data_path_dir']
    store_dir = os.path.join(store_dir,store_dir_name)
    store_file_name = store_file_name
    save_alpaca_data(transfer_alpaca, store_dir, store_file_name)



def main():
    ### local inference 
    local_inference_base_json(text_class="blzd",log_dir_name="blzd",store_dir_name="blzd",store_file_name="blzd.json")
    local_inference_base_json(text_class="jrzl",log_dir_name="jrzl",store_dir_name="jrzl",store_file_name="jrzl.json")
    local_inference_base_json(text_class="ssjl",log_dir_name="ssjl",store_dir_name="ssjl",store_file_name="ssjl.json")
    local_inference_base_json(text_class="rcbc",log_dir_name="rcbc",store_dir_name="rcbc",store_file_name="rcbc.json")
    local_inference_base_json(text_class="jc",log_dir_name="jc",store_dir_name="jc",store_file_name="jc.json")
    local_inference_base_json(text_class="ryjl",log_dir_name="ryjl",store_dir_name="ryjl",store_file_name="ryjl.json")

    
    ### online inference 
    # online_inference(text_class="blzd",log_dir_name="blzd",store_dir_name="blzd",store_file_name="blzd_30.json")