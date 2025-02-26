# Ball Socket Motor Development Guide

## Build & Test Commands
- Run any script: `python script_name.py`
- Run tests: `pytest tests/`
- Run specific test: `pytest tests/test_file.py::test_function`
- Install dependencies: `uv pip install -r requirements.txt`

## Code Style Guidelines
- Language: Python 3.9+
- Naming: snake_case for functions/variables, PascalCase for classes
- Imports: group standard library, third-party, local imports with blank line separators
- Types: Use type hints for function parameters and return values
- Docstrings: Google style with Parameters/Returns sections
- Error handling: Use explicit exceptions with descriptive messages
- Line length: Aim for 88 characters or less
- Main guard: Use `if __name__ == "__main__":` for executable scripts

## Libraries
- Simulation: magpylib, scipy, numpy
- CAD/3D: cadquery, badcad, pyvista, trimesh
- Visualization: matplotlib
- Use existing patterns for magnetic field calculations