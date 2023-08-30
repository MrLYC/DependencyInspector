# dependency-inspector

[![Release](https://img.shields.io/github/v/release/mrlyc/dependency-inspector)](https://img.shields.io/github/v/release/mrlyc/dependency-inspector)
[![Build status](https://img.shields.io/github/actions/workflow/status/mrlyc/dependency-inspector/main.yml?branch=main)](https://github.com/mrlyc/dependency-inspector/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/mrlyc/dependency-inspector/branch/main/graph/badge.svg)](https://codecov.io/gh/mrlyc/dependency-inspector)
[![Commit activity](https://img.shields.io/github/commit-activity/m/mrlyc/dependency-inspector)](https://img.shields.io/github/commit-activity/m/mrlyc/dependency-inspector)
[![License](https://img.shields.io/github/license/mrlyc/dependency-inspector)](https://img.shields.io/github/license/mrlyc/dependency-inspector)

A common dependencies checker/resolver.

- **Github repository**: <https://github.com/mrlyc/dependency-inspector/>
- **Documentation** <https://mrlyc.github.io/dependency-inspector/>

## Installation

```bash
pip install dependency-inspector
```

## Getting started

Assuming you have two interdependent services, write the dependencies into *artifact.yaml* in the following format:

```yaml
name: app-frontend
version: "1.1.2"
dependencies:
  - name: app-backend
    version: "1.x.x"
---
name: app-backend
version: "1.0.1"
dependencies:
  - name: app-frontend
    version: ">1.0"
---
name: app-backend
version: "1.0.10"
dependencies:
  - name: app-frontend
    version: ">1.1"
```

Run this command to resolve the dependencies:

```bash
dependency_inspector --artifacts artifact.yaml      
```

> --- Dependency Graph ---  
> \* --> app-frontend, app-backend  
> app-frontend --> app-backend  
> app-backend --> app-frontend  
>   
> --- Resolution ---  
> app-frontend==1.1.2  
> app-backend==1.0.10  