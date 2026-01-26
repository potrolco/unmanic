# TARS Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Phase 1 Backend Stability

### Added
- **Structured logging with BoundLogger**: New context-binding logging class in `unmanic/libs/logs.py`
  - Structlog-like immutable context binding (`bind()`, `unbind()`)
  - Automatic injection of context fields into all log messages
  - Supported context keys: worker_id, task_id, task_label, plugin_id, library_id, gpu_id, component
  - Factory method: `UnmanicLogging.get_bound_logger(name, **context)`
  - 17 unit tests in `tests/unit/test_bound_logger.py`

### Changed
- **Centralized API error handling**: New `api_error_handler` decorator in `base_api_handler.py`
  - Consistent exception handling across all API endpoints
  - Proper logging with tracebacks for debugging
  - Maps exceptions to appropriate HTTP status codes:
    - `BaseApiError` → Logged and handled
    - `ValidationError` → 400 Bad Request
    - `FileNotFoundError` → 404 Not Found
    - `PermissionError` → 403 Forbidden
    - `ValueError` → 400 Bad Request
    - `OSError` → 500 Internal Server Error
    - Generic `Exception` → 500 Internal Server Error with traceback
- Refactored 62 API handlers across 9 files to use the new decorator
- Reduced boilerplate try/except blocks by ~60%
- 242 tests passing (100%)

## [Unreleased] - Phase 3 Multi-GPU Support

### Added
- **GPU Manager module**: New `unmanic/libs/gpu_manager.py` with:
  - `GPUType` enum (CUDA, VAAPI, UNKNOWN)
  - `AllocationStrategy` enum (round_robin, least_used, manual)
  - `GPUDevice` dataclass with serialization support
  - `GPUAllocation` dataclass for tracking allocations
  - `GPUManager` singleton class with thread-safe allocation/release
- **GPU settings**: Added to Pydantic settings:
  - `gpu_enabled` - Enable/disable GPU acceleration
  - `gpu_assignment_strategy` - round_robin, least_used, or manual
  - `max_workers_per_gpu` - Concurrent workers per GPU (1-10)
  - `gpu_allowlist` - Comma-separated GPU device IDs to use
  - `gpu_blocklist` - Comma-separated GPU device IDs to exclude
- **Worker GPU integration**: GPU acquisition/release in worker pipeline:
  - Workers acquire GPU before transcoding starts
  - GPU released in finally block for cleanup
  - GPU info included in worker status
  - `get_current_gpu()` method for GPU access
- **GPU status API endpoint**: GET `/api/v2/health/gpu`
  - Returns GPU manager status
  - Lists available GPUs and current allocations
  - Shows allocation strategy and worker limits
- **Unit tests**: 240 tests (up from 222)
  - `tests/unit/test_gpu_manager.py` - GPU manager tests
  - `tests/unit/test_workers_gpu.py` - Worker GPU integration tests
  - `tests/unit/test_gpu_api.py` - GPU status API tests
  - Additional settings tests for GPU configuration

## [Unreleased] - Phase 2 Video Health Checking

### Added
- **Video health checking module**: New `unmanic/libs/health_check.py` with:
  - `HealthStatus` enum (healthy, corrupted, warning, error)
  - `HealthCheckResult` dataclass with JSON serialization
  - `check_file_integrity()` - FFmpeg-based corruption detection
  - `get_file_checksum()` - MD5/SHA256/SHA1 checksum support
  - `quick_health_check()` - Boolean health check helper
  - `compare_checksums()` - Pre/post transcode comparison
- **Health check settings**: Added to Pydantic settings:
  - `enable_pre_transcode_health_check` - Check before processing
  - `enable_post_transcode_health_check` - Check after processing
  - `fail_on_pre_check_corruption` - Block corrupted files
  - `health_check_timeout_seconds` - FFmpeg timeout (30-3600s)
  - `health_check_algorithm` - Checksum algorithm (md5/sha256/sha1)
- **Worker integration**: Health checks in worker pipeline:
  - Pre-transcode validation with configurable fail behavior
  - Post-transcode validation of output files
  - Health status stored in task object
- **Health check API endpoint**: POST `/api/v2/health/file`
  - Check video file integrity on demand
  - Optional checksum generation
  - Returns status, errors, warnings, file metadata
- **Unit tests**: 186 tests (up from 118)
  - `tests/unit/test_health_check.py` - Health check module tests
  - `tests/unit/test_workers_health.py` - Worker integration tests
  - Additional settings tests for health check configuration
  - API endpoint tests for file health check

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
