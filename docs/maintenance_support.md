# Maintenance & Support Plan

## Versioning
- Semantic Versioning (MAJOR.MINOR.PATCH).

## Branching & Releases
- `main` = stable, `dev` = integration, feature branches via `feat/*`.
- Release artifacts zipped under `release/` and tagged (e.g., v0.1.0).

## Backward Compatibility
- CLI flags and storage schema changes use migration scripts; avoid breaking changes within a MAJOR version.

## Testing & CI
- `pytest` for unit tests. Future CI: GitHub Actions to run tests and package release ZIP.

## Support
- Issues tracked via GitHub Issues. Known issues documented in README.
