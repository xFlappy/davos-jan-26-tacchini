# Setup Instructions

This guide shows how to set up your local environment for the Volue Energy Market Intelligence project.

## 1. Environment Variables Setup

Create a `.env` file in the **root** of the repository to store your API credentials and configuration.

```text
# .env (example) — fill with real values
VOLUE_CLIENT_ID=your-client-id-here
VOLUE_CLIENT_SECRET=your-client-secret-here

# Optional helpers
OPENAI_API_KEY=your-openai-key
DEFAULT_REGION=CH
START_DATE=2026-01-01
END_DATE=2026-01-31
```

Remember to add the `.env` file in `.gitignore`

## 2. Conda Environment Setup

- move to the **root** of the repository
- create the conda env from the environment.yml `conda env create -f environment.yml`

- activate the new env `conda activate hackathon-energy`

- if env already exists and you changed the file
`conda env update -f environment.yml --prune`