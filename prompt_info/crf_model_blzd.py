from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import json
from enum import Enum
from typing import Optional, Dict, Union, Literal
from pydantic import BaseModel

class 分化信息(str, Enum): # 分化程度
    高分化 = "高分化"
    高中分化 = "高-中分化"
    中分化 = "中分化"
    中低分化 = "中-低分化"
    低分化 = "低分化"
    无 = None

class HPV(str, Enum): # HPV检测
    阴性 = "阴性"
    阳性 = "阳性"
    无 = None

class P16(str, Enum): # P16检测
    阴性 = "阴性"
    阳性 = "阳性"
    无 = None

class 切缘(str, Enum): # 切缘检测
    阴性 = "阴性"
    阳性 = "阳性"
    无 = None

class 属性信息(BaseModel):
    解剖学方位: Literal["左侧", "右侧", "双侧", "不详"] = None
    DOI值: Literal["≤5", "≤10（＞5）", "＞10", "不详"] = None
    原发灶大小: Literal["≤2", "≤4（＞2）", "＞4", "不详"] = None

class 解剖学部位信息(BaseModel):
    解剖学部位: str
    属性信息: 属性信息

class 阳性淋巴结描述(BaseModel):
    阳性淋巴结清扫区域: str
    阳性颈清部位: Literal["左侧", "右侧", "双侧", "不详"] = None
    阳性颈清侧位: Literal["对侧", "同侧", "双侧"] = None
    阳性颈清直径: Literal["≤3", "≤6（＞3）", "＞6", "不详"] = None
    阳性淋巴结数量: int = Field(..., ge=0, le=999)
    淋巴结数量: int = Field(..., ge=0, le=999)
    包膜外侵犯: bool = False

class 区域描述(BaseModel):
    阳性颈清直径: Literal["≤3", "≤6（＞3）", "＞6", "不详"] = None
    阳性淋巴结: int = Field(..., ge=0, le=999)
    淋巴结: int = Field(..., ge=0, le=999)

class 阳性淋巴结分区(BaseModel):
    左: Optional[区域描述] = Field(default=None, exclude=True)
    右: Optional[区域描述] = Field(default=None, exclude=True)
    不详: Optional[区域描述] = Field(default=None, exclude=True)

class 阳性淋巴结分区描述(BaseModel):
    I: Optional[阳性淋巴结分区] = Field(default=None, exclude=True)
    II: Optional[阳性淋巴结分区] = Field(default=None, exclude=True)
    III: Optional[阳性淋巴结分区] = Field(default=None, exclude=True)
    IV: Optional[阳性淋巴结分区] = Field(default=None, exclude=True)
    V: Optional[阳性淋巴结分区] = Field(default=None, exclude=True)

class 阳性淋巴结信息(BaseModel):
    阳性淋巴结描述: 阳性淋巴结描述
    阳性淋巴结分区描述: Optional[阳性淋巴结分区描述]

class 基本信息描述(BaseModel):
    分化信息: 分化信息 
    HPV: HPV
    P16: P16
    切缘: 切缘
    神经侵犯: bool
    脉管侵犯: bool

class Part_AnatomicalSiteDescription(BaseModel):
    解剖学部位信息: 解剖学部位信息 

class Part_LymphNodeDescription(BaseModel):
    阳性淋巴结信息: 阳性淋巴结信息

class Part_OtherDescription(BaseModel):
    基本信息描述: 基本信息描述