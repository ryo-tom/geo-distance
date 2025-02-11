from pydantic import BaseModel

class DistanceRequest(BaseModel):
    address1: str
    address2: str
