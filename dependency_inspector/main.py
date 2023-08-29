
from argparse import ArgumentParser

import yaml
from packaging.requirements import Requirement
from resolvelib import BaseReporter, Resolver
from resolvelib.resolvers import Result

from dependency_inspector.provider import (ArtifactProvider, ArtifactRegistry,
                                           Candidate)


def display_resolution(result:Result[Requirement, Candidate, str]) -> None:
    """Print pinned candidates and dependency graph to stdout."""
    print("\n--- Pinned Candidates ---")
    for artifact, candidate in result.mapping.items():
        print(f"{artifact}: {candidate.name} {candidate.version}")

    print("\n--- Dependency Graph ---")
    for source in result.graph:
        targets = ", ".join(i for i in result.graph.iter_children(source) if i)
        print(f"{source} -> {targets}")


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-a", "--artifacts", required=True, help="artifacts config file")
    parser.add_argument("-r", "--requirements", required=True, action="append", help="requirements")

    args = parser.parse_args()
    with open(args.artifacts) as f:
        artifacts = yaml.safe_load(f)

    registry = ArtifactRegistry(artifacts=artifacts)
    provider = ArtifactProvider(registry=registry)
    reporter = BaseReporter()
    resolver = Resolver(provider, reporter)

    result = resolver.resolve([Requirement(r) for r in args.requirements])
    display_resolution(result)


if __name__ == "__main__":
    main()