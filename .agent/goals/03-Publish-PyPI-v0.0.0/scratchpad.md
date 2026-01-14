# Goal 03: Publish v0.0.0 to PyPI

> **Status**: 🟢 Complete
> **Priority**: P0 (Critical)
> **Created**: 2026-01-14
> **Updated**: 2026-01-14
> **Completed**: 2026-01-14

## Overview

Publish the first version (v0.0.0) of `real-estate-sustainability-mcp` to PyPI. This validates both the package structure and the release workflow before iterating on features.

## Success Criteria

- [x] Package builds successfully with `uv build`
- [x] `uv publish` or GitHub Actions publishes to PyPI
- [x] Package installable via `uvx real-estate-sustainability-mcp`
- [x] Server starts after install: `uvx real-estate-sustainability-mcp --help`
- [x] Version 0.0.0 visible on https://pypi.org/project/real-estate-sustainability-mcp/
- [x] v0.0.1 also published (fixed project name references)

## Context & Background

Per `.rules` versioning guidelines:
- First version is always 0.0.0
- Tests both initial implementation AND release workflow
- Publish to real PyPI (not TestPyPI) to validate full workflow

The project has GitHub Actions configured for PyPI trusted publisher.

## Constraints & Requirements

- **Hard Requirements**: 
  - All tests pass before publishing
  - Linting passes (`ruff check`)
  - Version in `pyproject.toml` is `0.0.0`
  - PyPI trusted publisher configured
- **Soft Requirements**: 
  - CHANGELOG.md updated
  - README accurate
- **Out of Scope**: 
  - Feature completeness (that's future versions)
  - Docker image publishing (separate workflow)

## Approach

1. Verify all tests pass (Goal-01)
2. Verify server starts (Goal-02)
3. Build package locally to test
4. Create git tag `v0.0.0`
5. Push tag to trigger GitHub Actions publish
6. Verify installation works

## Tasks

| Task ID | Description | Status | Depends On |
|---------|-------------|--------|------------|
| Task-01 | Verify tests pass and lint clean | 🟢 | Goal-01 |
| Task-02 | Update CHANGELOG.md for v0.0.0 | 🟢 | - |
| Task-03 | Build package locally: `uv build` | 🟢 | Task-01 |
| Task-04 | Test local install: `uv pip install dist/*.whl` | 🟢 | Task-03 |
| Task-05 | Configure PyPI trusted publisher (if not done) | 🟢 | - |
| Task-06 | Create and push git tag `v0.0.0` | 🟢 | Task-04 |
| Task-07 | Verify GitHub Actions publish workflow | 🟢 | Task-06 |
| Task-08 | Test installation: `uvx real-estate-sustainability-mcp --help` | 🟢 | Task-07 |
| Task-09 | Fix remaining template references, publish v0.0.1 | 🟢 | Task-08 |
| Task-10 | Set up self-hosted GitHub Actions runner | 🟢 | - |

## PyPI Trusted Publisher Setup

From README, configure at https://pypi.org/manage/account/publishing/:

| Field | Value |
|-------|-------|
| Project name | `real-estate-sustainability-mcp` |
| Owner | `l4b4r4b4b4` |
| Repository | `real-estate-sustainability-mcp` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

## Commands

```bash
# Build package
uv build

# Test local install
uv pip install dist/real_estate_sustainability_mcp-0.0.0-py3-none-any.whl

# Create and push tag
git tag v0.0.0
git push origin v0.0.0

# Test after PyPI publish
uvx real-estate-sustainability-mcp --help
uvx real-estate-sustainability-mcp streamable-http --port 8001
```

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| PyPI name taken | High | Low | Check availability first |
| Trusted publisher misconfigured | Medium | Medium | Test with dry-run if possible |
| Package structure wrong | High | Medium | Test local install first |

## Dependencies

- **Upstream**: Goal-01 (tests pass), Goal-02 (server works)
- **Downstream**: All future goals (can install from PyPI)

## Notes & Decisions

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| - | Start at 0.0.0 not 0.1.0 | Per .rules - test release workflow early |
| - | Use GitHub Actions not manual publish | Reproducible, auditable releases |

### Version Progression Plan

```
0.0.0 - Initial release (this goal) - basic server, demo tools
0.0.1 - Fix issues from 0.0.0 feedback
0.0.2 - Add Excel analysis tools
0.0.3 - Add PDF analysis tools
0.1.0 - After ~5-10 patches, feature-complete MVP
1.0.0 - Production-ready after 6+ months stable usage
```

### Open Questions

- [x] Is PyPI name `real-estate-sustainability-mcp` available? **Yes - claimed**
- [x] Is trusted publisher already configured from template? **No - configured manually**

## Completion Summary

**Date**: 2026-01-14

### What was done:
1. Created GitHub repo: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp
2. Configured PyPI trusted publisher for `publish.yml` workflow
3. Published v0.0.0 to PyPI (first release)
4. Found and fixed remaining `fastmcp-template` references in CLI
5. Published v0.0.1 to PyPI (fixed project name)
6. Set up self-hosted GitHub Actions runner on Threadripper workstation
7. Configured `RUNNER_LABEL` repo variable to use self-hosted runner

### Releases:
- v0.0.0: Initial release, validates package structure
- v0.0.1: Fixed CLI name display (`real-estate-sustainability-mcp 0.0.1`)

### Self-hosted runner configured:
- Labels: `self-hosted`, `nixos`, `threadripper`, `64-core`
- 32-core / 64-thread AMD Threadripper 3970X
- 64GB RAM
- Future workflows will use this runner for faster builds

### PyPI Package:
```bash
uvx real-estate-sustainability-mcp --version
# Output: real-estate-sustainability-mcp 0.0.1
```

## References

- PyPI: https://pypi.org/project/real-estate-sustainability-mcp/
- GitHub Actions: `.github/workflows/publish.yml`
- Versioning: `.rules` versioning section