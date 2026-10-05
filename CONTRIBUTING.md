# Contributing

Thanks for your interest in Pixelsonly Racing's Moza dashboards. Bug reports, dashboard
ideas and code are all welcome. Everyone taking part is expected to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help

- **Report a bug.** Use the [bug report form](https://github.com/pixelsonly/moza-downloads/issues/new?template=bug_report.yml).
  The details that matter most are your wheel model, how you load the dashboard (SimHub + AZOM or
  Pit House), the sim you're playing, and a photo or screenshot of the screen.
- **Request a dashboard**, or a change to one, with the
  [dashboard request form](https://github.com/pixelsonly/moza-downloads/issues/new?template=dashboard_request.yml).
- **Test on hardware.** Issues labelled `needs-hardware-test` need someone with the right wheel
  to try a build and report back.
- **Contribute code.** Look for `good first issue` and `help wanted`. For anything larger,
  open an issue first so we can agree on the approach.

Problems with the AZOM plugin itself (connecting, uploading, telemetry channels) belong in
[AZOM's issue tracker](https://github.com/giantorth/AZOM/issues).

## Development setup

You need Python 3.9+ (standard library only) and Node.js, which the tests use to evaluate the
dashboards' JavaScript bindings.

```sh
scripts/check.sh            # all tests, then build and package every dashboard (what CI runs)
scripts/check.sh ksp01      # the same for one dashboard
python3 dashboards/ksp01/build.py
```

Output goes to `dist/`, which is gitignored. Never commit generated `.mzdash` or `.zip` files;
CI builds them from source for each release.

The repo layout and the steps for adding a dashboard are in the [README](README.md#building-from-source).

## Pull requests

- **Branch from `main`.** Keep each PR to one change.
- **Title.** PRs are squash-merged, so the PR title becomes the commit that
  [release-please](https://github.com/googleapis/release-please) reads. It must follow
  [Conventional Commits](https://www.conventionalcommits.org/):

  | Change | Title |
  |---|---|
  | Dashboard behaviour or layout | `feat(ksp01): add fuel readout` |
  | Dashboard bug | `fix(ksp01): correct delta colour when ahead` |
  | Generator or tooling bug | `fix: handle empty driver name` |
  | Docs | `docs: clarify Pit House import` |
  | CI or housekeeping (no release) | `ci: …`, `chore: …`, `refactor: …`, `test: …` |

  Use the dashboard id as the scope when a change affects a dashboard. Add `!` (`feat(ksp01)!: …`)
  or a `BREAKING CHANGE:` line in the PR body for breaking changes.
- **Releases.** Only commits that touch `dashboards/<id>/` release that dashboard. If a change
  to `generator/` (or to a design another dashboard imports) alters a dashboard's output, that
  dashboard's `OUTPUT_SHA256` test fails; updating the hash in the same PR is what releases it.
- **Checks.** CI must pass (`ci-success` and `pr-title / lint`). Run `scripts/check.sh` locally first.
- **Layout changes.** Update the dashboard's `previews/` and say in the PR whether you tested it
  on hardware.

## Licensing of contributions

By contributing, you agree that your contributions are licensed under the same terms as the
files you change:

- code outside `dashboards/` under the [GNU GPL v3.0](LICENSE)
- everything under `dashboards/` under [CC BY-NC-SA 4.0](dashboards/LICENSE)

Don't submit work you don't have the right to license this way, such as images or designs
copied from other dashboards or from Moza's own.

## Maintainer notes

Labels are defined in [`.github/labels.json`](.github/labels.json). To create or update them:

```sh
jq -c '.[]' .github/labels.json | while read -r l; do
  gh label create "$(jq -r .name <<<"$l")" --color "$(jq -r .color <<<"$l")" \
    --description "$(jq -r .description <<<"$l")" --force
done
```

When adding a dashboard, also add a `dashboard: <id>` label and the new dashboard to the
`Dashboard` options in the bug report and dashboard request forms.
