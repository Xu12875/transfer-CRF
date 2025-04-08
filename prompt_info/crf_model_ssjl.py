from pydantic import BaseModel
from enum import Enum
import json

class NeckLymphNodeDissection(str, Enum):
    根治性 = "根治性"
    加强预防性 = "加强预防性"
    预防性 = "预防性"
    选择性 = "选择性"
    无 = "无"

class SurgeryRecord(BaseModel):
    颈部淋巴结清扫手术: NeckLymphNodeDissection
    皮瓣修复手术: bool
    气管切开手术: bool
    出血记录: bool
    ICU记录: bool

