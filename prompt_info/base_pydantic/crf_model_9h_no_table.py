from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Demographic(BaseModel):
    """人口学资料"""
    """患者人口学资料数据模型"""
    HZXM:str = Field(
        None,
        max_length=80,
        description="姓名"
    )
    JZH: str = Field(
        None,
        max_length=50,
        description="住院号"
    )
    XB: Literal["男", "女"] = Field(
        None,
        description="性别"
    )
    NL: float = Field(
        None,
        ge=0,
        le=150,
        description="年龄"
    )
    MZ: Literal["汉族", "其他"] = Field(
        None,
        description="民族"
    )
    QTMZ: str = Field(
        None,
        max_length=100,
        description="其他民族"
    )
    SFZH: str = Field(
        None,
        max_length=20,
        description="身份证号"
    )
    XJD_P: str = Field(
        None,
        max_length=20,
        description="住址-省（直辖市）"
    )
    XJD_C: str = Field(
        None,
        max_length=20,
        description="住址-市"
    )
    XJD_A: str = Field(
        None,
        max_length=20,
        description="住址-区（县）"
    )
    LXFS: str = Field(
        None,
        max_length=20,
        description="联系电话"
    )
    LXRDH: str = Field(
        None,
        max_length=20,
        description="联系人电话"
    )
    RYSJ:datetime = Field(
        None,
        description="住院时间"
    )
    YBLX: Literal[
        "城镇职工基本医疗保险",
        "城镇居民基本医疗保险",
        "新型农村合作医疗",
        "公务员医疗补助",
        "企业补充医疗保险",
        "大额补充医疗保险",
        "商业医疗保险",
        "其他"
    ] = Field(None, description="医保类型")


class XBS(BaseModel):
    SSZLBZ: Literal["无", "有", "不详"] = Field(None, description="既往手术史标志")
    TJZLSSLX: Literal[
        "原发灶扩大切除术",
        "颈部管理（根治性颈清、选择性颈清及其他颈部淋巴结送检）",
        "皮瓣修复",
        "气切术"
    ] = Field(None, description="既往手术类型")
    SFJSZL: Literal["无", "有", "不详"] = Field(None, description="既往系统治疗标志")
    XTZLLX: List[Literal[
        "术前诱导治疗",
        "术后辅助治疗",
        "姑息治疗",
        "靶向治疗",
        "免疫治疗",
        "化学治疗"
    ]] = Field(None, description="既往系统治疗类型")
    ZLYFFXZ: Literal[
        "原发",
        "复发",
        "二原发（不同解剖部位或不同病理诊断，同一部位需要5年以上）",
        "新辅助/诱导",
        "不彻底",
        "不详"
    ] = Field(None, description="肿瘤原复发性质")
    YFSJ:str = Field(None, max_length=100, description="原发时间")
    FFSJFL: Literal[
        "＜3个月",
        "＜6个月（≥3个月）",
        "＜1年（≥6个月）",
        "＜2年（≥1年）",
        "＜3年（≥2年）",
        "＜5年（≥3年）",
        "＜5年（≥2年）",
        "≥5年",
        "不详"
    ] = Field(None, description="复发时间")
    AQZTJBBZ: Literal["无", "有", "不详"] = Field(None, description="癌前状态疾病标志")
    AQZTJBFL: List[Literal[
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
    ]] = Field(None, description="癌前状态疾病名称")
    QTAQZDJB: str = Field(None, max_length=100, description="其他癌前状态疾病名称")


class JWS(BaseModel):
    GXYBZ: Literal["无", "有", "不详"] = Field(None, description="高血压病标志")
    TNBBZ: Literal["无", "有", "不详"] = Field(None, description="糖尿病标志")
    GXBBZ: Literal["无", "有", "不详"] = Field(None, description="冠心病标志")
    XYXTJBBZ: Literal["无", "有", "不详"] = Field(None, description="血液系统疾病标志")
    XYXTJBFL: List[Literal["白血病", "贫血", "淋巴瘤", "其他"]] = Field(None, description="血液系统疾病名称")
    QTXYXTJB: str = Field(None, max_length=100, description="其他血液系统疾病名称")
    ZLBZ: Literal["是", "否", "不详"] = Field(None, description="其他肿瘤病标志")
    ZLMC: str = Field(None, max_length=200, description="其他肿瘤疾病名称")
    KNYWSBZ: Literal["否", "是", "不详"] = Field(None, description="抗凝药物史标志")
    KNYWSLX: List[Literal["华法林", "氯吡格雷", "泰嘉", "波立维", "阿司匹林", "其他"]] = Field(None,    description="抗凝药物史类型")
    KNYWMC: str = Field(None, max_length=100, description="抗凝药物名称")


class GRS(BaseModel):
    SFXY: Literal["是", "否", "不详"] = Field(None, description="吸烟标志")
    SFYJ: Literal["是", "否", "不详"] = Field(None, description="饮酒标志")
    JBLBZ: Literal["是", "否", "不详"] = Field(None, description="嚼槟榔标志")


class HYS(BaseModel):
    HYZK: Literal["未婚", "已婚", "丧偶", "离婚", "再婚", "其他", "未说明的婚姻状况"] = Field(None,        description="婚姻状态")
    SFSY: Literal["是", "否", "不详"] = Field(None, description="生育情况")


class MedicalHistory(BaseModel):
    """一诉五史"""
    XBS: XBS
    JWS: JWS
    GRS: GRS
    HYS: HYS


class PhysicalExam(BaseModel):
    """体格检查"""
    SG: float = Field(
        None,
        ge=0,
        le=300,
        description="身高(cm)",
    )
    TZ: float = Field(
        None,
        ge=0,
        le=500,
        description="体重(kg)",
    )
    BMI: float = Field(
        None,
        ge=0,
        le=100,
        description="BMI指数(kg/m²)",
    )


class SurgeryRecord(BaseModel):
    """手术记录"""
    JBLBJQS: Literal[
        "无",
        "根治性颈清（I-V）",
        "加强预防性颈清（I-IV）",
        "预防性颈清（I-III、肩胛舌骨/舌骨）",
        "选择性颈清",
        "不详"
    ] = Field(None, description="颈部淋巴结清扫手术类型")

    SFPBXF: Literal["否", "是", "不详"] = Field(
        None, description="皮瓣修复手术标志"
    )

    SFQGQK: Literal["否", "是", "不详"] = Field(
        None, description="气管切开手术标志"
    )

    SXBZ: Literal["无", "有", "不详"] = Field(
        None, description="输血情况标志"
    )

    ICUZYZZBZ: Literal["无", "有", "不详"] = Field(
        None, description="ICU住院治疗标志"
    )


class AnatomicalDescription(BaseModel):
    """专科_解剖学部位描述信息分组模型"""
    ZK_SFJPX: Literal["无", "有", "不详"] = Field(
        None, description="解剖学部位描述信息"
    )
    ZK_YFBW: Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ] = Field(None, description="原发部位")
    ZK_QTYFBW: str = Field(
        None, max_length=100, description="其他原发部位"
    )
    ZK_ZLWZ: Literal["左侧", "右侧", "双侧", "不详"] = Field(
        None, description="肿瘤位置"
    )
    ZK_ZLDX: Literal["≤2", "≤4（＞2）", "＞4", "不详"] = Field(
        None, description="肿瘤大小(cm)"
    )


class LymphNodeStatus(BaseModel):
    """专科_阳性淋巴结描述信息分组模型"""
    ZK_SFLBJ: Literal["否", "是", "不详"] = Field(
        None, description="阳性淋巴结描述信息"
    )
    ZK_LBJQY: Literal[
        "I区", "II区", "III区", "IV区", "V区", "不详", "其他"
    ] = Field(None, description="阳性淋巴结区域(多选)")
    ZK_LBJQTQY: str = Field(
        None, max_length=100, description="阳性淋巴结其他区域"
    )
    ZK_YXLBJWZ: Literal["左侧", "右侧", "不详", "双侧"] = Field(
        None, description="阳性淋巴结位置"
    )
    ZK_YXLBJSL: int = Field(
        None, ge=0, le=99, description="阳性淋巴结数量"
    )
    ZK_LBJZSL: int = Field(
        None, ge=0, le=99, description="淋巴结总数量"
    )
    ZK_YXLBJZJ: Literal["≤3", "≤6（＞3）", "＞6", "不详"] = Field(
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
    YFZBW: Literal["左侧", "右侧", "双侧", "不详"] = Field(
        None, description="原发灶部位"
    )
    KQBZBW: List[Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ]] = Field(None, description="口腔病灶部位(ICD-O-3诊断部位)")
    KQBZGS: Literal["1", "2", "3", "4", ">4", "不详"] = Field(
        None, description="口腔病灶个数"
    )
    KQBZDX: Literal["≤2", "≤4（＞2）", "＞4", "不详"] = Field(
        None, description="口腔病灶大小"
    )
    ZK_JPXBWMSXX: List[AnatomicalDescription] = Field(
        None, description="专科_解剖学部位描述信息分组"
    )
    ZK_YXLBJMSXX: SJLBJ_ZK = Field(
        None, description="专科_阳性淋巴结描述信息分组"
    )


class ImageAnatomicalDescription(BaseModel):
    """影像_解剖学部位描述信息分组模型"""
    JPX_YXJCLX: Literal["CT", "MRI", "PET-CT", "超声", "不详"] = Field(
        None, description="影像检查类型"
    )
    YX_YFBW: Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ] = Field(None, description="原发部位")
    YX_QTYFBW: str = Field(
        None, max_length=100, description="其他原发部位"
    )
    YX_ZLWZ: Literal["左侧", "右侧", "双侧", "不详"] = Field(
        None, description="肿瘤位置"
    )
    YX_ZLDX: Literal["≤2", "≤4（＞2）", "＞4", "不详"] = Field(
        None, description="肿瘤大小(cm)"
    )


class ImageLymphNodeStatus(BaseModel):
    """影像_阳性淋巴结描述信息分组模型"""
    LB_YXJCLX: Literal["CT", "MRI", "PET-CT", "超声", "不详"] = Field(
        None, description="影像检查类型"
    )
    YX_LBJQY: Literal[
        "I区", "II区", "III区", "IV区", "V区", "不详", "其他"
    ] = Field(None, description="阳性淋巴结区域")
    YX_LBJQTQY: str = Field(
        None, max_length=100, description="阳性淋巴结其他区域"
    )
    YX_YXLBJWZ: Literal["左侧", "右侧", "不详", "双侧"] = Field(
        None, description="阳性淋巴结位置"
    )
    YX_YXLBJSL: int = Field(
        None, ge=0, le=99, description="阳性淋巴结数量"
    )
    YX_LBJZSL: int = Field(
        None, ge=0, le=99, description="淋巴结总数量"
    )
    YX_YXLBJZJ: Literal["≤3", "≤6（＞3）", "＞6", "不详"] = Field(
        None, description="阳性淋巴结直径(cm)"
    )
    YX_ENEPBZ: Literal["否", "是", "不详"] = Field(
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
    YX_SFJPX: Literal["无", "有", "不详"] = Field(
        None, description="解剖学部位描述信息"
    )
    YX_SFLBJ: Literal["否", "是", "不详"]= Field(
        None, description="阳性淋巴结描述信息"
    )
    YX_JPXBWMSXX: List[ImageAnatomicalDescription] = Field(
        None, description="影像_解剖学部位描述信息分组"
    )
    YX_YXLBJMSXX: SJLBJ_Image = Field(
        None, description="影像_阳性淋巴结描述信息分组"
    )


class PathologicalAnatomicalDescription(BaseModel):
    """病理_解剖学部位描述信息分组模型"""
    BL_SFJPX: Literal["无", "有", "不详"] = Field(
        None, description="解剖学部位描述信息"
    )
    YFBW: Literal[
        "唇部", "颊部", "舌体前2/3", "上牙龈", "下牙龈", "舌根",
        "口底", "口咽", "扁桃体", "磨牙后区", "软腭", "硬腭",
        "牙龈", "累及多部位", "其他", "不详"
    ] = Field(None, description="原发部位")
    JPXBW: str = Field(
        None, max_length=100, description="其他原发部位"
    )
    JPXFW: Literal["左侧", "右侧", "双侧", "不详"] = Field(
        None, description="肿瘤位置"
    )
    YFZDXFL: Literal["≤2", "≤4（＞2）", "＞4", "不详"] = Field(
        None, description="肿瘤大小(cm)"
    )
    JRSDDOI: Literal["≤5", "≤10（＞5）", "＞10"] = Field(
        None, description="浸润深度(mm)"
    )
    LJBW: List[Literal[
        "皮质骨（上颌骨或下颌骨）", "下牙槽神经管-下牙槽神经", "口底部",
        "面部皮肤（即颏部-下巴或鼻部）", "舌外肌（颏舌肌、舌咽肌、腭舌肌和茎突舌肌）",
        "上颌窦", "咀嚼肌间隙(咬肌，翼内肌，翼外肌，颞肌)", "翼状板（翼板）",
        "颅底并/或包绕颈内动脉", "其他", "不详"
    ]] = Field(None, description="累及部位")
    QTLJBW: str = Field(
        None, max_length=100, description="其他累及部位"
    )


class LymphNodeExamination(BaseModel):
    """送检淋巴结分组模型"""
    SJLBJQY: Literal["I区", "II区", "III区", "IV区", "V区", "不详", "其他"] = Field(
        None, description="淋巴结区域"
    )
    SJLBJQTQY: str = Field(
        None, max_length=100, description="淋巴结其他区域"
    )
    SJLBJFW: Literal["左侧", "右侧", "不详", "双侧"] = Field(
        None, description="淋巴结位置"
    )
    LBJYXSL: int = Field(
        None, ge=0, le=99, description="淋巴结转移数量"
    )
    LBJZS: int = Field(
        None, ge=0, le=99, description="送检淋巴结总数目"
    )
    LBJQFSL: int = Field(
        None, ge=0, le=99, description="淋巴结包膜外侵犯数目"
    )
    YXLBJZDZJ: Literal["≤3", "≤6（＞3）", "＞6", "不详"] = Field(
        None, description="淋巴结直径(cm)"
    )
    ENEPBZ: Literal["否", "是", "不详"] = Field(
        None, description="包膜外侵犯"
    )


class ENEStatus(BaseModel):
    """淋巴结转移包膜外分组模型"""
    ENEPFW: Literal["左侧", "右侧", "不详"] = Field(
        None, description="淋巴结转移包膜外ENE(+)方位"
    )
    ENEPQY: Literal["I区", "II区", "III区", "IV区", "V区", "不详"] = Field(
        None, description="淋巴结转移包膜外ENE(+)区域"
    )


class SJLBJZD(BaseModel):
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

    淋巴结未知方位I区: LymphNodeExamination = Field(None, description="未知方位I区的淋巴结信息")
    淋巴结未知方位II区: LymphNodeExamination = Field(None, description="未知方位II区的淋巴结信息")
    淋巴结未知方位III区: LymphNodeExamination = Field(None, description="未知方位III区的淋巴结信息")
    淋巴结未知方位IV区: LymphNodeExamination = Field(None, description="未知方位IV区的淋巴结信息")
    淋巴结未知方位V区: LymphNodeExamination = Field(None, description="未知方位V区的淋巴结信息")


class PathologicalExamination(BaseModel):
    """病理检查完整记录主模型"""
    TNMFQ:str = Field(
        None, max_length=100, description="病理TNM分期"
    )
    TJLAZZXFX: Literal["鳞状细胞癌", "其他"] = Field(
        None, description="组织学类型"
    )
    TJAZFL: Literal["口腔癌", "口咽癌", "其他"] = Field(
        None, description="癌肿分类"
    )
    FHCD: Literal[
        "高分化（I级）", "高-中分化（I-II级）", "中分化（II级）",
        "中-低分化（II-III级）", "低分化（III级）", "未分化（IV级）"
    ] = Field(None, description="分化程度")
    MYZHBZ: Literal["否", "是", "不详"] = Field(
        None, description="免疫组化标志"
    )
    HPVMYZHJG: Literal["阴性（-）", "阳性（+）", "不详"] = Field(
        None, description="HPV免疫组化结果"
    )
    P16MYZHJG: Literal["阴性（-）", "阳性（+）", "不详"] = Field(
        None, description="P16免疫组化指标"
    )
    SHBLQY: Literal["阴性（-）", "阳性（+）", "切缘过近或者不足"] = Field(
        None, description="术后病理切缘"
    )
    SJQF: Literal["否", "是"] = Field(
        None, description="神经侵犯"
    )
    XGQF: Literal["否", "是"] = Field(
        None, description="脉管侵犯"
    )
    BL_SFLBJ: Literal["否", "是", "不详"] = Field(
        None, description="阳性淋巴结描述信息"
    )
    SJLBJBZ: Literal["否", "是", "不详"] = Field(
        None, description="阳性淋巴结描述信息标志"
    )
    BL_JPXBWMSXX: List[PathologicalAnatomicalDescription] = Field(
        None, description="病理_解剖学部位描述信息分组"
    )
    SJLBJ: SJLBJZD = Field(
        None, description="送检淋巴结各分区情况"
    )
    ENE: List[ENEStatus] = Field(
        None, description="淋巴结转移包膜外分组"
    )


class OralCancerRecord(BaseModel):
    """口腔癌患者完整记录"""
    demographic: Demographic = None
    medical_history: MedicalHistory = None
    physical_exam: PhysicalExam = None
    surgery_record: SurgeryRecord = None
    special_exam: SpecialExam = None
    image_exam: ImageExaminationRecord = None
    pathological_exam: PathologicalExamination = None
