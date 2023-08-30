from dataclasses import dataclass
from operator import attrgetter
from typing import Any, Iterable, List, Mapping, Protocol, Union

from resolvelib.providers import AbstractProvider

from .model import Artifact, Requirement


class ArtifactRegistry(Protocol):
    def get_candidates(self, name: str) -> List[Artifact]:
        ...


@dataclass
class ArtifactProvider(AbstractProvider):
    registry: ArtifactRegistry

    def identify(self, requirement_or_candidate: Union[Requirement, Artifact]) -> str:
        return requirement_or_candidate.name

    def get_preference(
        self,
        identifier: str,
        resolutions: Mapping[str, Artifact],
        candidates: Mapping[str, Iterable[Artifact]],
        information: Any,
        backtrack_causes: Any,
    ) -> int:
        return sum(1 for _ in candidates[identifier])

    def find_matches(
        self,
        identifier: str,
        requirements: Mapping[str, Iterable[Requirement]],
        incompatibilities: Mapping[str, Iterable[Artifact]],
    ) -> Iterable[Artifact]:
        real_dependencies = list(requirements[identifier])
        bad_versions = {c.version for c in incompatibilities[identifier]}

        # Need to pass the extras to the search, so they
        # are added to the candidate at creation - we
        # treat candidates as immutable once created.
        candidates = (
            candidate
            for candidate in self.registry.get_candidates(identifier)
            if candidate.version not in bad_versions and all(r.is_satisfy(candidate.version) for r in real_dependencies)
        )
        return sorted(candidates, key=attrgetter("version"), reverse=True)

    def is_satisfied_by(self, requirement: Requirement, candidate: Artifact) -> bool:
        if requirement.name != candidate.name:
            return False
        return requirement.is_satisfy(candidate.version)

    def get_dependencies(self, candidate: Artifact) -> Iterable[Requirement]:
        return candidate.get_dependencies()
