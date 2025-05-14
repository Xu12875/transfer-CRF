from pydantic import BaseModel,Field
from enum import Enum
from typing import Union

# class NeckLymphNodeDissection(str, Enum):
#     根治性 = "根治性"
#     加强预防性 = "加强预防性"
#     预防性 = "预防性"
#     选择性 = "选择性"
#     无 = "无"

# class SurgeryRecord(BaseModel):
#     颈部淋巴结清扫: NeckLymphNodeDissection
#     皮瓣修复: bool
#     气切: bool
#     输血: bool
#     ICU: bool

class SurgeryRecord(BaseModel):
    颈部淋巴清扫: Union[str, bool] = Field(..., description="颈部淋巴结清扫")
    皮瓣修复: bool = Field(False, description="皮瓣修复")
    气切: bool = Field(False, description="气切")
    输血: bool = Field(False, description="输血")
    ICU: bool = Field(False, description="ICU")



