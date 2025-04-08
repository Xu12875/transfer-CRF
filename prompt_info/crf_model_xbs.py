from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional
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
    PRIMARY = "原发"
    RECURRENCE = "复发"
    SECOND_PRIMARY = "二原发"

class TumorRecurrenceTime(str, Enum):
    LESS_THAN_3_MONTHS = "＜3个月"
    LESS_THAN_6_MONTHS = "＜6个月（≥3个月）"
    LESS_THAN_1_YEAR = "＜1年（≥6个月）"
    LESS_THAN_2_YEARS = "＜2年（≥1年）"
    LESS_THAN_5_YEARS = "＜5年（≥2年）"
    MORE_THAN_5_YEARS = "≥5年"
    无 = "无"

class RadiationTherapyType(str, Enum):
    RADIOTHERAPY = "放射治疗"
    CHEMOTHERAPY = "化疗治疗"
    IMMUNOTHERAPY = "免疫治疗"
    TARGETED_THERAPY = "靶向治疗"
    INDUCTION_THERAPY = "诱导治疗"
    ADJUVANT_THERAPY = "辅助治疗"
    PREOPERATIVE_INDUCTION = "术前诱导"

class OralMucosalHistoryType(str, Enum):
    无: bool = False
    口腔白斑: bool = False
    口腔红斑: bool = False
    口腔扁平苔藓: bool = False
    口腔黏膜下纤维化: bool = False
    其他: OtherOption = Field(default_factory=OtherOption)

    @model_validator(mode='after')
    def validate_other_field(self):
        other = self.其他
        # 验证其他部位逻辑
        if other.是否选择 and not other.说明:
            raise ValueError("选择其他部位时必须填写说明")
        if not other.是否选择 and other.说明:
            raise ValueError("未选择其他部位时不能填写说明")
        return self

class SurgeryAttributes(BaseModel):
    手术时间: str = Field(..., title="手术时间", description="格式：YYYY年MM月DD日")

class SurgeryHistory(BaseModel):
    手术名称: str = Field(..., title="手术名称")
    属性信息: SurgeryAttributes = Field(..., title="属性信息")

class RadiationTherapyAttributes(BaseModel):
    放化疗次数: int = Field(..., title="放化疗次数")
    放化疗时间: str = Field(..., title="放化疗时间", description="格式：YYYY年MM月DD日")
    放化疗方案: Optional[str] = Field(None, title="放化疗方案")

class RadiationTherapyHistory(BaseModel):
    放化疗名称: RadiationTherapyType = Field(..., title="放化疗名称")
    属性信息: RadiationTherapyAttributes = Field(..., title="属性信息")

class PatientMedicalHistory(BaseModel):
    手术史: List[SurgeryHistory] = Field([], title="手术史")

    放化疗史: List[RadiationTherapyHistory] = Field([], title="放化疗史")

    肿瘤原复发类型: TumorRecurrenceType = Field(..., title="肿瘤原复发类型")
    肿瘤原发时间: str = Field(..., title="肿瘤原发时间", description="格式：YYYY年MM月DD日")
    肿瘤复发时间: TumorRecurrenceTime = Field(..., title="肿瘤复发时间")
    口腔黏膜病史: Dict[str, OralMucosalHistoryType] = Field(..., title="口腔黏膜病史")

class Part_SurgeryHistory(BaseModel):
    手术史: List[SurgeryHistory] = Field([], title="手术史")

class Part_RadiationTherapyHistory(BaseModel):
    放化疗史: List[RadiationTherapyHistory] = Field([], title="放化疗史")

class Part_OralMucosalHistory(BaseModel):
    肿瘤原复发类型: TumorRecurrenceType = Field(..., title="肿瘤原复发类型")
    肿瘤原发时间: str = Field(..., title="肿瘤原发时间", description="格式：YYYY年MM月DD日")
    肿瘤复发时间: TumorRecurrenceTime = Field(..., title="肿瘤复发时间")
    口腔黏膜病史: Dict[str, OralMucosalHistoryType] = Field(..., title="口腔黏膜病史")
