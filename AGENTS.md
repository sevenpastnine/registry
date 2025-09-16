# AGENTS Guidelines for This Repository

### Key Technologies
- **Django 5**: Web framework
- **HTMX** and **django-htmx**: Dynamic interactions without complex JavaScript
- **TailwindCSS 4.x**: Styling framework
- **TypeScript** and **React**: Frontend development
- **React XY Flow**: Diagrams and flowcharts in React
- **Yjs**: Real-time collaboration
- **Vite** and **django-vite**: Frontend build tool and asset management

## Development commands
- Install JavaScript dependencies: `npm install` and `npm install <package>`
- Install Python dependencies: `pdm install` and `pdm add <package>`
- Activate python virtual environment: `source .venv/bin/activate`
- JavaScript development server (Vite): `npm start`
- Django development server: `./manage.py runserver`

## Code Style and Rules

### Python
- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Use the `typing` module for type annotations (e.g., `List[str]`, `Dict[str, int]`).
- Break down complex functions into smaller, more manageable functions.
- Prefer functional style over imperative style where possible.
- Prefer functional style over objective-oriented style where possible.
- Prefer immutable data structures where possible (e.g., use tuples instead of lists for fixed collections).
- Prefer list comprehensions and generator expressions for creating lists and iterators.
- Avoid using global variables; pass parameters explicitly to functions.
- Use f-strings for string formatting (Python 3.6+).
- Handle errors with specific exception types
- Respect existing patterns in related files when adding new code
- Use two blank lines to separate functions, classes.

### TypeScript/React
- TypeScript with strict mode and linting rules enabled
- React with functional components and hooks
- Type all props and state
- Use React XY Flow for diagrams/charts
- Import order: React core → third-party → local modules
- Avoid unused variables and parameters
