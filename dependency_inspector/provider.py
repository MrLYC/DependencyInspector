import logging
from dataclasses import dataclass
from operator import attrgetter
from typing import Any, Iterable, List, Mapping, Protocol, Union

from resolvelib.providers import AbstractProvider

from .model import Artifact, Requirement

logger = logging.getLogger(__name__)


class ArtifactRegistry(Protocol):
    def get_candidates(self, name: str) -> List[Artifact]:
        ...


@dataclass
class ArtifactProvider(AbstractProvider):
    registry: ArtifactRegistry
    prefer_newer: bool = True

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
        preference = sum(1 for _ in candidates[identifier])
        logger.debug("preference: %s for %s", preference, identifier)
        return preference

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
        results = sorted(candidates, key=attrgetter("version"), reverse=self.prefer_newer)
        logger.debug("found %s candidates for %s", len(results), identifier)

        return results

    def is_satisfied_by(self, requirement: Requirement, candidate: Artifact) -> bool:
        if requirement.name != candidate.name:
            return False

        result = requirement.is_satisfy(candidate.version)
        logger.debug("check the requirement %s is satisfied by %s: %s", requirement, candidate, result)

        return result

    def get_dependencies(self, candidate: Artifact) -> Iterable[Requirement]:
        return candidate.get_dependencies()
