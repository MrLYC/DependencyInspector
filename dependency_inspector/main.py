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
        if source and targets:
            print(f"{source} -> {targets}")
        elif not source:
            print(f"[{targets}]")

    print("\n--- Resolution ---")
    for artifact, candidate in result.mapping.items():
        print(f"{candidate.name}=={candidate.version}")


def display_error(err: ResolutionImpossible) -> None:
    print("!!! Resolution Impossible !!!")
    for c in err.causes:
        if c.parent:
            print(f"{c.parent.requirement_string} -> {c.requirement.requirement_string}")
        else:
            print(f"[{c.requirement.requirement_string}]")


def load_artifacts(configs: Iterable[str]) -> Iterable[Artifact]:
    for config in configs:
        with open(config) as f:
            for artifact in yaml.safe_load_all(f):
                yield Artifact(**artifact)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-a", "--artifacts", required=True, action="append", help="artifact configs")
    parser.add_argument("-r", "--requirements", required=True, action="append", help="requirements")

    args = parser.parse_args()

    registry = ArtifactRegistry()
    for artifact in load_artifacts(args.artifacts):
        registry.declare_artifact(artifact)

    provider = ArtifactProvider(registry=registry)
    reporter = BaseReporter()
    resolver = Resolver(provider, reporter)  # type: ignore

    try:
        result = resolver.resolve([Requirement.from_requirement_string(r) for r in args.requirements])
    except ResolutionImpossible as err:
        display_error(err)
        sys.exit(-1)
    else:
        display_resolution(result)
        sys.exit(0)


if __name__ == "__main__":
    main()
