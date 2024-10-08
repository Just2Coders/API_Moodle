from pydantic import BaseModel
class Course(BaseModel):
    id: int
    fullname: str
    shortname: str