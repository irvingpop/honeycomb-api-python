# Builder Refactor Plan

## Overview

This document outlines the comprehensive builder system for the Honeycomb Python client. The design prioritizes:

1. **No duplicated capabilities** - Shared functionality lives in one place
2. **Clean composition** - Builders compose smaller pieces rather than duplicate
3. **Constraint enforcement** - Builders enforce API constraints at build time
4. **Flexibility** - Support both simple and advanced use cases
5. **Fluent integration** - Builders can be composed inline for single-call workflows

---

## Implementation Status

### ✅ Completed Phases

**Test Status:** 481 unit tests + 46 integration tests passing (100%)

#### Phase 1: RecipientMixin + RecipientBuilder
- **RecipientMixin** - Shared recipient methods for triggers/burn alerts
- **RecipientBuilder** - Factory for standalone recipient creation
- Methods: `.email()`, `.slack()`, `.pagerduty()`, `.webhook()`, `.msteams()`, `.recipient_id()`

#### Phase 2: TriggerBuilder
- **TriggerBuilder** - Extends QueryBuilder + RecipientMixin
- Enforces trigger constraints (single calc, time_range ≤ 3600s, no absolute time)
- Threshold shortcuts: `.threshold_gt/gte/lt/lte()`
- Frequency presets: `.every_minute/5_minutes/15_minutes/30_minutes/hour()`
- Dataset scoping: `.dataset()` or `.environment_wide()`

#### Phase 2.5: Enhanced TriggerBuilder
- **TagsMixin** - Shared tag methods (max 10 tags, format validation)
- Baseline threshold support
- Frequency vs duration validation
- Enhanced unit tests

#### Phase 3: SLOBuilder + BurnAlertBuilder
- **BurnAlertBuilder** - Extends RecipientMixin, supports EXHAUSTION_TIME and BUDGET_RATE
- **SLOBuilder** - Creates SLOs with integrated burn alerts and derived columns
- **SLOBundle** - Orchestration data structure
- **client.slos.create_from_bundle_async()** - Automatic derived column + SLO + burn alert creation
- Target helpers: `.target_percentage()`, `.target_nines()`, `.target_per_million()`
- SLI configuration: `.sli(alias)` for existing or `.sli(alias, expression, description)` for new

#### Phase 4: MarkerBuilder
- **MarkerBuilder** - Point and duration markers
- Time helpers: `.duration_minutes()`, `.duration_hours()`, `.start_time()`, `.end_time()`
- Static helper: `MarkerBuilder.setting(type, color)`

#### Phase 5: BoardBuilder (Basic)
- **BoardCreate** - Enhanced with panels, layout_generation, tags, preset_filters
- **BoardBuilder** - Creates boards with query/SLO/text panels
- **QueryAnnotationsResource** - Full CRUD wrapper for query annotations
- Panel types: query, SLO, text
- Layout modes: auto, manual

#### Phase 5.5: Enhanced BoardBuilder with QueryBuilder Integration ✅

**Goal:** Single fluent call for board creation with inline QueryBuilder instances, no separate query creation needed.

**Status:** Complete - All tests passing (481 unit + 46 integration)

#### Phase 6: SLOBuilder Integration into BoardBuilder ✅

**Goal:** Allow inline SLOBuilder instances in BoardBuilder, matching QueryBuilder pattern.

**Status:** Complete - All tests passing (481 unit + 46 integration)

---

## Phase 5.5: Enhanced BoardBuilder Design

### Problem

Current board creation requires too much ceremony:
```python
# TOO MUCH CEREMONY
from honeycomb import QueryBuilder

q1 = QueryBuilder().last_1_hour().count().annotate("Requests")
query1, annot1 = await client.queries.create_with_annotation_async("dataset", q1)

q2 = QueryBuilder().last_1_hour().avg("duration_ms").annotate("Latency")
query2, annot2 = await client.queries.create_with_annotation_async("dataset", q2)

board = BoardBuilder("Dashboard").query(query1.id, annot1).query(query2.id, annot2).build()
await client.boards.create_async(board)
```

### Solution

Single fluent call with inline QueryBuilder:
```python
# SINGLE FLUENT CALL
board = await client.boards.create_from_bundle_async(
    BoardBuilder("Dashboard")
        .auto_layout()
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_1_hour()
                .count()
                .group_by("service")
                .name("Request Count")
        )
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_1_hour()
                .avg("duration_ms")
                .name("Latency"),
            style="table"
        )
        .build()
)
```

---

## QueryBuilder Enhancements (Phase 5.5a)

### Add Dataset Scoping

```python
class QueryBuilder:
    def dataset(self, dataset_slug: str) -> QueryBuilder:
        """Set dataset scope for this query."""
        self._dataset = dataset_slug
        return self

    def environment_wide(self) -> QueryBuilder:
        """Mark query as environment-wide (all datasets)."""
        self._dataset = "__all__"
        return self

    def get_dataset(self) -> str:
        """Get dataset scope (defaults to "__all__" if not set)."""
        return self._dataset if self._dataset else "__all__"
```

### Replace .annotate() with .name() and .description()

**Remove:**
```python
.annotate(name, description)  # DELETE THIS - no dead code
```

**Add:**
```python
def name(self, name: str) -> QueryBuilder:
    """Set query name (required for board integration).

    For boards: This becomes the query annotation name.
    Outside boards: Optional, useful for documentation.
    """
    self._query_name = name
    return self

def description(self, desc: str) -> QueryBuilder:
    """Set query description (optional).

    For boards: This becomes the query annotation description.
    """
    self._query_description = desc
    return self

def has_name(self) -> bool:
    """Check if query has name set."""
    return self._query_name is not None

def get_name(self) -> str | None:
    """Get query name."""
    return self._query_name

def get_description(self) -> str | None:
    """Get query description."""
    return self._query_description
```

**Rationale:**
- `.name()` is required for boards, `.description()` is optional
- Outside of boards, neither is required
- More explicit and clear than `.annotate()` which conflates two concerns

---

## BoardBundle Data Structures (Phase 5.5b)

```python
@dataclass
class QueryBuilderPanel:
    """Query panel from inline QueryBuilder (needs creation)."""
    builder: QueryBuilder
    position: tuple[int, int, int, int] | None  # (x, y, width, height)
    style: Literal["graph", "table", "combo"]
    visualization: dict[str, Any] | None
    dataset_override: str | None

@dataclass
class ExistingQueryPanel:
    """Query panel from existing query ID."""
    query_id: str
    annotation_id: str
    position: tuple[int, int, int, int] | None
    style: Literal["graph", "table", "combo"]
    visualization: dict[str, Any] | None
    dataset: str | None

@dataclass
class SLOPanel:
    """SLO panel."""
    slo_id: str
    position: tuple[int, int, int, int] | None

@dataclass
class TextPanel:
    """Text panel."""
    content: str
    position: tuple[int, int, int, int] | None

@dataclass
class BoardBundle:
    """Board creation bundle for orchestration.

    Returned by BoardBuilder.build(), consumed by boards.create_from_bundle_async().
    """
    board_name: str
    board_description: str | None
    layout_generation: Literal["auto", "manual"]
    tags: list[dict[str, str]] | None
    preset_filters: list[dict[str, str]] | None
    # Panels (in order added)
    query_builder_panels: list[QueryBuilderPanel]
    existing_query_panels: list[ExistingQueryPanel]
    slo_panels: list[SLOPanel]
    text_panels: list[TextPanel]
```

---

## Updated BoardBuilder API (Phase 5.5c)

### New Storage Structure

```python
class BoardBuilder(TagsMixin):
    def __init__(self, name: str):
        TagsMixin.__init__(self)
        self._name = name
        self._description: str | None = None
        self._layout_generation: Literal["auto", "manual"] = "manual"
        self._preset_filters: list[dict[str, str]] = []
        # Panel storage (in order added)
        self._query_builder_panels: list[QueryBuilderPanel] = []
        self._existing_query_panels: list[ExistingQueryPanel] = []
        self._slo_panels: list[SLOPanel] = []
        self._text_panels: list[TextPanel] = []
```

### Updated .query() Method

```python
def query(
    self,
    query: QueryBuilder | str,
    annotation_id: str | None = None,
    *,
    position: tuple[int, int, int, int] | None = None,  # (x, y, width, height)
    style: Literal["graph", "table", "combo"] = "graph",
    visualization: dict[str, Any] | None = None,
    dataset: str | None = None,
) -> BoardBuilder:
    """Add a query panel.

    Args:
        query: QueryBuilder with .name() OR existing query_id string
        annotation_id: Required only if query is string
        position: (x, y, width, height) for manual layout
        style: graph | table | combo
        visualization: {"hide_markers": True, "utc_xaxis": True, ...}
        dataset: Override QueryBuilder's dataset

    Example - Inline QueryBuilder:
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_24_hours()
                .count()
                .group_by("service")
                .name("Request Count")
                .description("Requests by service over 24h"),
            position=(0, 0, 9, 6),
            style="graph",
            visualization={"hide_markers": True, "utc_xaxis": True}
        )

    Example - Existing query:
        .query("query-id-123", "annotation-id-456", style="table")
    """
    if isinstance(query, QueryBuilder):
        if not query.has_name():
            raise ValueError("QueryBuilder must have .name() set for board panels")

        self._query_builder_panels.append(QueryBuilderPanel(
            builder=query,
            position=position,
            style=style,
            visualization=visualization,
            dataset_override=dataset,
        ))
    else:
        if not annotation_id:
            raise ValueError("annotation_id required when using existing query ID")

        self._existing_query_panels.append(ExistingQueryPanel(
            query_id=query,
            annotation_id=annotation_id,
            position=position,
            style=style,
            visualization=visualization,
            dataset=dataset,
        ))
    return self
```

### Updated .slo() and .text() Methods

```python
def slo(
    self,
    slo_id: str,
    *,
    position: tuple[int, int, int, int] | None = None,
) -> BoardBuilder:
    """Add an SLO panel.

    Args:
        slo_id: ID of the SLO
        position: (x, y, width, height) for manual layout
    """
    self._slo_panels.append(SLOPanel(slo_id=slo_id, position=position))
    return self

def text(
    self,
    content: str,
    *,
    position: tuple[int, int, int, int] | None = None,
) -> BoardBuilder:
    """Add a text panel (supports markdown, max 10000 chars).

    Args:
        content: Markdown text content
        position: (x, y, width, height) for manual layout
    """
    if len(content) > 10000:
        raise ValueError(f"Text content must be <= 10000 characters, got {len(content)}")
    self._text_panels.append(TextPanel(content=content, position=position))
    return self
```

### Updated .build() Method

```python
def build(self) -> BoardBundle:
    """Build BoardBundle for orchestration.

    Returns:
        BoardBundle (not BoardCreate) for client orchestration
    """
    # Validate manual layout requires all positions
    if self._layout_generation == "manual":
        all_panels = (
            self._query_builder_panels +
            self._existing_query_panels +
            self._slo_panels +
            self._text_panels
        )
        for i, panel in enumerate(all_panels):
            if panel.position is None:
                raise ValueError(
                    f"Manual layout requires position for all panels. "
                    f"Panel {i} missing position. Use position=(x, y, width, height)"
                )

    return BoardBundle(
        board_name=self._name,
        board_description=self._description,
        layout_generation=self._layout_generation,
        tags=self._get_all_tags(),
        preset_filters=self._preset_filters if self._preset_filters else None,
        query_builder_panels=self._query_builder_panels,
        existing_query_panels=self._existing_query_panels,
        slo_panels=self._slo_panels,
        text_panels=self._text_panels,
    )
```

---

## Client Orchestration (Phase 5.5d)

### boards.create_from_bundle_async()

```python
class BoardsResource:
    async def create_from_bundle_async(self, bundle: BoardBundle) -> Board:
        """Create board from BoardBundle with automatic query creation.

        Orchestrates:
        1. Create queries + annotations from QueryBuilder instances
        2. Assemble all panel configurations
        3. Create board with all panels

        Panels are added to the board in the order they appear in the bundle:
        - Auto-layout: Honeycomb arranges panels in this order
        - Manual-layout: Respects explicit positions

        Args:
            bundle: BoardBundle from BoardBuilder.build()

        Returns:
            Created Board object
        """
        panels = []

        # Create query panels from QueryBuilder instances
        for qb_panel in bundle.query_builder_panels:
            dataset = qb_panel.dataset_override or qb_panel.builder.get_dataset()
            query, annotation_id = await self._client.queries.create_with_annotation_async(
                dataset, qb_panel.builder
            )
            panels.append(self._build_query_panel_dict(
                query.id, annotation_id, qb_panel.position,
                qb_panel.style, qb_panel.visualization, dataset
            ))

        # Add existing query panels
        for existing in bundle.existing_query_panels:
            panels.append(self._build_query_panel_dict(
                existing.query_id, existing.annotation_id, existing.position,
                existing.style, existing.visualization, existing.dataset
            ))

        # Add SLO panels
        for slo in bundle.slo_panels:
            panels.append(self._build_slo_panel_dict(slo.slo_id, slo.position))

        # Add text panels
        for text in bundle.text_panels:
            panels.append(self._build_text_panel_dict(text.content, text.position))

        # Create board
        board_create = BoardCreate(
            name=bundle.board_name,
            description=bundle.board_description,
            type="flexible",
            panels=panels if panels else None,
            layout_generation=bundle.layout_generation,
            tags=bundle.tags,
            preset_filters=bundle.preset_filters,
        )

        return await self.create_async(board_create)

    def _build_query_panel_dict(
        self,
        query_id: str,
        annotation_id: str,
        position: tuple[int, int, int, int] | None,
        style: str,
        visualization: dict[str, Any] | None,
        dataset: str | None,
    ) -> dict[str, Any]:
        """Build query panel dictionary for API."""
        panel = {
            "type": "query",
            "query_panel": {
                "query_id": query_id,
                "query_annotation_id": annotation_id,
                "query_style": style,
            }
        }
        if dataset and dataset != "__all__":
            panel["query_panel"]["dataset"] = dataset
        if visualization:
            panel["query_panel"]["visualization_settings"] = visualization
        if position:
            panel["position"] = {
                "x_coordinate": position[0],
                "y_coordinate": position[1],
                "width": position[2],
                "height": position[3],
            }
        return panel

    def _build_slo_panel_dict(
        self,
        slo_id: str,
        position: tuple[int, int, int, int] | None,
    ) -> dict[str, Any]:
        """Build SLO panel dictionary for API."""
        panel = {
            "type": "slo",
            "slo_panel": {"slo_id": slo_id}
        }
        if position:
            panel["position"] = {
                "x_coordinate": position[0],
                "y_coordinate": position[1],
                "width": position[2],
                "height": position[3],
            }
        return panel

    def _build_text_panel_dict(
        self,
        content: str,
        position: tuple[int, int, int, int] | None,
    ) -> dict[str, Any]:
        """Build text panel dictionary for API."""
        panel = {
            "type": "text",
            "text_panel": {"content": content}
        }
        if position:
            panel["position"] = {
                "x_coordinate": position[0],
                "y_coordinate": position[1],
                "width": position[2],
                "height": position[3],
            }
        return panel
```

---

## Panel Layout Behavior

### Manual Layout
- **Single unified section** - queries, SLOs, and text panels can be mixed in any position
- User explicitly sets `position=(x, y, width, height)` for every panel
- No automatic sectioning or offsetting
- Full control over placement
- **All panel types are equal** - no special SLO section

### Auto Layout
- **Panels arranged in order added** to the builder
- Order matters: panels flow in the sequence of `.query()`, `.slo()`, `.text()` calls
- No positions needed - Honeycomb calculates layout
- **All panel types are equal** - arranged in a single flow

### Examples

**Manual layout mixing all types:**
```python
BoardBuilder("Dashboard")
    .manual_layout()
    .slo("slo-1", position=(0, 0, 4, 6))      # Top left
    .query(qb1, position=(4, 0, 8, 6))        # Top right
    .text("Notes", position=(0, 6, 6, 4))     # Bottom left
    .query(qb2, position=(6, 6, 6, 4))        # Bottom right
    # All types mixed together - no sections
```

**Auto layout respects order:**
```python
BoardBuilder("Dashboard")
    .auto_layout()
    .query(qb1)    # Appears first
    .query(qb2)    # Appears second
    .slo("slo-1")  # Appears third
    .text("Notes") # Appears fourth
    # Honeycomb arranges in this exact order
```

---

## Usage Examples

### Simple Auto-Layout Board

```python
board = await client.boards.create_from_bundle_async(
    BoardBuilder("Service Dashboard")
        .description("Request metrics and latency tracking")
        .auto_layout()
        .tag("team", "platform")
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_24_hours()
                .count()
                .group_by("service")
                .name("Request Count"),
            style="graph"
        )
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_1_hour()
                .avg("duration_ms")
                .group_by("endpoint")
                .limit(10)
                .name("Avg Latency"),
            style="table"
        )
        .build()
)
```

### Complex Manual-Layout Board

```python
board = await client.boards.create_from_bundle_async(
    BoardBuilder("Production Dashboard")
        .description("Complete service health monitoring")
        .manual_layout()
        .tag("team", "platform")
        .tag("environment", "production")
        .preset_filter("service", "Service")
        .preset_filter("environment", "Environment")
        # Top left - large graph with visualization settings
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_24_hours()
                .count()
                .group_by("service")
                .name("Request Count")
                .description("Total requests by service over 24h"),
            position=(0, 0, 9, 6),
            style="graph",
            visualization={"hide_markers": True, "utc_xaxis": True}
        )
        # Top right - SLO panel
        .slo("slo-id-123", position=(9, 0, 3, 6))
        # Middle left - table view
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_1_hour()
                .avg("duration_ms")
                .group_by("endpoint")
                .limit(10)
                .name("Latency"),
            position=(0, 6, 6, 5),
            style="table"
        )
        # Middle right - combo view
        .query(
            QueryBuilder()
                .dataset("api-logs")
                .last_2_hours()
                .count()
                .gte("status_code", 400)
                .group_by("status_code")
                .name("Errors"),
            position=(6, 6, 6, 5),
            style="combo"
        )
        # Bottom - text panel (full width)
        .text(
            "## Monitoring Guidelines\n\n- Watch for latency > 500ms\n- Error rate should stay < 1%",
            position=(0, 11, 12, 3)
        )
        .build()
)
```

### Using Existing Queries

```python
board = await client.boards.create_from_bundle_async(
    BoardBuilder("Dashboard")
        .auto_layout()
        .query("existing-query-id", "existing-annotation-id", style="graph")
        .query("another-query-id", "another-annotation-id", style="table")
        .build()
)
```

---

## Implementation Checklist

### Phase 5.5a: Enhance QueryBuilder
- [x] Add `name` parameter to `__init__()` (optional, defaults to None)
- [x] Add `.dataset(dataset_slug)`, `.environment_wide()`, `.get_dataset()`
- [x] Add `self._query_name`, `self._query_description` to `__init__()`
- [x] Remove `.annotate()` method (replaced with name in constructor)
- [x] Keep `.description(desc)`, `.has_name()`, `.get_name()`, `.get_description()`
- [x] Update `create_with_annotation_async()` to use `.get_name()` and `.get_description()`
- [x] All unit tests passing (481 tests)

### Phase 5.5b: BoardBundle Structures
- [x] Create `QueryBuilderPanel` dataclass in `board_builder.py`
- [x] Create `ExistingQueryPanel` dataclass in `board_builder.py`
- [x] Create `SLOPanel` dataclass (with tuple position)
- [x] Create `TextPanel` dataclass (with tuple position)
- [x] Create `BoardBundle` dataclass in `board_builder.py`
- [x] Add all to `models/__init__.py` exports
- [x] Add all to `__init__.py` exports

### Phase 5.5c: Update BoardBuilder
- [x] Update `__init__()` to use typed panel lists
- [x] Update `.query()` to accept `QueryBuilder | str`
- [x] Update `.slo()` to use tuple position
- [x] Update `.text()` to use tuple position
- [x] Update `.build()` to return `BoardBundle` instead of `BoardCreate`
- [x] Remove old `BoardPanel`, `BoardQueryPanel`, `BoardSLOPanel`, `BoardTextPanel` classes
- [x] Remove `BoardPanelPosition`, `BoardPanelType` from public API
- [x] Update manual layout validation for all panel types

### Phase 5.5d: Client Orchestration
- [x] Implement `boards.create_from_bundle_async(bundle: BoardBundle)` in `boards.py`
- [x] Implement `boards.create_from_bundle(bundle: BoardBundle)` (sync wrapper)
- [x] Add `_build_query_panel_dict()` helper method
- [x] Add `_build_slo_panel_dict()` helper method
- [x] Add `_build_text_panel_dict()` helper method
- [x] Keep existing `boards.create_async(BoardCreate)` for non-builder usage

### Phase 5.5e: Update Examples
- [x] Update `docs/examples/boards/builder_board.py` simple example
- [x] Update `docs/examples/boards/builder_board.py` complex example
- [x] Move imports inside functions for copy-paste compatibility
- [x] Update `docs/usage/boards.md` to explain new pattern
- [x] Update `docs/usage/queries.md` to clarify when names are needed
- [x] Show dataset-scoped vs environment-wide query patterns

### Phase 5.5f: Update Tests
- [x] QueryBuilder unit tests passing with new constructor
- [x] Update BoardBuilder unit tests for tuple positions
- [x] Update BoardBuilder unit tests for QueryBuilder acceptance
- [x] Update integration tests to use `create_from_bundle_async()`
- [x] Test visualization dict configurations
- [x] Test both QueryBuilder and existing query ID patterns
- [x] All integration tests passing against live API (46 tests)

---

## Breaking Changes (Phase 5.5)

All implemented (library not yet shipped):

1. **QueryBuilder constructor**: Added optional `name` parameter - `QueryBuilder("Query Name")`
2. **QueryBuilder.annotate()**: Removed - use name in constructor + `.description()`
3. **BoardBuilder.build() return type**: `BoardCreate` → `BoardBundle`
4. **Board creation method**: `boards.create_from_bundle_async(builder.build())`
5. **Position type**: `BoardPanelPosition(...)` → `position=(0, 0, 9, 6)` tuples
6. **Panel parameter**: `visualization_settings` → `visualization`
7. **Removed classes**: `BoardPanel`, `BoardPanelPosition`, `BoardPanelType`, `BoardQueryPanel`, `BoardSLOPanel`, `BoardTextPanel`
8. **Dataset in panels**: Never included (query knows its scope)

---

## Phase 6: SLOBuilder Integration into BoardBuilder

**Goal:** Allow inline SLOBuilder instances in BoardBuilder, matching QueryBuilder pattern.

### Current Limitation

```python
# Must pre-create SLO and reference by ID
slo = await client.slos.create_from_bundle_async(
    SLOBuilder("API Availability")
        .dataset("api-logs")
        .target_nines(3)
        .sli(alias="success_rate")
        .build()
)

board = await client.boards.create_from_bundle_async(
    BoardBuilder("Dashboard")
        .slo(slo.id, position=(9, 0, 3, 6))  # Must use ID
        .build()
)
```

### Target API

Single fluent call with inline SLOBuilder:

```python
board = await client.boards.create_from_bundle_async(
    BoardBuilder("Dashboard")
        .auto_layout()
        .query(
            QueryBuilder("Requests")
                .dataset("api-logs")
                .last_1_hour()
                .count()
        )
        .slo(
            SLOBuilder("API Availability")
                .dataset("api-logs")
                .target_nines(3)
                .sli(alias="success_rate"),
            position=(9, 0, 3, 6)
        )
        .build()
)
```

### Implementation Plan

#### Phase 6a: SLOBuilder Panel Support

Update BoardBuilder to accept SLOBuilder instances:

```python
@dataclass
class SLOBuilderPanel:
    """SLO panel from inline SLOBuilder (needs creation)."""
    builder: SLOBuilder
    position: tuple[int, int, int, int] | None


@dataclass
class ExistingSLOPanel:
    """SLO panel from existing SLO ID."""
    slo_id: str
    position: tuple[int, int, int, int] | None
```

Rename current `SLOPanel` → `ExistingSLOPanel`, add `SLOBuilderPanel`.

#### Phase 6b: BoardBuilder Updates

```python
class BoardBuilder:
    def __init__(self, name: str):
        ...
        self._slo_builder_panels: list[SLOBuilderPanel] = []
        self._existing_slo_panels: list[ExistingSLOPanel] = []

    def slo(
        self,
        slo: SLOBuilder | str,
        *,
        position: tuple[int, int, int, int] | None = None,
    ) -> BoardBuilder:
        """Add an SLO panel.

        Args:
            slo: SLOBuilder instance OR existing SLO ID string
            position: (x, y, width, height) for manual layout

        Example - Inline SLOBuilder:
            .slo(
                SLOBuilder("Availability")
                    .dataset("api-logs")
                    .target_nines(3)
                    .sli(alias="success_rate"),
                position=(9, 0, 3, 6)
            )

        Example - Existing SLO:
            .slo("slo-id-123", position=(9, 0, 3, 6))
        """
        if isinstance(slo, SLOBuilder):
            self._slo_builder_panels.append(
                SLOBuilderPanel(builder=slo, position=position)
            )
        else:
            self._existing_slo_panels.append(
                ExistingSLOPanel(slo_id=slo, position=position)
            )
        return self
```

#### Phase 6c: BoardBundle Updates

```python
@dataclass
class BoardBundle:
    ...
    # Panels (in order added)
    query_builder_panels: list[QueryBuilderPanel]
    existing_query_panels: list[ExistingQueryPanel]
    slo_builder_panels: list[SLOBuilderPanel]      # NEW
    existing_slo_panels: list[ExistingSLOPanel]    # RENAMED from slo_panels
    text_panels: list[TextPanel]
```

#### Phase 6d: Orchestration

```python
class BoardsResource:
    async def create_from_bundle_async(self, bundle: BoardBundle) -> Board:
        panels = []

        # Create queries from QueryBuilder instances
        for qb_panel in bundle.query_builder_panels:
            ...

        # Create SLOs from SLOBuilder instances (NEW)
        for slo_panel in bundle.slo_builder_panels:
            # Create SLO using existing orchestration
            slo = await self._client.slos.create_from_bundle_async(slo_panel.builder.build())
            panels.append(self._build_slo_panel_dict(slo.id, slo_panel.position))

        # Add existing SLO panels
        for existing in bundle.existing_slo_panels:
            panels.append(self._build_slo_panel_dict(existing.slo_id, existing.position))

        ...
```

### Considerations

**Pros:**
- Consistent with QueryBuilder integration
- True single-call board creation
- No need to pre-create SLOs

**Cons:**
- SLO creation is slower than query creation (involves derived column creation)
- Creates resources even if board creation fails (need cleanup strategy)
- More complex error handling

**Decision Points:**
1. Should we support inline DerivedColumnBuilder too? (probably not - SLIs can be aliases)
2. Cleanup strategy if board creation fails after SLO creation?
3. Should inline SLOs support burn alerts? (probably yes, via SLOBuilder)

### Phase 6 Implementation Checklist ✅

#### Phase 6a: SLO Panel Data Structures
- [x] Create `SLOBuilderPanel` dataclass
- [x] Create `ExistingSLOPanel` dataclass (renamed from `SLOPanel`)
- [x] Update exports in `models/__init__.py`
- [x] Update exports in `__init__.py`

#### Phase 6b: BoardBuilder SLO Support
- [x] Update `__init__()` with `_slo_builder_panels` and `_existing_slo_panels` lists
- [x] Update `.slo()` to accept `SLOBuilder | str`
- [x] Update `.build()` to include both SLO panel types in BoardBundle
- [x] Update manual layout validation for SLO builder panels

#### Phase 6c: BoardBundle Updates
- [x] Add `slo_builder_panels: list[SLOBuilderPanel]` field
- [x] Rename `slo_panels` → `existing_slo_panels`
- [x] Update BoardBundle dataclass

#### Phase 6d: Orchestration
- [x] Update `boards.create_from_bundle_async()` to create SLOs from builders
- [x] Handle dict return from `slos.create_from_bundle_async()` (extract first SLO)
- [x] Maintain panel ordering (builders + existing)

#### Phase 6e: Examples & Documentation
- [x] Add example with inline SLOBuilder to `builder_board.py`
- [x] Complex example demonstrates inline SLO with derived column creation

#### Phase 6f: Tests
- [x] Updated unit tests for new SLO panel types (`existing_slo_panels`)
- [x] Integration test passing with inline SLO creation
- [x] All tests passing (481 unit + 46 integration)

---

### Phase 7: Final Cleanup ✅
- [x] Update README.md with builder examples
- [x] Add "Fluent Builders for Everything" section showcasing all builders
- [x] Comprehensive examples for QueryBuilder, TriggerBuilder, SLOBuilder, BoardBuilder
- [x] All 481 unit tests + 46 integration tests passing

---

## Phase 8: Query API Consistency ✅

**Goal:** Make QueryBuilder dataset handling consistent with BoardBuilder pattern while supporting advanced QuerySpec usage.

**Status:** Complete - Implemented with keyword-only dataset parameter and type overloads

**Test Status:** All 481 unit tests + 46 integration tests passing (100%)

### Solution: Keyword-Only Dataset with Overloads

```python
# Type overloads for perfect IDE autocomplete
@overload
async def create_async(self, spec: QueryBuilder) -> Query: ...

@overload
async def create_async(self, spec: QuerySpec, *, dataset: str) -> Query: ...

# Implementation supports both
async def create_async(
    self,
    spec: QuerySpec | QueryBuilder,
    *,
    dataset: str | None = None
) -> Query:
    if isinstance(spec, QueryBuilder):
        if dataset is not None:
            raise ValueError("dataset parameter not allowed with QueryBuilder")
        dataset = spec.get_dataset()
        query_spec = spec.build()
    else:
        if dataset is None:
            raise ValueError("dataset parameter required for QuerySpec")
        query_spec = spec
```

### Usage Patterns

```python
# QueryBuilder (recommended) - dataset on builder
await client.queries.create_async(
    QueryBuilder().dataset("my-dataset").count()
)

# QueryBuilder with .build() (for compatibility)
await client.queries.create_async(
    QueryBuilder().dataset("my-dataset").count().build(),
    dataset="my-dataset"  # Required when passing QuerySpec
)

# QuerySpec (advanced use cases)
await client.queries.create_async(
    QuerySpec(time_range=3600, calculations=[{"op": "COUNT"}]),
    dataset="my-dataset"
)

# Methods without builders still keep dataset parameter
await client.queries.get_async("my-dataset", "query-id")
await client.query_results.run_async("my-dataset", query_id="...")
```

### Implementation Checklist ✅

#### Phase 8a: Update Query Resource Methods
- [x] Add type overloads to `queries.create_async()`
- [x] Add keyword-only `dataset` parameter
- [x] Extract dataset from `builder.get_dataset()`
- [x] Validate parameter usage (errors for misuse)
- [x] Keep `run_async(dataset, ...)` unchanged (uses query_id)
- [x] Keep `get_async(dataset, query_id)` unchanged

#### Phase 8b: Update QueryResultsResource
- [x] Add type overloads to `create_and_run_async()`
- [x] Add keyword-only `dataset` parameter
- [x] Extract dataset from builder or validate QuerySpec has it
- [x] Update `run_all_async()` internal call to pass `dataset=dataset`
- [x] Keep `run_async(dataset, ...)` unchanged
- [x] Keep `create_async(dataset, ...)` unchanged (query result creation)

#### Phase 8c: Update All Examples
- [x] Update `docs/examples/queries/basic_query.py`
- [x] Update `docs/usage/queries.md`
- [x] Update `docs/getting-started/quickstart.md`
- [x] Update `docs/index.md`
- [x] Update README.md query examples

#### Phase 8d: Update All Tests
- [x] Update unit tests for queries resource
- [x] Fix remaining 7 test failures (add `dataset` parameter to QuerySpec calls)
- [x] Update integration tests - all 46 passing

### Breaking Changes
**NONE!** This is purely additive:
- QueryBuilder code works unchanged
- QuerySpec now requires `dataset=` keyword (NEW pattern, not a change)
- Non-builder methods (`get`, `run`) unchanged

### Benefits
- **Consistency:** Dataset on builder when using QueryBuilder
- **Flexibility:** Advanced users can still use QuerySpec directly
- **Type Safety:** Overloads provide perfect IDE autocomplete
- **Clear Errors:** Helpful validation messages guide correct usage

---

## Key Design Principles

### Builder Pattern Purity
- `.build()` returns data structures, never makes API calls
- Client orchestration methods handle API calls
- Consistent pattern: Builder → Bundle → `create_from_bundle_async()`

### Composition Over Duplication
- RecipientMixin shared by TriggerBuilder and BurnAlertBuilder
- TagsMixin shared by TriggerBuilder and BoardBuilder
- QueryBuilder embedded in BoardBuilder (no imports needed)

### Ergonomic APIs
- Single fluent call for complex operations
- Sensible defaults (environment-wide dataset, auto-layout, graph style)
- Support both simple and advanced use cases
- Clear method names (`.name()` not `.annotate()`)

### Validation at Build Time
- Triggers: single calc, time_range ≤ 3600s, no absolute time
- SLOs: require dataset, target, SLI
- Boards (manual): all panels need positions
- Boards (QueryBuilder): requires `.name()` for annotation

---

## File Structure

```
src/honeycomb/models/
├── query_builder.py          # QueryBuilder with .dataset(), .name(), .description()
├── query_annotations.py      # QueryAnnotation, QueryAnnotationCreate
├── trigger_builder.py        # TriggerBuilder (extends QueryBuilder + RecipientMixin)
├── recipient_builder.py      # RecipientBuilder + RecipientMixin
├── slo_builder.py            # SLOBuilder, BurnAlertBuilder, SLOBundle
├── marker_builder.py         # MarkerBuilder
├── board_builder.py          # BoardBuilder, BoardBundle, panel dataclasses
├── tags_mixin.py             # TagsMixin
└── __init__.py               # Export all builders

src/honeycomb/resources/
├── queries.py                # create_with_annotation_async()
├── query_annotations.py      # QueryAnnotationsResource (full CRUD)
├── boards.py                 # create_from_bundle_async()
├── slos.py                   # create_from_bundle_async()
└── ...
```

---

## Test Coverage

### Unit Tests: 481 passing
- QueryBuilder: 110+ tests
- SLOBuilder + BurnAlertBuilder: 44 tests
- MarkerBuilder: 11 tests
- BoardBuilder: 26 tests
- RecipientBuilder, DerivedColumnBuilder, etc.

### Integration Tests: 46 passing (100%)
- All documentation examples tested against live API
- Full CRUD lifecycles for all resources
- Builder patterns validated end-to-end

---

## Documentation Standards

### Progressive Complexity Examples
- **Simple** - 5-10 lines, minimal config, single feature
- **Moderate** - 15-20 lines, realistic usage, 2-3 features
- **Complex** - 25-35 lines, full feature showcase

### All Examples Must Be Integration Tested
Examples live in `docs/examples/*.py`, tests in `tests/integration/test_doc_examples.py`.

### Use Reference Tables
Tables for method listings, not code dumps showing every option.

### Include "Advanced Usage" Sections
Show non-builder alternatives for fine-grained control.
