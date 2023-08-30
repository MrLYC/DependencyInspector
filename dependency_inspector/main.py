import glob
import sys
from argparse import ArgumentParser
from typing import Iterable

import yaml
from resolvelib import BaseReporter, Resolver
from resolvelib.resolvers import ResolutionImpossible, Result

from dependency_inspector.model import Artifact, Requirement
from dependency_inspector.provider import ArtifactProvider
from dependency_inspector.registry import ArtifactRegistry


def display_resolution(result: Result[Requirement, Artifact, str]) -> None:
    """Print pinned candidates and dependency graph to stdout."""
    print("--- Dependency Graph ---")
    for source in result.graph:
        targets = ", ".join(i for i in result.graph.iter_children(source) if i)
        if targets:
            print(f"{source or '*'} --> {targets}")

    print("\n--- Solution ---")
    for candidate in result.mapping.values():
        print(f"{candidate.name}=={candidate.version}")


def display_error(err: ResolutionImpossible) -> None:
    print("--- Dependency Conflicts ---")

    for c in err.causes:
        if c.parent:
            print(f"{c.parent.requirement_string} --> {c.requirement.requirement_string}")
        else:
            print(f"* --> {c.requirement.requirement_string}")

    print("\n!!! Resolution Impossible !!!")


def load_artifacts(path_patterns: Iterable[str]) -> Iterable[Artifact]:
    for pattern in path_patterns:
        for config in glob.glob(pattern):
            with open(config) as f:
                for artifact in yaml.safe_load_all(f):
                    if not artifact:
                        continue

                    yield Artifact(**artifact)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-a", "--artifacts", required=True, action="append", help="artifact configs")
    parser.add_argument("-r", "--requirements", default=[], action="append", help="requirements to resolve")

    args = parser.parse_args()

    registry = ArtifactRegistry()
    for artifact in load_artifacts(args.artifacts):
        registry.declare_artifact(artifact)

    requirements = set(args.requirements) or registry.caches.keys()
    provider = ArtifactProvider(registry=registry)
    reporter = BaseReporter()
    resolver: Resolver = Resolver(provider, reporter)

    try:
        result = resolver.resolve([Requirement.from_requirement_string(r) for r in requirements])
    except ResolutionImpossible as err:
        display_error(err)
        sys.exit(-1)
    else:
        display_resolution(result)
        sys.exit(0)
