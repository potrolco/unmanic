# TARS Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
