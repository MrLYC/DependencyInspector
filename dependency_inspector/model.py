from typing import Any, Iterable, List

from packaging.requirements import Requirement as BaseRequirement
from packaging.specifiers import SpecifierSet
from pydantic import BaseModel, Field, PrivateAttr
from resolvelib.resolvers import Result


class Requirement(BaseModel):
    name: str
    version: str = ""
    enabled: bool = True
    _base_requirement: BaseRequirement = PrivateAttr()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        version = self.version.replace(".x", ".*").replace(".*.*", ".*")
        try:
            self._base_requirement = BaseRequirement(f"{self.name} {version}")
        except Exception:
            self._base_requirement = BaseRequirement(f"{self.name}=={version}")

    @property
    def specifier(self) -> SpecifierSet:
        return self._base_requirement.specifier

    @property
    def requirement_string(self) -> str:
        return f"{self.name}{str(self.specifier)}"

    def is_satisfy(self, version: str) -> bool:
        return version in self.specifier

    @classmethod
    def from_requirement_string(cls, requirement_string: str) -> "Requirement":
        r = BaseRequirement(requirement_string)
        return cls(name=r.name, version=str(r.specifier))

    def __str__(self) -> str:
        return self.requirement_string


class Artifact(BaseModel):
    name: str
    version: str
    dependencies: List[Requirement] = Field(default_factory=list)

    @property
    def requirement_string(self) -> str:
        return f"{self.name}=={self.version}"

    def get_dependencies(self) -> Iterable[Requirement]:
        for dependency in self.dependencies:
            if not dependency.enabled:
                continue

            yield dependency

    def __str__(self) -> str:
        return self.requirement_string


class Resolution(BaseModel):
    result: Result[Requirement, Artifact, str]

    @property
    def graph(self) -> Iterable[str]:
        result = self.result
        for source in result.graph:
            targets = ", ".join(i for i in result.graph.iter_children(source) if i)
            if targets:
                yield f"{source or '*'} --> {targets}"

    @property
    def resolution(self) -> Iterable[str]:
        for candidate in self.result.mapping.values():
            yield f"{candidate.name}=={candidate.version}"

    @property
    def artifacts(self) -> Iterable[Artifact]:
        for candidate in self.result.mapping.values():
            yield Artifact(name=candidate.name, version=candidate.version)
