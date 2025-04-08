from pydantic import BaseModel, Field, model_validator
from typing import Dict, Optional
import json
from enum import Enum

class OtherOption(BaseModel):
    是否选择: bool = False
    说明: Optional[str]  = Field(
        None,
        max_length=100,
        description="其他/有，需填写文字说明"
    )

# 抗凝药物选项
class Anticoagulant(BaseModel):
    无: bool = False
    阿司匹林: bool = False
    华法林: bool = False
    波立维: bool = False
    泰嘉: bool = False
    # 其他部位使用复合结构
    其他: OtherOption = Field(default_factory=OtherOption)

    @model_validator(mode='after')
    def validate_other_field(self):
        other = self.其他
        # 验证其他部位逻辑
        if other.是否选择 and not other.说明:
            raise ValueError("选择其他时必须填写说明")
        if not other.是否选择 and other.说明:
            raise ValueError("未选择其他时不能填写说明")
        return self

# 血液系统疾病选项
class BloodDisease(BaseModel):
    无: bool = False
    淋巴瘤: bool = False
    白血病: bool = False
    贫血: bool = False
    
    # 其他部位使用复合结构
    其他: OtherOption = Field(default_factory=OtherOption)

    @model_validator(mode='after')
    def validate_other_field(self):
        other = self.其他
        # 验证其他部位逻辑
        if other.是否选择 and not other.说明:
            raise ValueError("选择其他时必须填写说明")
        if not other.是否选择 and other.说明:
            raise ValueError("未选择其他时不能填写说明")
        return self

# 其他肿瘤疾病选项
class TumorDisease(BaseModel):
    无: bool = True
    # 有，使用复合结构
    有: OtherOption = Field(default_factory=OtherOption)

    @model_validator(mode='after')
    def validate_other_field(self):
        other = self.有
        # 验证其他部位逻辑
        if other.是否选择 and not other.说明:
            raise ValueError("选择有时必须填写说明")
        if not other.是否选择 and other.说明:
            raise ValueError("未选择有时不能填写说明")
        return self


class MedicalHistory(BaseModel):
    高血压: bool = Field(..., description="是否有高血压")
    糖尿病: bool = Field(..., description="是否有糖尿病")
    冠心病: bool = Field(..., description="是否有冠心病")
    血液系统疾病: BloodDisease
    其他肿瘤疾病: TumorDisease
    抗凝药物治疗: Anticoagulant



