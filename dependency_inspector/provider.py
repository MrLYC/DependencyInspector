from collections import defaultdict
from dataclasses import InitVar, dataclass, field
from operator import attrgetter
from typing import Any, Dict, Iterable, List, Mapping

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


@dataclass
class Candidate:
    name: str
    version: str
    requirements: List[Requirement]


@dataclass
class ArtifactRegistry:
    artifacts: InitVar[List[Dict[str, Any]]]
    registry: Dict[str, List[Candidate]] = field(default_factory=lambda: defaultdict(list))

    def __post_init__(self, artifacts: List[Dict[str, Any]]) -> None:
        for artifact in artifacts:
            self.registry[artifact["name"]].append(Candidate(
                name=artifact["name"],
                version=str(artifact["version"]),
                requirements=[
                    Requirement(r) for r in artifact.get("requirements") or []
                ]
            ))

    def get_candidates(self, name:str) -> List[Candidate]:
        return self.registry[name]


@dataclass
class ArtifactProvider:
    registry: ArtifactRegistry

    def identify(self, requirement_or_candidate: Requirement | Candidate) -> str:
        return canonicalize_name(requirement_or_candidate.name)

    def get_preference(
        self,
        identifier:str,
        resolutions:Mapping[str, Candidate],
        candidates:Mapping[str, Iterable[Candidate]],
        information:Any,
        backtrack_causes:Any
    ) -> int:
        return sum(1 for _ in candidates[identifier])
    
    def find_matches(
        self, 
        identifier: str,
        requirements: Mapping[str, Iterable[Requirement]],
        incompatibilities: Mapping[str, Iterable[Candidate]],
    ) -> Iterable[Candidate]:
        real_requirements = list(requirements[identifier])
        bad_versions = {c.version for c in incompatibilities[identifier]}

        # Need to pass the extras to the search, so they
        # are added to the candidate at creation - we
        # treat candidates as immutable once created.
        candidates = (
            candidate
            for candidate in self.registry.get_candidates(identifier)
            if candidate.version not in bad_versions
            and all(candidate.version in r.specifier for r in real_requirements)
        )
        return sorted(candidates, key=attrgetter("version"), reverse=True)

    def is_satisfied_by(self, requirement: Requirement, candidate: Candidate) -> bool:
        if canonicalize_name(requirement.name) != candidate.name:
            return False
        return candidate.version in requirement.specifier

    def get_dependencies(self, candidate: Candidate) -> Iterable[Requirement]:
        return candidate.requirements