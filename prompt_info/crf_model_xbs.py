from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional,Union
from enum import Enum
import json


class OtherOption(BaseModel):
    是否选择: bool = False
    说明: Optional[str] = Field(
        None,
        max_length=100,
        description="其他需填写文字说明"
    )

class TumorRecurrenceType(str, Enum):
    PRIMARY = "原发初治"
    RECURRENCE = "复发"
    SECOND_PRIMARY = "二原发"
    Neoadjuvant_Induction = "新辅助/诱导"
    Incomplete = "不彻底"

class TumorRecurrenceTime(str, Enum):
    LESS_THAN_3_MONTHS = "＜3个月"
    LESS_THAN_6_MONTHS = "＜6个月（≥3个月）"
    LESS_THAN_1_YEAR = "＜1年（≥6个月）"
    LESS_THAN_2_YEARS = "＜2年（≥1年）"
    LESS_THAN_5_YEARS = "＜5年（≥2年）"
    MORE_THAN_5_YEARS = "≥5年"
    NONA = None

class Part_OralMucosalHistory(BaseModel):
    原发复发: TumorRecurrenceType = Field(..., title="肿瘤原复发类型")
    复发时间: TumorRecurrenceTime = Field(..., title="肿瘤复发时间")
    既往口腔黏膜病史: Union[str,bool] = Field(..., title="既往口腔黏膜病史")
    
class Part_PastMedicalHistory(BaseModel):
    既往手术史: bool = Field(False, title="既往手术史")
    既往化疗史: bool = Field(False, title="既往化疗史")
    既往放疗史: bool = Field(False, title="既往放疗史")
    既往颈清史: bool = Field(False, title="既往颈清史")
