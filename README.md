# <repo-name>

Create new repos from this template, then run `control-plane/scripts/bootstrap-repo.sh <owner/repo> [project-number]` to apply merge settings, the `baseline` property and the org `protect:main` ruleset. While this repo is marked as a template, its workflows skip every job. This template repo itself is deliberately **not** bootstrapped (`baseline=false`): its jobs are skipped, so the required checks never report and the org ruleset would block every PR here. Do not run the bootstrap script on it.
