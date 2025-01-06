# Registry

Registry is a Django application that provides a registry of studies and all its resources.

## Development

Registry is a regular [django](https://www.djangoproject.com/) project written in [python](https://www.python.org/) that uses [pdm](https://pdm.fming.dev/) for dependency management.

For the interactive and collaborative editing of the the StudyDesignMaps the project uses the [ReactFlow](https://reactflow.dev/) diagraming library and [Hocuspocus](https://tiptap.dev/docs/hocuspocus/introduction) collaborative server based on [Y.js](https://docs.yjs.dev/).

### Requirements

...

### Installation

For python and django:

1. Install the python dependencies with `pdm install`
2. Activate the virtual environment with `eval $(pdm venv activate)`

For JavaScript:

1. Install the frontend dependencies with `npm install`
2. Install the Hocuspocus server dependencies with `npm --prefix hocuspocus install`

### Configuration

...

### Running the project

In two separate shells run:

1. `python manage.py runserver`
2. `npm run start`

## TODO

- Migrate registry management commands to admin

- Implement StudyDesign API endpoints
- Implement StudyDesignMap django views
- Add transactions on API endpoints
