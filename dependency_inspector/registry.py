from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from .model import Artifact


@dataclass
class ArtifactRegistry:
    caches: Dict[str, List[Artifact]] = field(default_factory=lambda: defaultdict(list))

    def _fetch_candidates(self, name: str) -> List[Artifact]:
        raise KeyError(name)

    def declare_artifact(self, artifact: Artifact) -> None:
        self.caches[artifact.name].append(artifact)

    def get_candidates(self, name: str) -> List[Artifact]:
        if name in self.caches:
            return self.caches[name]

        fetched = self._fetch_candidates(name)
        self.caches[name] = fetched
        return fetched
