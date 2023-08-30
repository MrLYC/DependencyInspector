from typing import Any, List

from packaging.requirements import Requirement as BaseRequirement
from pydantic import BaseModel, Field, PrivateAttr
from pydantic.dataclasses import dataclass


class Requirement(BaseModel):
    name: str
    version: str = ""
    _base_requirement: BaseRequirement = PrivateAttr()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        try:
            self._base_requirement = BaseRequirement(f"{self.name} {self.version}")
        except Exception as e:
            self._base_requirement = BaseRequirement(f"{self.name}=={self.version}")

    @property
    def requirement_string(self) -> str:
        return f"{self.name}{str(self._base_requirement.specifier)}"

    def is_satisfy(self, version: str) -> bool:
        return version in self._base_requirement.specifier

    @classmethod
    def from_requirement_string(cls, requirement_string: str) -> "Requirement":
        r = BaseRequirement(requirement_string)
        return cls(name=r.name, version=str(r.specifier))


class Artifact(BaseModel):
    name: str
    version: str
    dependencies: List[Requirement] = Field(default_factory=list)

    @property
    def requirement_string(self) -> str:
        return f"{self.name}=={self.version}"