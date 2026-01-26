# TARS Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Phase 1 Modernization

### Added
- **Type hints**: Added comprehensive type annotations to core modules
  - `unmanic/libs/task.py` - Task and TaskDataStore classes
  - `unmanic/libs/workers.py` - Worker, WorkerSubprocessMonitor classes
  - `unmanic/libs/foreman.py` - Foreman class
- **Pydantic settings module**: New `unmanic/libs/settings.py` with:
  - Type-safe configuration with `UnmanicSettings` class
  - Environment variable support (`UNMANIC_` prefix)
  - Field validation (port ranges, path normalization)
- **Health check API**: New `/api/v2/health` endpoints for monitoring
  - `/health` - Full health status with component checks
  - `/health/live` - Kubernetes liveness probe
  - `/health/ready` - Kubernetes readiness probe
- **Unit tests**: 118 tests with 20% code coverage
  - `tests/unit/test_settings.py` - Settings module tests
  - `tests/unit/test_health_api.py` - Health API tests
  - `tests/unit/test_task.py` - Task/TaskDataStore tests
  - `tests/unit/test_common.py` - Utility function tests
  - `tests/unit/test_config.py` - Config class tests

### Changed
- Google-style docstrings in type-hinted modules
- SQLite configured with WAL mode for better concurrency

## [1.1.0] - 2026-01-26

### Added
- **Configurable paths**: Use `--unmanic_path` CLI argument or `UNMANIC_PATH` environment variable to override default `~/.unmanic` location
- **Bulk delete API**: New `DELETE /api/v2/history/tasks/all` endpoint to delete all completed tasks
  - Optional `?success_only=true` query parameter to only delete successful tasks
- **Pre-commit hooks**: Automated code quality checks (Black, Flake8, trailing whitespace, etc.)
- **GitHub Actions CI**: Automated testing on Python 3.10, 3.11, 3.12 with pre-commit validation

### Changed
- Dropped Python 3.8 and 3.9 support (EOL)
- CI now runs pre-commit as a gate before tests

### Fixed
- Path configuration now properly includes log_path when using custom unmanic_path
- Paths are normalized (tilde expansion, relative to absolute conversion)

### Security
- Custom paths are logged for auditing purposes

## [1.0.0] - Initial TARS Fork

### Added
- Removed library limits (unlimited libraries)
- Force supporter level 100 in all code paths
- Updated branding to TARS (Transcoding Automation & Reorganization System)

### Changed
- Based on Unmanic upstream

---

For more details, see the [TARS Modernization Roadmap](https://github.com/potrolco/unmanic/blob/master/docs/ROADMAP.md).
