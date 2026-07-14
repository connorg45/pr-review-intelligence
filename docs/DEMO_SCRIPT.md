# Two-minute demo script

## 0:00 to 0:20: Problem and dashboard

“PR Review Intelligence helps engineering teams find risky pull requests and the right reviewers. The dashboard shows the current queue, risk distribution, review latency, and recent system activity.”

Show the five summary cards and the high-risk queue.

## 0:20 to 0:55: Risk factors

Open the highest-risk pull request. Point out:

- the numeric score and risk level
- the exact rule-based reasons
- changed files marked as sensitive or test files
- reviewer recommendations with repository-history evidence

“Each recommendation is tied to changed-file signals or prior repository activity, so an engineer can verify why it appeared.”

## 0:55 to 1:25: Trusted local GitHub sync

On a trusted local instance, open Settings. Enter a repository owner and name, then run sync. On public hosting, point out that these controls are deliberately disabled.

“The GitHub client handles pagination, timeouts, and token errors. The sync is idempotent, so unchanged pull requests do not create duplicate files or analysis results.”

Show the processed, updated, reanalyzed, and unchanged counters.

## 1:25 to 1:45: Reliability

Open Activity and show successful and failed sync records.

“Sync and analysis actions create an audit trail. Failed external calls are recorded, and the health endpoint verifies database connectivity for deployments.”

## 1:45 to 2:00: Engineering summary

“The application is a React and TypeScript frontend backed by Flask, SQLAlchemy, and PostgreSQL or SQLite. It has backend and frontend tests, GitHub Actions, a production Docker image, and a one-click deployment blueprint.”
