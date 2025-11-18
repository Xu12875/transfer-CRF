from json import load
import os

from pydantic import BaseModel

from inference_client import local_inference_client, online_inference_client
from typing import List, Dict, Any, Tuple, Optional, Union, Type
from logger import CustomLogger
from prompter_9h import LABEL_LIST_DICT, CRFModel
from utils import load_alpaca_data, load_config, process_prompt_to_client, save_alpaca_data
# from prompt_info.base_pydantic.crf_model_9h_zhcn import GRS, HYS, JWS, XBS, SurgeryRecord, \
#     SpecialExam, ImageExaminationRecord, PathologicalPart1, PathologicalPart2, \
#     PathologicalPart3, PathologicalPart4

from prompt_info.base_pydantic.crf_model_9h_no_table import PathologicalExamination, GRS, HYS, JWS, XBS, SurgeryRecord, \
    SpecialExam, ImageExaminationRecord


def transfer_inference(inference_client_cls: Union[Type[local_inference_client],
Type[online_inference_client]],
                       prompter_cls: Union[Type[CRFModel]],
                       text_type: str,
                       label_list_dicts: Dict[str, Any],
                       prompter_logger: CustomLogger,
                       client_logger: CustomLogger,
                       inference_logger: CustomLogger,
                       config_file_path: str,
                       prompt_text_class: str,
                       clz: Type[BaseModel]
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
        model_path = model_config['model_path']
        base_url = model_config['base_url']
        api_token = model_config['api_token']
        temperature = model_config['temperature']

        ## setup local inference client
        local_inference_client_setup = inference_client_cls(model_path=model_path, model_name=model_name,
                                                            base_url=base_url, api_key=api_token, clogger=client_logger)

        ## init tokenizer

        ## setup prompter and load data
        data_config = local_inference_config['data']
        alpaca_data = load_alpaca_data(data_config['transfer_data_path'][text_type])
        print(f"load {len(alpaca_data)} data from {data_config['transfer_data_path'][text_type]}")
        ## sent prompt to client 
        if not issubclass(prompter_cls, (CRFModel)):
            raise TypeError("Invalid prompter type")

        # json based prompter
        prompter_logger = prompter_logger
        prompter_setup = prompter_cls(label_list_dict=label_list_dicts, text_type=text_type, logger=prompter_logger)

        all_prompt_list = prompter_setup.generate_prompt(alpaca_data[:50], clz, prompt_text_class)

        inference_alpaca_data = process_prompt_to_client(all_prompt_list, local_inference_client_setup,
                                                         inference_logger, temperature=temperature)
        inference_logger.info(f"local inference client get {len(inference_alpaca_data)} data")
    return inference_alpaca_data


def local_inference_base_pydantic(text_class: str, log_dir_name: str, store_dir_name: str, store_file_name: str,
                                  prompt_text_class: str):
    # local inference
    ## define config file path
    config_file_path = "./config.json"

    ## load log config
    log_config = load_config(config_file_path)['log']
    log_dir = log_config['log_dir']
    log_dir = os.path.join(log_dir, log_dir_name)

    # Initialize logger    
    prompter_logger = CustomLogger(log_dir=log_dir, log_file="prompter.log", log_name="prompter")
    client_logger = CustomLogger(log_dir=log_dir, log_file="client.log", log_name="client")
    inference_logger = CustomLogger(log_dir=log_dir, log_file="inference.log", log_name="inference")

    # switch CRF_model
    dataModel = {
        # "blzd9": [PathologicalPart1, PathologicalPart2, PathologicalPart3, PathologicalPart4],
        "blzd9": [PathologicalExamination],
        "grs9": [GRS],
        "hys9": [HYS],
        "jws9": [JWS],
        "ssjl9": [SurgeryRecord],
        "xbs9": [XBS],
        "yxjc9": [ImageExaminationRecord],
        "zkjc9": [SpecialExam]
    }[text_class]

    # Run the transfer_CRF_inference
    transfer_alpaca = transfer_inference(
        inference_client_cls=local_inference_client,
        prompter_cls=CRFModel,
        text_type=text_class,
        label_list_dicts=LABEL_LIST_DICT,
        prompter_logger=prompter_logger,
        client_logger=client_logger,
        inference_logger=inference_logger,
        config_file_path=config_file_path,
        prompt_text_class=prompt_text_class,
        clz=dataModel
    )

    ## save transfer data
    store_transfer_data_config = load_config(config_file_path)['local_inference']['store_transfer_data']
    store_dir = store_transfer_data_config['store_transfer_data_path_dir']
    store_dir = os.path.join(store_dir, store_dir_name)
    store_file_name = store_file_name
    save_alpaca_data(transfer_alpaca, store_dir, store_file_name)


def main():
    local_inference_base_pydantic(text_class="blzd9", log_dir_name="blzd", store_dir_name="temp",
                                  store_file_name="blzd.json", prompt_text_class="blzd")
    # local_inference_base_pydantic(text_class="jws9", log_dir_name="jws", store_dir_name="temp",
    #                               store_file_name="jws.json", prompt_text_class="base")
    # local_inference_base_pydantic(text_class="ssjl9", log_dir_name="ssjl", store_dir_name="temp",
    #                               store_file_name="ssjl.json", prompt_text_class="base")
    # local_inference_base_pydantic(text_class="xbs9", log_dir_name="xbs", store_dir_name="temp",
    #                               store_file_name="xbs.json", prompt_text_class="base")
    # local_inference_base_pydantic(text_class="hys9", log_dir_name="hys", store_dir_name="temp",
    #                               store_file_name="hys.json", prompt_text_class="base")
    # local_inference_base_pydantic(text_class="grs9", log_dir_name="grs", store_dir_name="temp",
    #                               store_file_name="grs.json", prompt_text_class="base")
    # local_inference_base_pydantic(text_class="yxjc9", log_dir_name="yxjc", store_dir_name="temp",
    #                               store_file_name="yxjc.json", prompt_text_class="base")
    # local_inference_base_pydantic(text_class="zkjc9", log_dir_name="zkjc", store_dir_name="temp",
    #                               store_file_name="zkjc.json", prompt_text_class="base")


main()
# local_inference_base_json(text_class="grs9",log_dir_name="grs",store_dir_name="grs",store_file_name="grs.json",data_text_class="grs9")
# local_inference_base_json(text_class="hys9",log_dir_name="hys",store_dir_name="hys",store_file_name="hys.json",data_text_class="hys9")
# local_inference_base_json(text_class="ssjl9",log_dir_name="ssjl",store_dir_name="ssjl",store_file_name="ssjl.json",data_text_class="ssjl9")
# local_inference_base_json(text_class="xbs9",log_dir_name="xbs",store_dir_name="xbs",store_file_name="xbs.json",data_text_class="xbs9")
# local_inference_base_json(text_class="yxjc9",log_dir_name="yxjc",store_dir_name="yxjc",store_file_name="yxjc.json",data_text_class="yxjc9")
# local_inference_base_json(text_class="zkjc9",log_dir_name="zkjc",store_dir_name="zkjc",store_file_name="zkjc.json",data_text_class="zkjc9")
# local_inference_base_json(text_class="blzd9h",log_dir_name="blzd",store_dir_name="blzd",store_file_name="blzd_test.json",data_text_class="blzd9h")
