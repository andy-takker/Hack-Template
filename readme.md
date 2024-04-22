# Hack Template

Template project for web application which based on Python and React.

## Stack

### Python libs

- [Aiomisc](https://aiomisc.readthedocs.io/en/latest/) for DI and service organization
- [FastAPI](https://aiomisc.readthedocs.io/en/latest/) with uvicorn for REST backend with Swagger (can be replaced with aiohttp)
- [Aiogram Dialog](https://aiogram-dialog.readthedocs.io/en/latest/overview/index.html) for Telegram Bot
- [SqlAlchemy](https://www.sqlalchemy.org/) with [Alembic](https://alembic.sqlalchemy.org) for database
- [Poetry](https://python-poetry.org/) for requirements management and project config

### JS stack

- ...

## Deployment

- Github Actions
- Makefile
- Docker Compose

## To-Do List

- [ ] Add telegram bot service
- [ ] Add github actions: check project for linters and tests, bulding docker images
- [ ] Add python unit tests
- [ ] Add docker images for backend and frontend
- [ ] Add nginx conf and image