from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field





class XBS(BaseModel):
    既往手术史标志: Optional[Literal["无", "有", "不详"]] = Field(None, description="既往手术史标志")
    既往手术类型: Optional[Literal[
        "原发灶扩大切除术",
        "颈部管理（根治性颈清、选择性颈清及其他颈部淋巴结送检）",
        "皮瓣修复",
        "气切术"
    ]] = Field(None, description="既往手术类型")
    既往系统治疗标志: Optional[Literal["无", "有", "不详"]] = Field(None, description="既往系统治疗标志")
    既往系统治疗类型: Optional[List[Literal[
        "术前诱导治疗",
        "术后辅助治疗",
        "姑息治疗",
        "靶向治疗",
        "免疫治疗",
        "化学治疗"
    ]]] = Field(None, description="既往系统治疗类型")
    肿瘤原复发性质: Optional[Literal[
        "原发",
        "复发",
        "二原发（不同解剖部位或不同病理诊断，同一部位需要5年以上）",
        "新辅助/诱导",
        "不彻底",
        "不详"
    ]] = Field(None, description="肿瘤原复发性质")
    原发时间: Optional[str] = Field(None, max_length=100, description="原发时间")
    复发时间: Optional[Literal[
        "＜3个月",
        "＜6个月（≥3个月）",
        "＜1年（≥6个月）",
        "＜2年（≥1年）",
        "＜3年（≥2年）",
        "＜5年（≥3年）",
        "＜5年（≥2年）",
        "≥5年",
        "不详"
    ]] = Field(None, description="复发时间")
    癌前状态疾病标志: Optional[Literal["无", "有", "不详"]] = Field(None, description="癌前状态疾病标志")
    癌前状态疾病名称: Optional[List[Literal[
        "口腔扁平苔藓",
        "口腔黏膜下纤维性变",
        "盘状红斑狼疮",
        "上皮过角化",
        "先天性角化不良",
        "梅毒",
        "艾滋病",
        "白斑",
        "红斑",
        "其他"
    ]]] = Field(None, description="癌前状态疾病名称")
    其他癌前状态疾病名称: Optional[str] = Field(None, max_length=100, description="其他癌前状态疾病名称")


class JWS(BaseModel):
    高血压病标志: Optional[Literal["无", "有", "不详"]] = Field(None, description="高血压病标志")
    糖尿病标志: Optional[Literal["无", "有", "不详"]] = Field(None, description="糖尿病标志")
    冠心病标志: Optional[Literal["无", "有", "不详"]] = Field(None, description="冠心病标志")
    血液系统疾病标志: Optional[Literal["无", "有", "不详"]] = Field(None, description="血液系统疾病标志")
    血液系统疾病名称: Optional[List[Literal["白血病", "贫血", "淋巴瘤", "其他"]]] = Field(None,
                                                                                          description="血液系统疾病名称")
    其他血液系统疾病名称: Optional[str] = Field(None, max_length=100, description="其他血液系统疾病名称")
    其他肿瘤病标志: Optional[Literal["是", "否", "不详"]] = Field(None, description="其他肿瘤病标志")
    其他肿瘤疾病名称: Optional[str] = Field(None, max_length=200, description="其他肿瘤疾病名称")
    抗凝药物史标志: Optional[Literal["否", "是", "不详"]] = Field(None, description="抗凝药物史标志")
    抗凝药物史类型: Optional[List[Literal["华法林", "氯吡格雷", "泰嘉", "波立维", "阿司匹林", "其他"]]] = Field(None,
                                                                                                                description="抗凝药物史类型")
    抗凝药物名称: Optional[str] = Field(None, max_length=100, description="抗凝药物名称")


class GRS(BaseModel):
    吸烟标志: Optional[Literal["是", "否", "不详"]] = Field(None, description="吸烟标志")
    饮酒标志: Optional[Literal["是", "否", "不详"]] = Field(None, description="饮酒标志")
    嚼槟榔标志: Optional[Literal["是", "否", "不详"]] = Field(None, description="嚼槟榔标志")


class HYS(BaseModel):
    婚姻状态: Optional[Literal["未婚", "已婚", "丧偶", "离婚", "再婚", "其他", "未说明的婚姻状况"]] = Field(None,
                                                                                                            description="婚姻状态")
    生育情况: Optional[Literal["是", "否", "不详"]] = Field(None, description="生育情况")

class MedicalHistory(BaseModel):
    """一诉五史"""
    XBS: XBS
    JWS: JWS
    GRS: GRS
    HYS: HYS
class SurgeryRecord(BaseModel):
    """手术记录"""
    颈部淋巴结清扫手术类型: Optional[Literal[
        "无",
        "根治性颈清（I-V）",
        "加强预防性颈清（I-IV）",
        "预防性颈清（I-III、肩胛舌骨/舌骨）",
        "选择性颈清",
        "不详"
    ]] = Field(None, description="颈部淋巴结清扫手术类型")

    皮瓣修复手术标志: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="皮瓣修复手术标志"
    )

    气管切开手术标志: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="气管切开手术标志"
    )

    输血情况标志: Optional[Literal["无", "有", "不详"]] = Field(
        None, description="输血情况标志"
    )

    ICU住院治疗标志: Optional[Literal["无", "有", "不详"]] = Field(
        None, description="ICU住院治疗标志"
    )


class AnatomicalDescription(BaseModel):
    """专科_解剖学部位描述信息分组模型"""
    解剖学部位描述信息: Optional[Literal["无", "有", "不详"]] = Field(
        None, description="解剖学部位描述信息"
    )
    原发部位: Optional[Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ]] = Field(None, description="原发部位")
    其他原发部位: Optional[str] = Field(
        None, max_length=100, description="其他原发部位"
    )
    肿瘤位置: Optional[Literal["左侧", "右侧", "双侧", "不详"]] = Field(
        None, description="肿瘤位置"
    )
    肿瘤大小: Optional[Literal["≤2", "≤4（＞2）", "＞4", "不详"]] = Field(
        None, description="肿瘤大小(cm)"
    )


class LymphNodeStatus(BaseModel):
    """专科_阳性淋巴结描述信息分组模型"""
    阳性淋巴结描述信息: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="阳性淋巴结描述信息"
    )
    阳性淋巴结区域: Optional[Literal[
        "I区", "II区", "III区", "IV区", "V区", "不详", "其他"
    ]] = Field(None, description="阳性淋巴结区域(多选)")
    阳性淋巴结其他区域: Optional[str] = Field(
        None, max_length=100, description="阳性淋巴结其他区域"
    )
    阳性淋巴结位置: Optional[Literal["左侧", "右侧", "不详", "双侧"]] = Field(
        None, description="阳性淋巴结位置"
    )
    阳性淋巴结数量: Optional[int] = Field(
        None, ge=0, le=99, description="阳性淋巴结数量"
    )
    淋巴结总数量: Optional[int] = Field(
        None, ge=0, le=99, description="淋巴结总数量"
    )
    阳性淋巴结直径: Optional[Literal["≤3", "≤6（＞3）", "＞6", "不详"]] = Field(
        None, description="阳性淋巴结直径(cm)"
    )
class SJLBJ_ZK(BaseModel):
    淋巴结左侧I区: LymphNodeStatus = Field(None, description="左侧I区的淋巴结信息")
    淋巴结左侧II区: LymphNodeStatus = Field(None, description="左侧II区的淋巴结信息")
    淋巴结左侧III区: LymphNodeStatus = Field(None, description="左侧III区的淋巴结信息")
    淋巴结左侧IV区: LymphNodeStatus = Field(None, description="左侧IV区的淋巴结信息")
    淋巴结左侧V区: LymphNodeStatus = Field(None, description="左侧V区的淋巴结信息")

    淋巴结右侧I区: LymphNodeStatus = Field(None, description="右侧I区的淋巴结信息")
    淋巴结右侧II区: LymphNodeStatus = Field(None, description="右侧II区的淋巴结信息")
    淋巴结右侧III区: LymphNodeStatus = Field(None, description="右侧III区的淋巴结信息")
    淋巴结右侧IV区: LymphNodeStatus = Field(None, description="右侧IV区的淋巴结信息")
    淋巴结右侧V区: LymphNodeStatus = Field(None, description="右侧V区的淋巴结信息")

    淋巴结未知方位I区: LymphNodeStatus = Field(None, description="未知方位I区的淋巴结信息")
    淋巴结未知方位II区: LymphNodeStatus = Field(None, description="未知方位II区的淋巴结信息")
    淋巴结未知方位III区: LymphNodeStatus = Field(None, description="未知方位III区的淋巴结信息")
    淋巴结未知方位IV区: LymphNodeStatus = Field(None, description="未知方位IV区的淋巴结信息")
    淋巴结未知方位V区: LymphNodeStatus = Field(None, description="未知方位V区的淋巴结信息")

class SpecialExam(BaseModel):
    """专科检查"""
    原发灶部位: Optional[Literal["左侧", "右侧", "双侧", "不详"]] = Field(
        None, description="原发灶部位"
    )
    口腔病灶部位: Optional[List[Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ]]] = Field(None, description="口腔病灶部位(ICD-O-3诊断部位)")
    口腔病灶个数: Optional[Literal["1", "2", "3", "4", ">4", "不详"]] = Field(
        None, description="口腔病灶个数"
    )
    口腔病灶大小: Optional[Literal["≤2", "≤4（＞2）", "＞4", "不详"]] = Field(
        None, description="口腔病灶大小"
    )
    ZK_JPXBWMSXX: Optional[List[AnatomicalDescription]] = Field(
        None, description="专科_解剖学部位描述信息分组"
    )
    ZK_YXLBJMSXX: Optional[SJLBJ_ZK] = Field(
        None, description="专科_阳性淋巴结描述信息分组"
    )


class ImageAnatomicalDescription(BaseModel):
    """影像_解剖学部位描述信息分组模型"""
    影像检查类型: Optional[Literal["CT", "MRI", "PET-CT", "超声", "不详"]] = Field(
        None, description="影像检查类型"
    )
    原发部位: Optional[Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ]] = Field(None, description="原发部位")
    其他原发部位: Optional[str] = Field(
        None, max_length=100, description="其他原发部位"
    )
    肿瘤位置: Optional[Literal["左侧", "右侧", "双侧", "不详"]] = Field(
        None, description="肿瘤位置"
    )
    肿瘤大小: Optional[Literal["≤2", "≤4（＞2）", "＞4", "不详"]] = Field(
        None, description="肿瘤大小(cm)"
    )


class ImageLymphNodeStatus(BaseModel):
    """影像_阳性淋巴结描述信息分组模型"""
    影像检查类型: Optional[Literal["CT", "MRI", "PET-CT", "超声", "不详"]] = Field(
        None, description="影像检查类型"
    )
    阳性淋巴结区域: Optional[Literal[
        "I区", "II区", "III区", "IV区", "V区", "不详", "其他"
    ]] = Field(None, description="阳性淋巴结区域")
    阳性淋巴结其他区域: Optional[str] = Field(
        None, max_length=100, description="阳性淋巴结其他区域"
    )
    阳性淋巴结位置: Optional[Literal["左侧", "右侧", "不详", "双侧"]] = Field(
        None, description="阳性淋巴结位置"
    )
    阳性淋巴结数量: Optional[int] = Field(
        None, ge=0, le=99, description="阳性淋巴结数量"
    )
    淋巴结总数量: Optional[int] = Field(
        None, ge=0, le=99, description="淋巴结总数量"
    )
    阳性淋巴结直径: Optional[Literal["≤3", "≤6（＞3）", "＞6", "不详"]] = Field(
        None, description="阳性淋巴结直径(cm)"
    )
    淋巴结转移包膜外ENE: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="淋巴结转移包膜外ENE(+)标志"
    )
class SJLBJ_Image(BaseModel):
    淋巴结左侧I区: ImageLymphNodeStatus = Field(None, description="左侧I区的淋巴结信息")
    淋巴结左侧II区: ImageLymphNodeStatus = Field(None, description="左侧II区的淋巴结信息")
    淋巴结左侧III区: ImageLymphNodeStatus = Field(None, description="左侧III区的淋巴结信息")
    淋巴结左侧IV区: ImageLymphNodeStatus = Field(None, description="左侧IV区的淋巴结信息")
    淋巴结左侧V区: ImageLymphNodeStatus = Field(None, description="左侧V区的淋巴结信息")

    淋巴结右侧I区: ImageLymphNodeStatus = Field(None, description="右侧I区的淋巴结信息")
    淋巴结右侧II区: ImageLymphNodeStatus = Field(None, description="右侧II区的淋巴结信息")
    淋巴结右侧III区: ImageLymphNodeStatus = Field(None, description="右侧III区的淋巴结信息")
    淋巴结右侧IV区: ImageLymphNodeStatus = Field(None, description="右侧IV区的淋巴结信息")
    淋巴结右侧V区: ImageLymphNodeStatus = Field(None, description="右侧V区的淋巴结信息")


    淋巴结未知方位I区: ImageLymphNodeStatus = Field(None, description="未知方位I区的淋巴结信息")
    淋巴结未知方位II区: ImageLymphNodeStatus = Field(None, description="未知方位II区的淋巴结信息")
    淋巴结未知方位III区: ImageLymphNodeStatus = Field(None, description="未知方位III区的淋巴结信息")
    淋巴结未知方位IV区: ImageLymphNodeStatus = Field(None, description="未知方位IV区的淋巴结信息")
    淋巴结未知方位V区: ImageLymphNodeStatus = Field(None, description="未知方位V区的淋巴结信息")



class ImageExaminationRecord(BaseModel):
    """影像检查完整记录主模型"""
    解剖学部位描述信息: Optional[Literal["无", "有", "不详"]] = Field(
        None, description="解剖学部位描述信息"
    )
    阳性淋巴结描述信息: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="阳性淋巴结描述信息"
    )
    YX_JPXBWMSXX: Optional[List[ImageAnatomicalDescription]] = Field(
        None, description="影像_解剖学部位描述信息分组"
    )
    YX_YXLBJMSXX: Optional[SJLBJ_Image] = Field(
        None, description="影像_阳性淋巴结描述信息分组"
    )


# 病理
class PathologicalAnatomicalDescription(BaseModel):
    """病理_解剖学部位描述信息分组模型"""
    解剖学部位描述信息: Optional[Literal["无", "有", "不详"]] = Field(
        None, description="解剖学部位描述信息"
    )
    原发部位: Optional[Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ]] = Field(None, description="原发部位")
    其他原发部位: Optional[str] = Field(
        None, max_length=100, description="其他原发部位"
    )
    肿瘤位置: Optional[Literal["左侧", "右侧", "双侧", "不详"]] = Field(
        None, description="肿瘤位置"
    )
    肿瘤大小: Optional[Literal["≤2", "≤4（＞2）", "＞4", "不详"]] = Field(
        None, description="肿瘤大小(cm)"
    )
    浸润深度: Optional[Literal["≤5", "≤10（＞5）", "＞10"]] = Field(
        None, description="浸润深度(mm)"
    )
    累及部位: Optional[List[Literal[
        "皮质骨（上颌骨或下颌骨）", "下牙槽神经管-下牙槽神经", "口底部",
        "面部皮肤（即颏部-下巴或鼻部）", "舌外肌（颏舌肌、舌咽肌、腭舌肌和茎突舌肌）",
        "上颌窦", "咀嚼肌间隙(咬肌，翼内肌，翼外肌，颞肌)", "翼状板（翼板）",
        "颅底并/或包绕颈内动脉", "其他", "不详"
    ]]] = Field(None, description="累及部位")
    其他累及部位: Optional[str] = Field(
        None, max_length=100, description="其他累及部位"
    )


class LymphNodeExamination(BaseModel):
    """送检淋巴结分组模型"""
    阳性淋巴结区域: Optional[Literal["I区", "II区", "III区", "IV区", "V区", "不详", "其他"]] = Field(
        None, description="阳性淋巴结区域"
    )
    阳性淋巴结其他区域: Optional[str] = Field(
        None, max_length=100, description="阳性淋巴结其他区域"
    )
    阳性淋巴结位置: Optional[Literal["左侧", "右侧", "不详", "双侧"]] = Field(
        None, description="阳性淋巴结位置"
    )
    阳性淋巴结数目: Optional[int] = Field(
        None, ge=0, le=99, description="阳性淋巴结数目"
    )
    送检淋巴结总数目: Optional[int] = Field(
        None, ge=0, le=99, description="送检淋巴结总数目"
    )
    阳性淋巴结直径: Optional[Literal["≤3", "≤6（＞3）", "＞6", "不详"]] = Field(
        None, description="阳性淋巴结直径"
    )
    包膜外侵犯: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="包膜外侵犯"
    )


class ENEStatus(BaseModel):
    """淋巴结转移包膜外分组模型"""
    淋巴结转移包膜外ENE方位: Optional[Literal["左侧", "右侧", "不详"]] = Field(
        None, description="淋巴结转移包膜外ENE(+)方位"
    )
    淋巴结转移包膜外ENE区域: Optional[Literal["I区", "II区", "III区", "IV区", "V区", "不详"]] = Field(
        None, description="淋巴结转移包膜外ENE(+)区域"
    )


class PathologicalPart1(BaseModel):
    病理TNM分期: Optional[str] = Field(
        None, max_length=100, description="病理TNM分期"
    )
    组织学类型: Optional[Literal["鳞状细胞癌", "其他"]] = Field(
        None, description="组织学类型"
    )
    癌肿分类: Optional[Literal["口腔癌", "口咽癌", "其他"]] = Field(
        None, description="癌肿分类"
    )
    分化程度: Optional[Literal[
        "高分化（I级）", "高-中分化（I-II级）", "中分化（II级）",
        "中-低分化（II-III级）", "低分化（III级）", "未分化（IV级）"
    ]] = Field(None, description="分化程度")
    免疫组化标志: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="免疫组化标志"
    )
    HPV免疫组化结果: Optional[Literal["阴性（-）", "阳性（+）", "不详"]] = Field(
        None, description="HPV免疫组化结果"
    )
    P16免疫组化指标: Optional[Literal["阴性（-）", "阳性（+）", "不详"]] = Field(
        None, description="P16免疫组化指标"
    )
    术后病理切缘: Optional[Literal["阴性（-）", "阳性（+）", "切缘过近或者不足"]] = Field(
        None, description="术后病理切缘"
    )
    神经侵犯: Optional[Literal["否", "是"]] = Field(
        None, description="神经侵犯"
    )
    脉管侵犯: Optional[Literal["否", "是"]] = Field(
        None, description="脉管侵犯"
    )
    阳性淋巴结描述信息: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="阳性淋巴结描述信息"
    )
    阳性淋巴结描述信息标志: Optional[Literal["否", "是", "不详"]] = Field(
        None, description="阳性淋巴结描述信息标志"
    )


class PathologicalPart2(BaseModel):
    BL_JPXBWMSXX: Optional[List[PathologicalAnatomicalDescription]] = Field(
        None, description="病理_解剖学部位描述信息分组"
    )


class PathologicalPart3(BaseModel):
    ENE: Optional[List[ENEStatus]] = Field(
        None, description="淋巴结转移包膜外分组"
    )


class PathologicalPart4(BaseModel):
    淋巴结左侧I区: LymphNodeExamination = Field(None, description="左侧I区的淋巴结信息")
    淋巴结左侧II区: LymphNodeExamination = Field(None, description="左侧II区的淋巴结信息")
    淋巴结左侧III区: LymphNodeExamination = Field(None, description="左侧III区的淋巴结信息")
    淋巴结左侧IV区: LymphNodeExamination = Field(None, description="左侧IV区的淋巴结信息")
    淋巴结左侧V区: LymphNodeExamination = Field(None, description="左侧V区的淋巴结信息")

    淋巴结右侧I区: LymphNodeExamination = Field(None, description="右侧I区的淋巴结信息")
    淋巴结右侧II区: LymphNodeExamination = Field(None, description="右侧II区的淋巴结信息")
    淋巴结右侧III区: LymphNodeExamination = Field(None, description="右侧III区的淋巴结信息")
    淋巴结右侧IV区: LymphNodeExamination = Field(None, description="右侧IV区的淋巴结信息")
    淋巴结右侧V区: LymphNodeExamination = Field(None, description="右侧V区的淋巴结信息")


class PathologicalExamination(BaseModel):
    """病理检查完整记录主模型"""
    PathologicalPart1: PathologicalPart1
    PathologicalPart2: PathologicalPart2
    PathologicalPart3: PathologicalPart3
    PathologicalPart4: PathologicalPart4


class OralCancerRecord(BaseModel):
    """口腔癌患者完整记录"""
    medical_history: Optional[MedicalHistory] = None
    surgery_record: Optional[SurgeryRecord] = None
    special_exam: Optional[SpecialExam] = None
    image_exam: Optional[ImageExaminationRecord] = None
    pathological_exam: Optional[PathologicalExamination] = None
