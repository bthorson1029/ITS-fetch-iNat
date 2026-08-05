# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-04

Initial public release.

### Added

- `fetch_barcodes.py`, a command-line tool that searches iNaturalist for all observations of a
  given taxon carrying the "DNA Barcode ITS" observation field and writes the sequences to a
  FASTA file.
- Server-side filtering on the observation field, so observations without a barcode are never
  paged through.
- Cursor-style pagination via `id_above`, with a 1-second delay between requests.
- Automatic taxon-name resolution for default output filenames
  (`barcodes_<taxon_id>_<binomial>.fasta`).
- Sequence cleaning to IUPAC nucleotide characters.
- `--taxon-id`, `--output`, `--field-id`, and `--field-name` options.
- Project documentation, MIT license, contribution guide, and GitHub Actions CI.

[Unreleased]: https://github.com/bthorson1029/ITS-fetch-iNat/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bthorson1029/ITS-fetch-iNat/releases/tag/v0.1.0
