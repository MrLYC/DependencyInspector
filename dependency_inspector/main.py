import glob
import logging
import sys
from typing import Iterable, List

import click
import yaml
from resolvelib import BaseReporter, Resolver
from resolvelib.resolvers import ResolutionImpossible

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
        rendered_artifacts = yaml.safe_dump_all(i.model_dump(exclude_unset=True) for i in resolution.artifacts)
        print("--- Snapshot ---", rendered_artifacts, sep="\n")


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


def load_artifacts_registry(artifacts: Iterable[str]) -> ArtifactRegistry:
    registry = ArtifactRegistry()
    for artifact in load_artifacts(artifacts):
        registry.declare_artifact(artifact)

    return registry


@click.group()
@click.option(
    "--log-level", default="WARNING", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), help="log level"
)
def main(log_level: str) -> None:
    import pdb

    pdb.set_trace()
    logging.basicConfig(level=log_level, stream=sys.stderr)


@click.command()
@click.option("-a", "--artifacts", default=[], multiple=True, required=True, help="defined artifacts")
@click.option("-r", "--requirements", default=[], multiple=True, help="requirements to resolve")
@click.option("--prefer-older", is_flag=True, help="prefer older versions")
@click.option("--disable-dependency-graph", is_flag=True, help="disable dependency graph")
@click.option("--disable-dependency-resolution", is_flag=True, help="disable dependency resolution")
@click.option("--disable-artifact-resolution", is_flag=True, help="disable artifact resolution")
def resolve(
    artifacts: List[str],
    requirements: List[str],
    prefer_older: bool,
    disable_dependency_graph: bool,
    disable_dependency_resolution: bool,
    disable_artifact_resolution: bool,
) -> None:
    registry = load_artifacts_registry(artifacts)

    if not requirements:
        requirements = list(registry.caches.keys())

    provider = ArtifactProvider(registry=registry, prefer_newer=not prefer_older)
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
            disable_dependency_graph,
            disable_dependency_resolution,
            disable_artifact_resolution,
        )


if __name__ == "__main__":
    main.add_command(resolve)
    main()
