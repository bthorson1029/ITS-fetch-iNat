# ITS-fetch-iNat

[![CI](https://github.com/bthorson1029/ITS-fetch-iNat/actions/workflows/ci.yml/badge.svg)](https://github.com/bthorson1029/ITS-fetch-iNat/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)

Fetch **DNA Barcode ITS** sequences from [iNaturalist](https://www.inaturalist.org)
observations and write them to a FASTA file.

Given a taxon ID, the script finds every iNaturalist observation of that taxon that has the
"DNA Barcode ITS" observation field filled in, cleans each sequence, and writes the whole set
to a single FASTA file ready for alignment, BLAST, or phylogenetic work.

## What is ITS?

The **internal transcribed spacer** (ITS) is the standard DNA barcode region for fungi. A
growing number of iNaturalist observers sequence their collections and record the result in
the community "DNA Barcode ITS" observation field (field ID `2330`). That data is public, but
there is no built-in way to export it in bulk — this tool does that.

## Requirements

- Python 3.7 or newer
- [`requests`](https://pypi.org/project/requests/)

## Installation

```bash
git clone https://github.com/bthorson1029/ITS-fetch-iNat.git
cd ITS-fetch-iNat
pip install -r requirements.txt
```

Using a virtual environment is recommended:

```bash
python -m venv .venv && source .venv/bin/activate
```

On Windows, activate with `.venv\Scripts\activate` instead.

## Usage

Find the numeric taxon ID in the iNaturalist taxon page URL — for
`inaturalist.org/taxa/1678285-Amanita-pallidorubescens`, the ID is `1678285`.

```bash
python fetch_barcodes.py --taxon-id 1678285
```

```bash
python fetch_barcodes.py --taxon-id 1678285 --output pallidorubescens.fasta
```

```bash
python fetch_barcodes.py --taxon-id 47219 --field-id 9999
```

Because a taxon ID matches everything beneath it, pointing the tool at a genus (or higher)
pulls barcodes for the whole clade in one pass.

### Options

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--taxon-id` | **yes** | — | iNaturalist numeric taxon ID, from the taxon page URL. |
| `--output` | no | `<binomial>_<taxon_id>.fasta` | Output FASTA filename. Only the filename is used; see the note below. |
| `--field-id` | no | `2330` | iNaturalist observation field ID for the barcode. |
| `--field-name` | no | `"DNA Barcode ITS"` | Observation field name, used as a fallback match and as the server-side filter. |

### Notes on behavior

- **Run it from the repository root.** The output directory `iNat-barcodes/` is resolved
  relative to your current working directory, not to the script's location.
- **`--output` takes a filename, not a path.** Anything you pass is reduced to its basename,
  so the file always lands inside `iNat-barcodes/`.
- **Existing files are overwritten** without prompting.
- The tool waits **1 second between paginated API requests** to stay polite to iNaturalist's
  free public API. Please leave that delay in place.
- No authentication is needed — the tool only reads public, unauthenticated endpoints.

## Output

Records are written to `iNat-barcodes/<filename>`, one header line followed by one sequence
line, with a blank line between records. Headers are built as
`>iNat<observation_id>_<binomial>_<place>`, with all whitespace collapsed to underscores:

```
>iNat123456789_Amanita_muscaria_Example_County,_State,_US
ACGTACGTACGTNNNNACGTACGTRYSWKMACGTACGTACGT

>iNat987654321_Amanita_sp._location_unknown
ACGTTTGCAACGTACGT-------ACGTACGTACGTACGTAC
```

Sequences are uppercased and stripped down to IUPAC nucleotide characters
(`A C G T U R Y S W K M B D H V N -`); anything else in the field value is discarded.
Observations whose barcode field is present but empty are skipped.

The `iNat-barcodes/` directory is intentionally listed in `.gitignore` — see below.

## Data, licensing, and etiquette

**The MIT license in this repository covers the code only.** It does not cover any data you
fetch with it.

Sequences and locality strings retrieved from iNaturalist are contributed by individual
observers, each of whom chooses their own license (CC0, CC-BY, CC-BY-NC, or all rights
reserved — it varies per observation). FASTA headers produced by this tool also embed each
observation's `place_guess` field verbatim, which is free text and occasionally contains a
precise address.

If you intend to redistribute, publish, or deposit fetched sequences, you are responsible for
checking the license and locality sensitivity of each source observation. Please credit the
original observers and iNaturalist. See the
[iNaturalist Terms of Service](https://www.inaturalist.org/pages/terms) and
[Community Guidelines](https://www.inaturalist.org/pages/community+guidelines).

For that reason, this repository ships **no fetched data** — the example output above is
fabricated. Run the tool yourself to generate your own.

## Contributing

Bug reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE) © bthorson1029
