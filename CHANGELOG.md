# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.11] - 2026-01-10

### Bug Fixes

- Handling of values passed to filter ops 'exists' and 'does-not-exist'

## [0.5.10] - 2026-01-10

### Bug Fixes

- Validate that columns must be passed to all but 2 CalcOps
- The order of order parameters was wrong (the irony)
- Tests had wrong recipient properties, and add model validation and tests to prevent it in the future

## [0.5.9] - 2026-01-10

### Bug Fixes

- Tags validation

### Features

- Claude skillz

## [0.5.8] - 2026-01-10

### Bug Fixes

- Board query input was missing limits on the limit field

## [0.5.7] - 2026-01-10

### Bug Fixes

- BoardBuilder was accidentally ommitting granularity, filter combination and havings. oops!

## [0.5.6] - 2026-01-10

### Features

- Shared validation infrastructure for tool input validation

## [0.5.5] - 2026-01-09

### Bug Fixes

- A failing triggers integration test

### Features

- Speed up CLI launch by lazy loading tools, also capture control-C better without throwing a traceback
- Add fail-fast validation for duplicate queries and tags

## [0.5.4] - 2026-01-09

### Bug Fixes

- Queries not including ad-hoc calculated fields, and stop swallowing errors

## [0.5.3] - 2026-01-09

### Bug Fixes

- TagInput model needs to be used for SLOs and triggers

## [0.5.2] - 2026-01-09

### Bug Fixes

- QueryBuilder incorrectly added the `alias` property to calcuation when it shouldn't have been there
- SLOBuilder API conformance issues - missing tags, and MD-SLO behavior
- Triggers API conformance
- Recipients API conformance improvements

## [0.5.1] - 2026-01-08

### Bug Fixes

- Fix issue where board and query tool inputs were missing Visualization settings, Chart settings and calculated fields 

* fix issue where board and query tool inputs were missing certain inputs, back them up with pydantic models

## Summary
- Add typed `VisualizationSettingsInput` model for board query panels with proper schema validation
- Add `chart_type` convenience field at the panel level (transforms to `visualization_settings.charts[].chart_type`)
- Add `calculated_fields` support for inline derived columns in queries
- Add `compare_time_offset_seconds` field with validation for historical comparisons
- Add field validator to `QuerySpec` ensuring only valid compare offset values are accepted

## Test plan
- [x] Unit tests for new Pydantic models (`ChartSettingsInput`, `VisualizationSettingsInput`, `CalculatedFieldInput`)
- [x] Unit tests for `QuerySpec.compare_time_offset_seconds` validation
- [x] Integration test cases for boards with chart_type, visualization settings, calculated fields, and compare offsets
- [x] Integration test cases for queries with calculated fields and compare offsets
- [x] CI passes (736 unit tests)

* we don't actually want those extra tool fields in our generators

## [0.5.0] - 2026-01-08

### Bug Fixes

- Majorly improve Claude tool schema validation 

### Features

- Add --remove-delete-protection for dataset deletes, and discovered a whole host of missing functionality around dataset updating and deletion we can rectify.

### Other

- Make all tools easier to reason about 

## [0.4.3] - 2026-01-07

### Bug Fixes

- Fix issue in service_map schema

## [0.4.2] - 2026-01-07

### Miscellaneous

- API file update and make it determinstic [SORRY FOR THE HORRORS] 

### Other

- Board views feature 

* feat: OpenAPI spec update process

Signed-off-by: Irving Popovetsky <irving@honeycomb.io>

* conflict resolution

Signed-off-by: Irving Popovetsky <irving@honeycomb.io>

* pull in api spec update with board views

Signed-off-by: Irving Popovetsky <irving@honeycomb.io>

* adding board view functionality

* add board views to claude tools and test thoroughly

* lintz

---------

Signed-off-by: Irving Popovetsky <irving@honeycomb.io>

## [0.4.1] - 2026-01-06

### Documentation

- Docsing

### Features

- Add dataset auto-detection for triggers and SLOs 

### Other

- Completely refactor that cli_auto_dataset test so it isn't flaky in real terminals

## [0.4.0] - 2026-01-01

### Features

- Add confidence and notes fields to the tool schema 

## [0.3.6] - 2026-01-01

### Bug Fixes

- Expose a trigger minimum time range

## [0.3.5] - 2026-01-01

### Bug Fixes

- SLI expression was missing from SLOBuilder description

## [0.3.4] - 2025-12-31

### Features

- Add columns to the CLI

## [0.3.3] - 2025-12-31

### Bug Fixes

- Improve derived column syntax info
- Cli query and board list shouldn't return Created At because apparently the API doesn't

## [0.3.2] - 2025-12-31

### Other

- Whoops forgot to update docs

## [0.3.1] - 2025-12-31

### Features

- Add api keys and environments to CLI and claude tools 

## [0.3.0] - 2025-12-30

### Features

- Auth resource 

### Other

- Refactor CI 

### Testing

- Test for unreachable code and fix 3 instances of it

## [0.2.1] - 2025-12-30

### Bug Fixes

- Fix CI hopefully

## [0.2.0] - 2025-12-30

### Other

- CLI version 1
- Query builder niceties
- Merge pull request #1 from irvingpop/phase12_cli

feat: CLI version 1

## [0.1.1] - 2025-12-29

### Bug Fixes

- Fix CI
- Fix tool eval test failures and docs
- Fixed issues in recipient resource and trigger executor
- Fix recipient mixin orchestration and get all live tool tests working
- Fix some transient tool eval test failures

### Build

- Builder refactor phases 1-2 checkpoint
- Builder refactor queries again

### Documentation

- Docs improvements
- Docs integration testing phase 2

### Other

- Initial version

Signed-off-by: Irving Popovetsky <irving@honeycomb.io>
- Phases 4 and 5 implemented
- Phase 6 complete
- Phase 7.1 complete plus a bunch of docs
- Deploy docs
- More CI
- Phase 7 complete
- Phase 8 (pagination) implemented
- Phase 8-post - working faux-pagination of query results
- Queries builder pattern is way nicer
- Integration+docs testing and massive docs cleanup phase 1
- SLO builder and fixing up some integration tests
- MarkerBuilder
- Board builder attempt 1
- Boardbuilder phase 5.5
- Make QueryBuilder consistent
- Board builder with SLO mixin
- Post refactor cleanups
- Phase 11 priority 1 resources implemented with unit and DeepEval tests
- Basic deepeval testing working
- Deepeval test architecture
- Cleanup
- Tools implemented datasets and columns
- Tools implemented derived_columns and recipients
- Tools implemented query
- Add parallelism and caching for deepeval tests
- Tools implemented board
- Tools implement events and markers
- Tools implementation is complete
- Ready for publishing to pypi
- Publishing workflow

<!-- generated by git-cliff -->
