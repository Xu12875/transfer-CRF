from json import load
import os
import argparse
from traitlets import CRegExp
from inference_client import local_inference_client,online_inference_client
from typing import List, Dict, Any, Tuple, Optional, Union, Type
from logger import CustomLogger
from prompter import CRFModel_Blzd_Prompter, CRFModel_Grs_Prompter,CRFModel_Hys_Prompter,CRFModel_Jws_Prompter,CRFModel_Ssjl_Prompter,CRFModel_Xbs_Prompter,CRFModel_Yxjc_Prompter,CRFModel_Zkjc_Prompter,CRFModel
from prompter_json import CRCDEs_Prompter,CRCDEsModel_PreGroup,CRCDEsModel_PostGroup,CRCDEsModel, CRCDEs_Prompter_Pre,CRCDEs_Prompter_Post
from params import LABEL_LIST_DICT,BASIC_PROMPT,ENTITY_GROUPED_PROMPT,CRCDES_PROMPT
from prompt_info.base_json.CReDEs_Prompter import CReDEs_FileProcessor,BasePrompter
from utils import load_alpaca_data, load_config, process_prompt_to_client, save_alpaca_data,timeit


def transfer_inference(inference_client_cls: Union[Type[local_inference_client], 
Type[online_inference_client]], 
                       prompter_cls: Union[Type[CRCDEs_Prompter], Type[CRCDEsModel], Type[CRFModel]], 
                       text_type: str,
                       prompter_logger: CustomLogger,
                       client_logger: CustomLogger,
                       inference_logger: CustomLogger,
                       config_file_path: str,
                       baseprompter: BasePrompter,
                       grouped_entity_prompter: Union[Type[CRCDEsModel_PreGroup], Type[CRCDEsModel_PostGroup]],
                       label_list_dicts: Dict[str, Any]= LABEL_LIST_DICT,
                       ) -> List[Dict[str, Any]]:
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
        
        ## init tokenizer
        local_tokenizer = local_inference_client_setup.get_tokenizer()
        max_token_len = model_config['max_token_len']

        ## setup prompter and load data
        data_config =local_inference_config['data']
        alpaca_data = load_alpaca_data(data_config['transfer_data_path'][text_type])[:10]
        print(f"load {len(alpaca_data)} data from {data_config['transfer_data_path'][text_type]}")
        ## sent prompt to client 
        if not issubclass(prompter_cls, (CRFModel,CRCDEs_Prompter)):
            raise TypeError("Invalid prompter type")
        
        # json based prompter
        if issubclass(prompter_cls, CRCDEs_Prompter):
            #init mapping  file
            label_mapping_file = data_config['label_mapping_path']
            CReDEs_mapping_file = data_config['CReDEs_mapping_path']
            
            #init CReDEs FileProcessor
            CReDEs_dict =  CReDEs_FileProcessor(label_mapping_file,CReDEs_mapping_file).get_CReDEs_mapping_dict()

            # init baseprompter
            baseprompter = BasePrompter(CReDEs_dict=CReDEs_dict)

            # grouped entity data -> pre_processing or post processing
            entity_grouped_data_list:List[Dict[str, Any]] = []
            if not isinstance(grouped_entity_prompter, CRCDEsModel):
                raise TypeError("Invalid grouped prompter type")
            if isinstance(grouped_entity_prompter, CRCDEsModel_PostGroup):
                entity_grouped_data_list = grouped_entity_prompter.get_process_data(alpaca_data)
                # init prompter
                prompter_logger = prompter_logger
                # init CRCDEs_prompter_post
                prompter_setup:CRCDEs_Prompter_Post = CRCDEs_Prompter_Post(
                    grouped_entity_data=entity_grouped_data_list,
                    text_type=text_type,
                    logger=prompter_logger,
                    crcdes_prompt=CRCDES_PROMPT,
                    baseprompter_obj=baseprompter,
                    tokenizer=local_tokenizer,
                    max_token_len=max_token_len
                )
                # generate prompt
                ## TODO: add parma --> grouped: combine json
                all_prompt_list = prompter_setup.generate_prompt(grouped=False)

                # sent prompt to client
                inference_alpaca_data = process_prompt_to_client(all_prompt_list,local_inference_client_setup,inference_logger,temperature=temperature)
                inference_logger.info(f"local inference client get {len(inference_alpaca_data)} data")
                return inference_alpaca_data

            elif isinstance(grouped_entity_prompter, CRCDEsModel_PreGroup):
                entity_grouped_data_list = grouped_entity_prompter.get_process_data(alpaca_data)            
            
                # init prompter
                prompter_logger = prompter_logger
                # init CRCDEs_prompter_pre
                """
                need fix prompter_cls -> CRCDEs_prompter_pre
                """
                prompter_setup:CRCDEs_Prompter_Pre = CRCDEs_Prompter_Pre(
                    label_list_dict=label_list_dicts,
                    text_type=text_type,
                    logger=prompter_logger,
                    basic_prompt=BASIC_PROMPT,
                    baseprompter_obj=baseprompter,
                    tokenizer=local_tokenizer,
                    max_token_len=max_token_len
                )
                # generate prompt
                ## TODO: add parma --> grouped: combine json
                all_prompt_list = prompter_setup.generate_prompt(alpaca_data,grouped=True)

                # sent prompt to client
                inference_alpaca_data = process_prompt_to_client(all_prompt_list,local_inference_client_setup,inference_logger,temperature=temperature)
                inference_logger.info(f"local inference client get {len(inference_alpaca_data)} data")
                return inference_alpaca_data
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
    ## define info logger
    info_logger = CustomLogger(log_dir_name=log_dir_name,log_file="info.log", log_name="info")
    
    ## define config file path
    # config_file_path = "/home/xuhaitong/projects/temp/transfer_CRF/config.json"
    config_file_path = ""
    local_config = os.path.join(os.getcwd(), "config.json")
    if os.path.exists(local_config):
        config_file_path = local_config
    else:
        info_logger.info("No local config file found")

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

@timeit
def local_inference_base_json(text_type:str,
                              log_dir_name:str,store_dir_name:str,store_file_name:str,
                              is_PreProcess:bool=False,
                              label_list_dict:Optional[Dict[str, Any]]=None,
                              entity_grouped_prompt:Optional[str]=None):
    # local inference     
    ## define config file path
    config_file_path = ""
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 脚本所在目录
    config_file_path = os.path.join(current_dir, "config.json")
    if os.path.exists(config_file_path):
        config_file_path = config_file_path
    else:
        print("No local config file found")

    ## load local config
    local_config = load_config(config_file_path)
    # load log config
    log_config = local_config['log']
    log_dir = log_config['log_dir']
    log_dir = os.path.join(log_dir,log_dir_name)
    
    # Initialize logger 
    prompter_logger = CustomLogger(log_dir=log_dir,log_file="prompter.log", log_name="prompter")
    client_logger = CustomLogger(log_dir=log_dir,log_file="client.log", log_name="client")
    inference_logger = CustomLogger(log_dir=log_dir,log_file="inference.log", log_name="inference")
    
    # Init grouped prompter -> pre_process or post_process
    if is_PreProcess:
        ## Init pre-grouped entity prompter
        grouped_entity_prompter = CRCDEsModel_PreGroup(label_list_dict,text_type)
    else:
        ## Init inference client for grouped entity prompter
        grouped_entity_inference_logger = CustomLogger(log_dir=log_dir,log_file="grouped_entity_inference.log", log_name="grouped_entity_inference")
        model_config = local_config['local_inference']["model_config"]
        base_url = model_config["base_url"]
        model_name = model_config["model_name"]
        api_key = model_config["api_token"]
        grouped_entity_inference_client = local_inference_client(model_name=model_name, base_url=base_url, api_key=api_key, clogger=grouped_entity_inference_logger)
        ## Init grouped entity prompter
        grouped_entity_prompter = CRCDEsModel_PostGroup(entity_grouped_prompt,grouped_entity_inference_logger,grouped_entity_inference_client)

    """
    update: transfer_inerence func -> CReDEs_Prompter = pre-process or post-process
    """
    # Run the transfer_CRF_inference
    transfer_alpaca = transfer_inference(
        inference_client_cls = local_inference_client,
        prompter_cls = CRCDEs_Prompter,
        # prompter_cls = CRCDEs_Prompter_Post,
        text_type = text_type,
        label_list_dicts = LABEL_LIST_DICT,
        prompter_logger = prompter_logger,
        client_logger = client_logger,
        inference_logger = inference_logger,
        config_file_path = config_file_path ,
        baseprompter=BasePrompter,
        grouped_entity_prompter = grouped_entity_prompter
    )

    ## save transfer data
    store_transfer_data_config = load_config(config_file_path)['local_inference']['store_transfer_data']
    store_dir = store_transfer_data_config['store_transfer_data_path_dir']
    store_dir = os.path.join(store_dir,store_dir_name)
    store_file_name = store_file_name
    save_alpaca_data(transfer_alpaca, store_dir, store_file_name)


def main():
    local_inference_base_json(text_type="病理",log_dir_name="xk_bl",store_dir_name="xk_bl",store_file_name="xk_bl.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)

    local_inference_base_json(text_type="过敏史",log_dir_name="xk_gms",store_dir_name="xk_gms",store_file_name="xk_gms.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)

    local_inference_base_json(text_type="个人史",log_dir_name="xk_grs",store_dir_name="xk_grs",store_file_name="xk_grs.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)
    
    local_inference_base_json(text_type="婚育史",log_dir_name="xk_hys",store_dir_name="xk_hys",store_file_name="xk_hys.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)
    
    local_inference_base_json(text_type="既往史",log_dir_name="xk_jws",store_dir_name="xk_jws",store_file_name="xk_jws.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)
    
    local_inference_base_json(text_type="家族史",log_dir_name="xk_jzs",store_dir_name="xk_jzs",store_file_name="xk_jzs.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)
    
    
    local_inference_base_json(text_type="物理检查",log_dir_name="xk_wljc",store_dir_name="xk_wljc",store_file_name="xk_wljc.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)
    
    
    local_inference_base_json(text_type="现病史",log_dir_name="xk_xbs",store_dir_name="xk_xbs",store_file_name="xk_xbs.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)
    
    
    local_inference_base_json(text_type="诊断",log_dir_name="xk_zd",store_dir_name="xk_zd",store_file_name="xk_zd.json",is_PreProcess=False, entity_grouped_prompt=ENTITY_GROUPED_PROMPT)

    
