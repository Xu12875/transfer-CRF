from pydantic import BaseModel, Field, model_validator
from typing import Dict, Optional,Union
import json
from enum import Enum

class MedicalHistory(BaseModel):
    高血压: bool = Field(False, alias="高血压")
    糖尿病: bool = Field(False, alias="糖尿病")
    冠心病: bool = Field(False, alias="冠心病")
    血液系统疾病: Union[str,bool] = Field(...,alias="血液系统疾病")
    抗凝药物史: Union[str,bool] = Field(...,alias="抗凝药物史")
    其他肿瘤史: bool = Field(...,alias="其他肿瘤史")



