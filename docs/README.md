# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Environment Configuration

The frontend uses environment variables for configuration. Create a `.env` file in the `docs` directory based on `.env.example`:

```bash
cp .env.example .env
```

### Required Environment Variables

- `REACT_APP_API_URL`: Backend API URL (defaults to Hugging Face deployment: `https://junaidkh84-python-backend.hf.space`)

For local backend development, you can change this to:
```
REACT_APP_API_URL=http://localhost:8000
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
