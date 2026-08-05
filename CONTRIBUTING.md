# Contributing to ITS-fetch-iNat

Thanks for your interest. This is a small, single-file tool, so contributing is
straightforward.

## Getting set up

```bash
git clone https://github.com/bthorson1029/ITS-fetch-iNat.git
cd ITS-fetch-iNat
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`.

## Before opening a pull request

Run the same checks CI runs:

```bash
pip install ruff && ruff check .
```

```bash
python fetch_barcodes.py --help
```

Both must pass. Lint configuration lives in `ruff.toml`.

A note on formatting: **please do not run `ruff format` or `black` on the codebase.** The
script uses aligned assignment blocks that a formatter would collapse, producing a large diff
that buries the actual change. CI deliberately runs `ruff check` only.

## Reporting bugs

The single most useful bug report includes:

- The **taxon ID** you were fetching
- The **exact command** you ran
- Your **Python version** (`python --version`) and OS
- The **full console output**, including any traceback

Since the tool talks to a live public API, results can also change simply because the
underlying iNaturalist data changed — mentioning roughly when you ran it helps.

## A rule about data

**Never commit fetched sequence data to this repository.** The `iNat-barcodes/` directory is
gitignored on purpose:

- Sequences are contributed by individual iNaturalist users under their own licenses, which
  vary per observation and are not covered by this project's MIT license.
- FASTA headers embed each observation's free-text `place_guess`, which sometimes contains a
  precise address.

If you need to illustrate output in an issue, a PR, or the documentation, fabricate a short
example rather than pasting real records.

## Scope

This tool does one thing: pull ITS barcode sequences out of iNaturalist observations and write
FASTA. Changes that keep it small, dependency-light, and polite to the public API are the
easiest to merge. If you have an idea that would meaningfully expand the scope, open an issue
to discuss it before writing code.

## Code of Conduct

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
