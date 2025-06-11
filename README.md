# Transfer_CRF
**利用fine-tune model 推理得出的字段信息结合qwen2.5-32B/QWQ-32B进行本地推理和调用** 

## 模块结构
```shell
transfer_CRF/
        ├── data/
        ├── logs/
        ├── prompt_info/
        ├── server_sh/
        ├── transfer_data/
        ├── config.json
        ├── inference_client.py
        ├── logger.py
        ├── main.py
        ├── prompter_json.py
        ├── prompter.py
        ├── transfer_CRF_inference.py
        └── utils.py
```
- 1. `data/`：data文件夹，存放数据文件，存放CReDEs和inference data
- 2. `server_sh` 启动QWQ-32B/Qwen2.5-32B-Instruct模型服务sh
- 3. `prompt_info/`：base_json 中对针对CReDEs标准进行json的生成 
- 4. `transfer_CRF_inference.py`：推理逻辑核心，负责调用QWQ-32B/Qwen2.5-32B-Instruct模型进行推理。
- 5. `inference_client.py`：用于客户端推理调用，提供API接口。
- 6. `prompter_json.py`：生成或处理提示信息，生成json结构和键值对的描述信息，分组处理推理字段，生成prompt。
- 7. `config.json`：配置文件，包含模型路径、API地址等信息。
- 8. `logger.py`：日志工具，用于记录日志信息。
- 9. `utils.py`：工具函数，提供一些辅助功能。 

## 主要模块说明
### 1. `transfer_CRF/prompt_info`
base_json中定义CReDEs 数据文件（xlsx） 的文件处理类`FileProcessor` 和 基于`langchian`的结构化输出`ResponseSchema`生成baseprompt 
```python
from .output_structure import ResponseSchema,StructuredOutputParser

``` 
### 2. `prompter_json.py`

#### 🧠 模块作用：基于实体分组的Prompt生成器
##### 📂 核心结构
```python

class CReDEsModel
基础模型类，负责将标签分组，并匹配标注数据与这些标签组。

主要功能：

_group_labels()：将带属性的标签（如 "主要病变:病变大小"）按主实体（如 "主要病变"）进行分组。

match_grouped_label_data()：将标注数据按标签分组组织，形成方便后续处理的结构。

get_unit_grouped_label_key()：获取某一条数据中涉及的主实体。
```
```python
class CReDEs_Prompter(CReDEsModel)
扩展自 CReDEsModel，是实际执行 Prompt生成 的类。

主要职责：

使用标注数据和原始文本，结合标签体系和基础Prompt模板，构造出适合LLM抽取的提示词。

支持区分“仅实体”和“实体+属性”的prompt。
```
#### 📦 输入数据结构
**alpaca_data: List[Dict]**
```json
[
  {
    "input": "原始电子病历文本",
    "output": "实体标注结果，格式为 实体 或 实体:属性"
  }
]
```
**LABEL_LIST_DICT_JSON**：定义每种病历类型（如 "blzd"）下的所有可抽取标签。

会被 _group_labels() 方法按实体组织成一个嵌套结构。

#### 🔧 Prompt 构建流程
**标签分组：**

使用 _group_labels() 将标签按主实体进行分组（有属性和无属性分别处理）。

**数据匹配：**

使用 match_grouped_label_data() 把每条标注数据中提到的标签归入对应实体组。

**生成Prompt：**

遍历每个实体组：
对于“无属性实体”：将多个实体统一合成一个Prompt。
对于“有属性实体”：分别为每个主实体生成一个Prompt。
用 **BASIC_PROMPT.format()** 插入具体的原始文本、标注数据和待填写JSON结构。


#### 📝 示例Prompt格式（伪代码）
```text
[任务]
请你使用中文回答...

[病例原文]
病人男性，45岁...

[标注数据]
主要病变:病变大小
主要病变:卫星结节

[json]
{
  "主要病变": List[str],  // 信息描述..., 值域为...
  ...
}

[输出]
```
### 3. `transfer_CRF_inference.py`
- `local_inference_base_json()`：定义了推理逻辑
具体实现在代码中体现


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