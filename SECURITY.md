# Security Policy

## Supported version

Security fixes are applied to the default branch. The project does not currently maintain multiple release lines.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature for this repository. Include the affected endpoint or component, reproduction conditions, impact, and any suggested mitigation.

Do not open a public issue for a suspected vulnerability and do not include credentials, access tokens, private repository data, or personal information in a report.

## Deployment boundary

Public deployments must keep `WRITE_OPERATIONS_ENABLED=false` and must not configure `GITHUB_TOKEN`. Write operations are intended only for trusted local or private deployments. This project does not provide multi-user authentication or tenant isolation.
