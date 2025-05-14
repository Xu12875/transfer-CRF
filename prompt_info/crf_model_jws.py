from pydantic import BaseModel, Field, model_validator
from typing import Dict, Optional
import json
from enum import Enum

class MedicalHistory(BaseModel):
    抗凝药物史: bool
    血液系统疾病: bool
    高血压: bool
    糖尿病: bool
    冠心病: bool
    其他肿瘤史: bool



