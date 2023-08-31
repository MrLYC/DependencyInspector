# dependency-inspector

[![Release](https://img.shields.io/github/v/release/MrLYC/DependencyInspector)](https://img.shields.io/github/v/release/MrLYC/DependencyInspector)
[![Build status](https://img.shields.io/github/actions/workflow/status/MrLYC/DependencyInspector/main.yml?branch=main)](https://github.com/MrLYC/DependencyInspector/actions/workflows/main.yml?query=branch%3Amaster)
[![codecov](https://codecov.io/gh/MrLYC/DependencyInspector/branch/master/graph/badge.svg)](https://codecov.io/gh/MrLYC/DependencyInspector)
[![Commit activity](https://img.shields.io/github/commit-activity/m/MrLYC/DependencyInspector)](https://img.shields.io/github/commit-activity/m/MrLYC/DependencyInspector)
[![License](https://img.shields.io/github/license/MrLYC/DependencyInspector)](https://img.shields.io/github/license/MrLYC/DependencyInspector)

A common dependencies checker/resolver.

- **Github repository**: <https://github.com/MrLYC/DependencyInspector/>
- **Documentation** <https://mrlyc.github.io/DependencyInspector/>

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
> --- Solution ---  
> app-frontend==1.1.2  
> app-backend==1.0.10  