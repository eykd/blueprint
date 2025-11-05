# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Blueprint is a procedural generation library for Python that implements a "magical blueprints" pattern for content generation. It uses metaclass-based prototypal inheritance to define templates (blueprints) with static and dynamic fields that are "mastered" (instantiated with concrete values) on demand.

**Key Concept**: Think of Blueprints as templates that generate concrete data objects. When you instantiate a Blueprint subclass, all dynamic fields are resolved to produce a "mastered" blueprint with final values.

## Core Architecture

The codebase follows a metaclass-driven design with these key components:

### 1. **Blueprint System** (`base.py`)
- `BlueprintMeta`: Metaclass that handles blueprint inheritance and tag repository setup
- `Blueprint`: Base class for all blueprints
  - Uses metaclass to auto-tag classes by name (CamelCase → separate tags)
  - Instantiation triggers field resolution to create "mastered" blueprints
  - Each direct Blueprint descendant gets its own `TagRepository`

### 2. **Field System** (`fields.py`)
- `Field`: Base class for dynamic fields (callables that resolve during blueprint instantiation)
- Operators: `Add`, `Subtract`, `Multiply`, `Divide`, `FloorDivide`
- Random fields: `RandomInt`, `Dice`, `DiceTable`
- Selection fields: `PickOne`, `PickFrom`, `All`, `WithTags`
- Template fields: `FormatTemplate`, `Property`
- Decorators: `generator`, `depends_on`, `defer_to_end`
- `resolve()`: Core field resolution function

### 3. **Tag System** (`taggables.py`)
- `TagRepository`: Stores and queries blueprints by tags
- `Taggable`: Base class for tagged objects
- `TagSet`: Collection of tags with query capabilities
- Tag inheritance: child blueprints inherit parent tags
- Automatic tagging from class names (e.g., `CaveMan` → `['cave', 'man']`)

### 4. **Mods** (`mods.py`)
- `Mod`: Special blueprint that modifies another blueprint
- Applied via `ModifiedBlueprint = Mod(BaseBlueprint)`
- Always produces mastered blueprints
- Common use: adding prefixes/suffixes, scaling values

### 5. **Factories** (`factories.py`)
- `Factory`: Blueprint factory that combines base blueprints with mods
- Selects blueprints and applies transformations
- Always produces mastered blueprints
- Common use: procedural item generation with randomized properties

### 6. **Additional Systems**
- `dice.py`: Dice rolling with expressions (e.g., "3d6+2")
- `markov.py`: Markov chain text generation
- `collection.py`: Blueprint collections and utilities

## Development Commands

### Testing
```bash
# Run pytest tests
uv run pytest

# Run a single test file
uv run pytest tests/test_specific.py

# Run doctests in source files
uv run python -m doctest src/blueprint/base.py
```

### Code Quality
```bash
# Run ruff linter
uv run ruff check .

# Run ruff formatter
uv run ruff format .

# Run type checker
uv run mypy src/

# Fix auto-fixable linting issues
uv run ruff check --fix .
```

### Development Workflow
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --group dev --group test
```

## Important Patterns & Conventions

### Field Resolution
- Fields are resolved during `Blueprint.__init__()` instantiation
- Static fields: plain values, used as-is
- Dynamic fields: callables taking `self` (the blueprint instance) as argument
- Deferred fields: marked with `@defer_to_end`, resolved after other fields
- Dependencies: use `@depends_on('field_name')` to declare resolution order

### Tag Queries
```python
# Query blueprints by tags
Weapon.tag_repo.query(with_tags=('piercing', 'sharp'))
Weapon.tag_repo.query(without_tags=('blunt',))

# Use in fields
weapon = blueprint.PickFrom(blueprint.WithTags('pointed weapon'))
```

### Generators vs Fields
- Use `@generator` decorator for methods that build final objects (not auto-called during mastering)
- Without `@generator`, methods are treated as fields and resolved during instantiation

### Metaclass Behavior
- Direct Blueprint subclasses create new `TagRepository` instances
- Indirect descendants share ancestor's repository
- `Meta.abstract = True` prevents blueprint from being added to tag repository

## Code Style Notes

- **Python version**: 3.11+
- **Type hints**: Adding type hints is encouraged (mypy strict mode enabled)
- **Formatting**: Ruff with single quotes for inline strings, double quotes for docstrings
- **Line length**: 120 characters
- **Imports**: Use ruff's isort integration (profile = "black")
- **Docstrings**: Google-style docstrings with examples (many modules have extensive doctests)

## Testing Strategy

- **pytest**: Configured but test directory not yet created (pytest.ini points to `tests/`)
