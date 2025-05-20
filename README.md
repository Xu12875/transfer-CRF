# Transfer_CRF
**利用fine-tune model 推理得出的字段信息结合QWQ-32B进行本地推理和调用** 

## 模块结构
```shell
transfer_CRF
    ├── main.py 
    ├── transfer_CRF_inference.py # 推理逻辑核心
    ├── inference_client.py # 用于客户端推理调用
    ├── prompter.py # 生成或处理提示信息（如 prompt 模板）
    ├── config.json # 配置文件
    ├── logger.py # 日志工具
    ├── utils.py # 工具函数
    └── .git/
```
- 1. `main.py`：主程序，负责启动推理服务。
- 2. `transfer_CRF_inference.py`：推理逻辑核心，负责调用QWQ-32B模型进行推理。
- 3. `inference_client.py`：用于客户端推理调用，提供API接口。
- 4. `prompter.py`：生成或处理提示信息，生成json schema，分组处理推理字段，生成prompt模板。
- 5. `config.json`：配置文件，包含模型路径、API地址等信息。
- 6. `logger.py`：日志工具，用于记录日志信息。
- 7. `utils.py`：工具函数，提供一些辅助功能。 

## 主要模块说明
### 1. `transfer_CRF/prompt_info`
这个文件夹下是定义不同数据类型的json shcema，用于生成约束json的prompt模板(**{json_schema}**)。可利用以下库去实现不同数据类型的CRF表的json schema。
```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Union, Literal
...
``` 
### 2. `prompter.py`
-  定义了不同数据的**prompt**模板，每个class 都继承自 **`CRFModel`**
    里面定义了分组的算法`match_grouped_label_data()`,将每个字段数据按照组别进行分组，例如
    ```
    [
        ['淋巴结清扫区域:III', '淋巴结清扫区域:LN数量:3', '淋巴结清扫区域:颈清直径:0.3-1.5cm'],
        ['淋巴结清扫区域:IV', '淋巴结清扫区域:LN数量:6', '淋巴结清扫区域:颈清直径:0.3-1cm']
    ]
    ``` 
    在不同数据的class中可自定义分组情况，不同的分组情况在对应的`transfer_CRF/prompt_info/xxx.py`中定义分组json schema，例如，将分组信息定义在不同的json schema，这个分组设计是人为制定的，根据实际情况进行分组设计（关联程度大的字段信息放在一块）
    ``` python
    class Part_AnatomicalSiteDescription(BaseModel):
        解剖学部位信息: 解剖学部位信息 

    class Part_LymphNodeDescription(BaseModel):
        阳性淋巴结信息: 阳性淋巴结信息

    class Part_OtherDescription(BaseModel):
        基本信息描述: 基本信息描述
    ```
    具体分组设计可以在每个类中自定义，修改 **`generate_prompt()`** 函数 

- `prompter.py`中的`LABEL_LIST_DICT`,定义的是对应数据的标签数据，具体可看其内容

### 3. `transfer_CRF_inference.py`
- `local_inference()`：定义了推理逻辑
注意，在 **# switch CRF_model （注释）** 中定义了不同数据的prompter模型，可进行修改，对应到实际情况添加和修改；
```python
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
```

## 使用说明
### 1. 安装依赖
在`requirements.txt`中有所需的依赖包。
```shell
conda create --name env_name python=3.8.18 --file requirements.txt
conda create --name env_name 
``` 

### 2. 启动服务
启动`server_sh/vllm_server.sh`推理，以API形式提供服务。具体可操作参数可参考 
https://docs.vllm.ai/en/latest/serving/engine_args.html 

### 3. 配置文件
在`config.json`中配置模型路径、API地址、数据地址等信息，本地推理在`local_inference`中修改配置。
#### model config
其中`base_url`和`api_token`可在`server_sh/vllm_server.sh`中配置。
```json
"model_config": {
            "model_path": "/data/hf_cache/models/Qwen/QwQ-32B",
            "base_url": "http://localhost:8030/v1",
            "api_token": "token-abc123",
            "model_name": "/data/hf_cache/models/Qwen/QwQ-32B",
            "temperature": 0.0,
            }
```
#### data config
可配置推理出的字段数据地址，还有结果的存储地址
```json
"data": {
    "transfer_data_path": {
        "推理数据类型": "地址",
        ...
    }
},
"store_transfer_data": {
    "store_transfer_data_path_dir": "结果的存储地址"
}
```
注意：此处的地址是指一个json文件地址，数据格式为Alpaca形式
示例如下： 
```json
{
    "instruction": "",
    "input": "\n“右颊”黏膜鳞状细胞癌\n切缘：“内，外，上，后，底”均阴性（-）部分颌骨及周围组织：5*4*2.5cm，粘膜切面见一肿块：3*2*1cm，灰白，界不清。\n送检切缘5处。\n“右颊”黏膜鳞状细胞癌I-II级\n切缘：“内、外、上、后、底”均阴性（-）\n免疫组化结果：I2015-2178\nCKH，CKpan，p63（+），CK14,CK19，Ki-67部分（+）,Vim，S-100（-）颈大块0.5*3.5*3cm，内见一腺体1.5*1.5*1cm，灰黄分叶，余为肌肉等。\n送检淋巴结三区。\n“右颌下腺”慢性涎腺炎\n送检淋巴结：“右”“I”5只，“II”3只，“III”2只均阴性（-）",
    "output": "解剖学部位:颊\n解剖学部位:解剖学方位:右\n解剖学部位:颊\n解剖学部位:解剖学方位:右\n解剖学部位:原发灶大小:3*2*1cm\n分化信息:I-II级\n切缘:切缘：“内，外，上，后，底”均阴性（-）\n切缘:切缘：“内、外、上、后、底”均阴性（-）\n淋巴结清扫区域:I\n淋巴结清扫区域:LN清扫方位:右\n淋巴结清扫区域:LN数量:5\n淋巴结清扫区域:II\n淋巴结清扫区域:LN清扫方位:右\n淋巴结清扫区域:LN数量:3\n淋巴结清扫区域:III\n淋巴结清扫区域:LN清扫方位:右\n淋巴结清扫区域:LN数量:2"
}
```
#### log config 
记录日志的路径
```json
"log": {
    "log_dir": "日志的存储文件夹",
}
```
### 4. 推理调用
在`transfer_CRF_inference.py`中的`main()`函数中调用`local_infrence()`推理数据,相关参数如下
```
text_class="", --推理数据类型(数据类型要已定义)
log_dir_name="", --日志的存储文件夹名
store_dir_name="", --结果的存储文件夹名
store_file_name="xxx.json" --结果的存储文件名
```


