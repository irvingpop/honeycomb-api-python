# Phase 2.5: Enhanced TriggerBuilder + TagsMixin

## Overview

Add missing trigger features and create a reusable TagsMixin for Triggers, Boards, and SLOs.

## Missing Trigger Constraints

From API yaml analysis:

### 1. Frequency vs Duration Validation
- **Rule**: `duration <= frequency * 4`
- **API constraint**: Frequency cannot be more than 4 times the query's duration
- **Example**: If time_range is 1800 seconds (30 min), frequency must be >= 450 seconds

### 2. Duration Maximum
- **Rule**: Duration (time_range) cannot exceed 86400 seconds (1 day)
- **Note**: Triggers already have 3600 second (1 hour) limit, so this is already enforced

### 3. Exceeded Limit Range
- **Rule**: exceeded_limit must be between 1 and 5
- **API**: minimum: 1, maximum: 5

## New Features to Add

### 1. Tags Support

**Resources that support tags:**
- Triggers (confirmed)
- Boards (confirmed)
- SLOs (need to verify)

**Tag structure:**
```python
@dataclass
class Tag:
    key: str  # lowercase letters only, max 32 chars
    value: str  # start with lowercase letter, alphanumeric + / and -, max 128 chars
```

**TagsMixin design:**
```python
class TagsMixin:
    """Mixin providing tag management methods."""

    def __init__(self) -> None:
        self._tags: list[dict[str, str]] = []

    def tag(self, key: str, value: str) -> TagsMixin:
        """Add a tag to the resource.

        Args:
            key: Tag key (lowercase letters only, max 32 chars)
            value: Tag value (alphanumeric + / and -, max 128 chars)

        Returns:
            Self for method chaining.
        """
        # Validate key format
        if not key or len(key) > 32:
            raise ValueError("Tag key must be 1-32 characters")
        if not key.islower() or not key.replace('_', '').isalpha():
            raise ValueError("Tag key must be lowercase letters only")

        # Validate value format
        if not value or len(value) > 128:
            raise ValueError("Tag value must be 1-128 characters")
        if not value[0].islower():
            raise ValueError("Tag value must start with a lowercase letter")
        # Allow alphanumeric + / and -
        allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789/-')
        if not all(c in allowed_chars for c in value):
            raise ValueError("Tag value can only contain lowercase letters, numbers, / and -")

        self._tags.append({"key": key, "value": value})
        return self

    def tags(self, tags: dict[str, str]) -> TagsMixin:
        """Add multiple tags from a dictionary.

        Args:
            tags: Dictionary of key-value pairs

        Returns:
            Self for method chaining.
        """
        for key, value in tags.items():
            self.tag(key, value)
        return self

    def _get_all_tags(self) -> list[dict[str, str]] | None:
        """Get tags for API (None if empty)."""
        return self._tags if self._tags else None
```

### 2. Baseline Threshold Support

**Baseline Details structure:**
```python
@dataclass
class BaselineDetails:
    """Baseline threshold configuration for comparing against historical data."""
    offset_minutes: int  # 60, 1440, 10080, or 40320 (1 hour, 1 day, 7 days, 28 days)
    type: Literal["percentage", "value"]  # How to compare: (b-a)/b or b-a

class BaselineOffsetMinutes(int, Enum):
    """Allowed baseline offset values."""
    ONE_HOUR = 60
    ONE_DAY = 1440
    ONE_WEEK = 10080
    FOUR_WEEKS = 40320

class BaselineComparisonType(str, Enum):
    """Baseline comparison types."""
    PERCENTAGE = "percentage"
    VALUE = "value"
```

**TriggerBuilder baseline methods:**
```python
def baseline_percentage(
    self,
    offset: BaselineOffsetMinutes | int,
    threshold_percent: float
) -> TriggerBuilder:
    """Enable baseline comparison using percentage change.

    Args:
        offset: How far back to compare (60, 1440, 10080, or 40320 minutes)
        threshold_percent: Percentage change threshold

    Returns:
        Self for method chaining.
    """
    self._baseline_details = {
        "offset_minutes": offset,
        "type": "percentage"
    }
    # Baseline uses threshold differently - need to understand API better
    return self

def baseline_value(
    self,
    offset: BaselineOffsetMinutes | int,
    threshold_value: float
) -> TriggerBuilder:
    """Enable baseline comparison using absolute value change.

    Args:
        offset: How far back to compare (60, 1440, 10080, or 40320 minutes)
        threshold_value: Absolute value change threshold

    Returns:
        Self for method chaining.
    """
    self._baseline_details = {
        "offset_minutes": offset,
        "type": "value"
    }
    return self

def baseline_1_hour_ago(self, comparison_type: Literal["percentage", "value"] = "percentage") -> TriggerBuilder:
    """Compare against 1 hour ago (shortcut)."""
    self._baseline_details = {"offset_minutes": 60, "type": comparison_type}
    return self

def baseline_1_day_ago(self, comparison_type: Literal["percentage", "value"] = "percentage") -> TriggerBuilder:
    """Compare against 1 day ago (shortcut)."""
    self._baseline_details = {"offset_minutes": 1440, "type": comparison_type}
    return self

def baseline_1_week_ago(self, comparison_type: Literal["percentage", "value"] = "percentage") -> TriggerBuilder:
    """Compare against 1 week ago (shortcut)."""
    self._baseline_details = {"offset_minutes": 10080, "type": comparison_type}
    return self

def baseline_4_weeks_ago(self, comparison_type: Literal["percentage", "value"] = "percentage") -> TriggerBuilder:
    """Compare against 4 weeks ago (shortcut)."""
    self._baseline_details = {"offset_minutes": 40320, "type": comparison_type}
    return self
```

## Implementation Tasks

1. **Create TagsMixin** in `src/honeycomb/models/tags_mixin.py`
   - Tag validation
   - Single tag and bulk tags methods
   - Used by TriggerBuilder, BoardBuilder, SLOBuilder

2. **Update TriggerBuilder**
   - Add TagsMixin to inheritance
   - Add baseline threshold support
   - Add frequency vs duration validation in build()
   - Add exceeded_limit validation (1-5 range)

3. **Update Trigger Models**
   - Add baseline_details field to TriggerCreate
   - Add tags field to TriggerCreate
   - Update Trigger response model

4. **Tests**
   - TagsMixin validation tests
   - TriggerBuilder tags tests
   - TriggerBuilder baseline tests
   - Frequency vs duration validation tests
   - Exceeded limit range validation tests

5. **Documentation**
   - Add tags section to triggers.md
   - Add baseline triggers section to triggers.md
   - Document frequency vs duration constraint
   - Update reference tables

## File Changes

- New: `src/honeycomb/models/tags_mixin.py`
- Modified: `src/honeycomb/models/trigger_builder.py`
- Modified: `src/honeycomb/models/triggers.py`
- New: `tests/unit/test_tags_mixin.py`
- Modified: `tests/unit/test_trigger_builder.py`
- Modified: `docs/usage/triggers.md`
