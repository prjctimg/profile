# Profile

Reusable GitHub Actions workflows for keeping profile READMEs up to date.

## Usage

Call the workflow from your repo:

```yaml
jobs:
  update:
    uses: prjctimg/profile/.github/workflows/update.yml@main
    with:
      commit-message: "Update README"
      git-user-name: "your-username"
      git-user-email: "your-email"
    secrets: inherit
```

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `"3.11"` | Python version |
| `script-path` | string | `.github/scripts/update.py` | Path to update script |
| `script-output` | string | `"stdout"` | `stdout`: capture output; `direct`: script writes README |
| `readme-path` | string | `README.md` | README file path |
| `commit-message` | string | *(required)* | Commit message |
| `git-user-name` | string | *(required)* | Git user.name |
| `git-user-email` | string | *(required)* | Git user.email |
