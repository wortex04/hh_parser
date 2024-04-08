__all__ = 'Resume'


from pydantic import BaseModel, Field
from typing import Optional, List

class HashableModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))

class Experience(HashableModel):
    period: str
    company: str
    position: str
    description: str

class Education(HashableModel):
    year: str
    university: str
    speciality: str

class Language(HashableModel):
    language: str
    level: str

class ExtraEducation(HashableModel):
    year: str
    name: str
    organization: str

class Test(HashableModel):
    year: str
    name: str
    organization: str

class Resume(HashableModel):
    job: str
    specialization: str
    employment: str
    schedule: str
    experience: str
    other_work: Optional[List[Experience]] = None
    skills: List[str] = None
    my_self: str
    education_level: str
    education: Optional[List[Education]] = None
    languages: Optional[List[Language]] = None
    extra_education: Optional[List[ExtraEducation]] = None
    test: Optional[List[Test]] = None
    citizenship: str

