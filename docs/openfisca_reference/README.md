# OpenFisca Documentation — Vendored Knowledge Base

This folder contains a curated, version-pinned copy of the official
[OpenFisca documentation](https://github.com/openfisca/openfisca-doc), vendored
into this repository as a stable knowledge base for the DSPy pipeline and for
human contributors.

## Provenance

- **Upstream repository:** https://github.com/openfisca/openfisca-doc
- **Upstream commit:** `c019fab6d94e7116e784f95843dd35c20ff429a8`
- **Upstream commit date:** 2026-01-11
- **Fetched on:** 2026-04-26
- **License:** GNU Affero General Public License v3.0 (see `LICENSE` in this
  folder, copied verbatim from upstream)

## What is included

Four folders from `openfisca-doc/source/`:

| Folder | Purpose |
|---|---|
| [openfisca-python-api/](openfisca-python-api/) | Full Python API reference — variables, parameters, periods, entities, simulations, holders, reforms, tracer, test_runner. Maps directly to what this project's DSPy pipeline generates. |
| [coding-the-legislation/](coding-the-legislation/) | "How to model law as code" guide: basic example, input variables, vectorial computing, case disjunction, periods, legislation evolutions, entities, parameters, reforms, `writing_yaml_tests.md`, `bootstrapping_a_new_country_package.md`. |
| [key-concepts/](key-concepts/) | Short conceptual primers (variables, parameters, periods/instants, entities/roles, reforms, simulation, tax_and_benefit_system). Dense and ideal for LLM system-prompt grounding. |
| [simulate/](simulate/) | How to run, analyse, profile, and replicate simulations — relevant to validation against the test personas in `src/oll_law_as_code/runner.py`. |

## What is excluded and why

| Excluded | Reason |
|---|---|
| `source/_templates/`, `source/static/` | Sphinx infrastructure, not content. |
| `source/conf.py`, `source/summary.rst`, `source/index.md`, `source/manifest-history.md`, `source/license.md`, `source/architecture.md`, `source/find-help.md` | Sphinx wiring or upstream meta-docs; not useful as standalone references here. |
| `source/contribute/` | Guides for contributing to upstream openfisca-doc. |
| `source/installation/` | OpenFisca platform install — covered by our own `pyproject.toml`. |
| `source/openfisca-web-api/` | This project does not use the web API. |
| `source/training/` | Workshop slides, not reference material. |

## Caveats

- These are `.rst` and `.md` files written for Sphinx. Sphinx-specific
  cross-references (`:ref:`, `:doc:`) into excluded folders will not resolve
  in plain rendering — content stands alone as a knowledge base, but a Sphinx
  build would need either the full upstream tree or link rewriting.
- This is a frozen snapshot. The upstream docs evolve; refresh as described
  below when targeting a newer `openfisca-core` version.

## Refreshing this snapshot

```bash
TMPDIR=$(mktemp -d)
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/openfisca/openfisca-doc "$TMPDIR/openfisca-doc"
cd "$TMPDIR/openfisca-doc"
git sparse-checkout set \
  source/openfisca-python-api \
  source/coding-the-legislation \
  source/key-concepts \
  source/simulate

DEST=/path/to/oll_2026_law_as_code/docs/openfisca_reference
rm -rf "$DEST"/openfisca-python-api "$DEST"/coding-the-legislation \
       "$DEST"/key-concepts "$DEST"/simulate
cp -R source/openfisca-python-api source/coding-the-legislation \
      source/key-concepts source/simulate "$DEST/"
cp LICENSE "$DEST/LICENSE"

# Then update the "Upstream commit" / "Fetched on" lines above with:
git rev-parse HEAD
date +%F
```
