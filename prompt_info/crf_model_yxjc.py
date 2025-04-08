from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import json
from enum import Enum
# ---------------------------
# 基础校验模型
# ---------------------------
class OtherOption(BaseModel):
    是否选择: bool = False
    说明: Optional[str] = Field(
        None,
        max_length=100,
        description="其他部位需填写文字说明"
    )

# 影像检查类型
class ImagingType(str, Enum):
    CT = "CT"
    MRI = "MRI"
    PET_CT = "PET-CT"
    ULTRASOUND = "超声"
    UNKNOWN = "不详"

# 解剖学部位描述信息模型
# 原发部位
class AnatomicalSiteRegion(BaseModel):
    # 固定部位使用纯布尔值
    不详: bool = False
    唇: bool = False
    颊: bool = False
    舌: bool = False
    腭: bool = False
    口咽: bool = False
    口底: bool = False
    颌骨: bool = False
    牙龈: bool = False
    # 其他部位使用复合结构
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

# 累及部位
class InvolvedSite(BaseModel):
    # 固定部位使用纯布尔值（保留别名）
    不详: bool = False
    皮质骨: bool = False
    下牙槽神经管: bool = False
    口底部: bool = False
    面部皮肤: bool = False
    舌外肌: bool = False
    上颌窦: bool = False
    咀嚼肌间隙:bool = False
    翼状板: bool = False
    颅底: bool = False
    # 其他使用专用结构
    其他: OtherOption = Field(default_factory=OtherOption)

    @model_validator(mode='after')
    def validate_selections(self):
        # 验证其他部位逻辑
        if self.其他.是否选择 and not self.其他.说明:
            raise ValueError("选择其他累及部位时必须填写说明")
        if not self.其他.是否选择 and self.其他.说明:
            raise ValueError("未选择其他累及部位时不能填写说明")
        return self

# 属性
class AnatomicalSiteAttributes(BaseModel):
    肿瘤位置: Literal["左侧", "右侧", "双侧", "不详"]
    肿瘤大小: Literal["≤2", "≤4（＞2）", "＞4", "不详"]
    浸润深度: Literal["≤5", "≤10（＞5）", "＞10", "不详"]
    累及部位: InvolvedSite

class AnatomicalSiteDescription(BaseModel):
    影像检查类型:ImagingType
    原发部位: AnatomicalSiteRegion
    属性信息: AnatomicalSiteAttributes

# 阳性淋巴结描述信息模型
class LymphNodeAttributes(BaseModel):
    阳性淋巴结位置: Literal["左侧", "右侧", "双侧", "不详"]
    阳性淋巴结数量: int = Field(..., ge=0, le=999)
    淋巴结总数量: int = Field(..., ge=0, le=999)
    阳性淋巴结直径: Literal["≤3", "≤6（＞3）", "＞6", "不详"]
    包膜外侵犯: bool

class LymphNodeRegion(BaseModel):
    不详: bool = False
    I区: bool = False
    II区: bool = False
    III区: bool = False
    IV区: bool = False
    V区: bool = False
    # 其他区域使用专用结构
    其他: OtherOption = Field(default_factory=OtherOption)

    @model_validator(mode='after')
    def validate_selections(self):
        # 验证其他部位逻辑
        if self.其他.是否选择 and not self.其他.说明:
            raise ValueError("选择其他区域时必须填写说明")
        if not self.其他.是否选择 and self.其他.说明:
            raise ValueError("未选择其他区域时不能填写说明")
        return self

class LymphNodeDescription(BaseModel):
    影像检查类型:ImagingType
    阳性淋巴结区域: LymphNodeRegion
    属性信息: LymphNodeAttributes

# 主模型
class MedicalReport(BaseModel):
    解剖学部位描述信息: AnatomicalSiteDescription
    阳性淋巴结描述信息: List[LymphNodeDescription]


class Part_AnatomicalSiteDescription_image(BaseModel):
    解剖学部位描述信息: List[AnatomicalSiteDescription]

class Part_LymphNodeDescription_image(BaseModel):
    阳性淋巴结描述信息: List[LymphNodeDescription]