import glob
import logging
import sys
from argparse import ArgumentParser
from typing import Iterable

import yaml
from resolvelib import BaseReporter, Resolver
from resolvelib.resolvers import ResolutionImpossible, Result

from dependency_inspector.model import Artifact, Requirement, Resolution
from dependency_inspector.provider import ArtifactProvider
from dependency_inspector.registry import ArtifactRegistry


def display_resolution(
    resolution: Resolution, disable_graph: bool, disable_resolution: bool, disable_artifacts: bool
) -> None:
    """Print pinned candidates and dependency graph to stdout."""

    if not disable_graph:
        rendered_graph = "\n".join(resolution.graph)
        print("--- Dependency Graph ---", rendered_graph, sep="\n", end="\n\n")

    if not disable_resolution:
        rendered_resolution = "\n".join(resolution.resolution)
        print("--- Resolution ---", rendered_resolution, sep="\n", end="\n\n")

    if not disable_artifacts:
        rendered_artifacts = yaml.safe_dump_all(i.model_dump() for i in resolution.artifacts)
        print("--- Artifacts ---", rendered_artifacts, sep="\n")


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
    parser.add_argument("--prefer-older", default=False, action="store_true", help="prefer older versions")
    parser.add_argument(
        "--disable-dependency-graph", default=False, action="store_true", help="disable dependency graph"
    )
    parser.add_argument(
        "--disable-dependency-resolution", default=False, action="store_true", help="disable dependency resolution"
    )
    parser.add_argument(
        "--disable-artifact-resolution",
        default=False,
        action="store_true",
        help="disable artifact resolution",
    )
    parser.add_argument(
        "--log-level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="log level"
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, stream=sys.stderr)

    registry = ArtifactRegistry()
    for artifact in load_artifacts(args.artifacts):
        registry.declare_artifact(artifact)

    requirements = set(args.requirements) or registry.caches.keys()
    provider = ArtifactProvider(registry=registry, prefer_newer=not args.prefer_older)
    reporter = BaseReporter()
    resolver: Resolver = Resolver(provider, reporter)

    try:
        result = resolver.resolve([Requirement.from_requirement_string(r) for r in requirements])
    except ResolutionImpossible as err:
        display_error(err)
        sys.exit(-1)
    else:
        display_resolution(
            Resolution(result=result),
            args.disable_dependency_graph,
            args.disable_dependency_resolution,
            args.disable_artifact_resolution,
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
