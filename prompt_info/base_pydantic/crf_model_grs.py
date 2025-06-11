from pydantic import BaseModel, Field
from typing import Literal, Optional, List
import json
from enum import Enum

class HealthHistory(BaseModel):
    smoking: bool = Field(..., alias="吸烟史")
    drinking: bool = Field(..., alias="饮酒史")
    betel_nut: bool = Field(..., alias="槟榔史")