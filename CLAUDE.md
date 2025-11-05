# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Blueprint is a procedural generation library for Python that implements a "magical blueprints" pattern for content generation. It uses metaclass-based prototypal inheritance to define templates (blueprints) with static and dynamic fields that are "mastered" (instantiated with concrete values) on demand.

**Key Concept**: Think of Blueprints as templates that generate concrete data objects. When you instantiate a Blueprint subclass, all dynamic fields are resolved to produce a "mastered" blueprint with final values.

### Quality Requirements
- All code is now fully type-annotated (mypy strict mode)
- Comprehensive linting rules enforced (ruff)
- 100% test coverage required

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

### Initial Setup
```bash
# Install dependencies (dev + test)
uv sync --group dev --group test

# Install pre-commit hooks
uv run pre-commit install
```

### Testing
```bash
# Run all checks (format, lint, type-check, test)
./runtests.sh

# Run pytest with coverage
uv run pytest

# Run tests with randomized order (validates test independence)
uv run pytest --random-order

# Run tests with 100% coverage requirement (CI mode)
uv run pytest --cov-fail-under=100

# Run a single test file
uv run pytest tests/test_base.py

# Run only fast tests (exclude slow tests)
uv run pytest -m "not slow"
```

### Code Quality
```bash
# Run ruff linter
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Run ruff formatter
uv run ruff format .

# Run type checker on source and tests
uv run mypy src tests

# Run pre-commit hooks manually (all files)
uv run pre-commit run --all-files
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

## Code Quality Standards

This codebase maintains **100% test coverage** and enforces strict quality standards through automated tooling:

### Python Version & Type Safety
- **Python version**: 3.11+ (Python 2.7 support dropped as of v0.7.0)
- **Type hints**: Fully typed with mypy strict mode enabled across all modules
- **Type checking**: `uv run mypy src tests` validates all code
- **py.typed marker**: Package includes type information for downstream consumers

### Code Formatting & Linting
- **Formatter**: Ruff with single quotes for inline strings, double quotes for docstrings
- **Line length**: 120 characters
- **Linter**: Comprehensive ruff configuration with 50+ rule groups enabled
- **Import sorting**: Ruff's isort integration (profile = "black")
- **Docstrings**: Google-style docstrings with executable examples

### Testing Infrastructure
- **Framework**: pytest with 100% coverage requirement (enforced in CI)
- **Test execution**:
  - `uv run pytest` - runs all tests with coverage
  - `./runtests.sh` - development test script with auto-formatting
  - `uv run pytest --random-order` - validates test independence
- **Test types**:
  - Unit tests in `tests/` directory (one test file per module)
  - Doctests embedded in all source modules
  - Hypothesis-based property testing where applicable
- **Coverage**: Branch coverage enabled, 100% required for CI to pass

### Continuous Integration
- **GitHub Actions**: Automated testing on Python 3.11, 3.12, and 3.13
- **Pre-commit hooks**: Auto-format, lint, type-check, and test before commit
- **Quality gates**: All checks must pass (tests, coverage, linting, type checking)

## Development Practices

When working on this codebase:

1. **Run tests before commits**: Use `./runtests.sh` to validate all changes locally
2. **Pre-commit hooks are mandatory**: They catch issues before they reach CI
3. **100% coverage is required**: All new code must include comprehensive tests
4. **Type annotations are required**: Add type hints for all functions, methods, and variables
5. **Docstrings with examples**: Include Google-style docstrings with doctests where applicable
6. **Test independence**: Tests must pass regardless of execution order (validated by pytest-random-order)

### Adding New Features

When adding new functionality:

1. Write tests first or alongside implementation (TDD approach)
2. Add type annotations from the start
3. Include doctests in docstrings for user-facing APIs
4. Ensure 100% coverage for your changes
5. Run the full test suite with `./runtests.sh` before committing

### Modifying Existing Code

When changing existing code:

1. Verify existing tests still pass
2. Update or add tests to cover your changes
3. Maintain 100% coverage (no regression)
4. Update docstrings and doctests if behavior changes
5. Run type checker to ensure no type safety regressions
