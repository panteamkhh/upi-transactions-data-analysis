# Security Policy

## Supported versions

This is a portfolio/analysis project. Security fixes are applied to the latest
`main` branch and the most recent tagged release.

| Version | Supported |
|---------|-----------|
| 1.x     | ✅        |
| < 1.0   | ❌        |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Instead, use GitHub's private vulnerability reporting
(**Security → Report a vulnerability**) or email the maintainer at
`pantea.mkh18@gmail.com`. Include:

- a description of the issue and its impact,
- steps to reproduce,
- any suggested fix.

You can expect an acknowledgement within a few days.

## Scope notes

- The bundled dataset is **synthetic**; no real personal or financial data is
  stored in this repository.
- Do not commit credentials, API keys or tokens. `.gitignore` excludes common
  secret and environment files, but always double-check before pushing.
- The Streamlit dashboard and CLI read local files only; they do not make
  outbound network calls beyond fetching Python dependencies.
