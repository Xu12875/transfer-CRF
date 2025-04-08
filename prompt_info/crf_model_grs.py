from pydantic import BaseModel, Field
from typing import Literal, Optional, List
import json
from enum import Enum

# 枚举类型 
class YesNoEnum(str, Enum):
    NO = "无"
    YES = "有"

class HealthHistory(BaseModel):
    smoking: YesNoEnum = Field(..., alias="吸烟史")
    drinking: YesNoEnum = Field(..., alias="饮酒史")
    betel_nut: YesNoEnum = Field(..., alias="槟榔史")