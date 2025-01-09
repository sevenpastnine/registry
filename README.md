# Registry

Registry is a Django application that provides a registry of studies and all its resources.

## Development

Registry is a regular [django](https://www.djangoproject.com/) project written in [python](https://www.python.org/) that uses [pdm](https://pdm.fming.dev/) for dependency management.

For the StudyDesignMaps the project uses the [ReactFlow](https://reactflow.dev/) diagraming library together with the [Y.js](https://docs.yjs.dev/) for collaborative editing.

### Requirements

...

### Installation

For python and django:

1. Install the python dependencies with `pdm install`
2. Activate the virtual environment with `eval $(pdm venv activate)`

For JavaScript:

1. Install the frontend dependencies with `npm install`

### Configuration

...

### Running the project

In two separate shells run:

1. `python manage.py runserver`
2. `npm run start`

## TODO

- Verify if the user is a member of the current site for API endpoints
- Migrate registry management commands to admin (adding users in bulk)
- Add transactions to API endpoints
- Implement StudyDesign API endpoints
- Implement StudyDesignMap django views
