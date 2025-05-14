from pydantic import BaseModel, Field
from enum import Enum
import json


# 结构使用的是枚举类型
class MaritalStatusEnum(str, Enum):
    MARRIED = "已婚"
    SINGLE = "未婚"
    DIVORCED = "离异"
    WIDOWED = "丧偶"

class FertilityStatusEnum(str, Enum):
    NO_CHILDREN = "未育"
    HAS_CHILDREN = "已育"
    OTHER_option = "不合适"

class MarriageFertilityHistory(BaseModel):
    marital_status: MaritalStatusEnum = Field(..., alias="婚姻情况")
    fertility_status: FertilityStatusEnum = Field(..., alias="生育情况")

