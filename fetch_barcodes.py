#!/usr/bin/env python3
"""
fetch_barcodes.py

Searches iNaturalist for all observations of a given taxon that have the
"DNA Barcode ITS" observation field filled, then writes each barcode sequence
to a FASTA file.

Usage:
    python fetch_barcodes.py --taxon-id 1678285
    python fetch_barcodes.py --taxon-id 1678285 --output my_barcodes.fasta
    python fetch_barcodes.py --taxon-id 1678285 --field-id 9999

Arguments:
    --taxon-id    (required) iNaturalist numeric taxon ID.
                  Find it in the taxon URL: inaturalist.org/taxa/<ID>
    --output      (optional) Output FASTA filename. Only the filename is used;
                  the file is always written inside the iNat-barcodes/ folder.
                  Defaults to: barcodes_<taxon_id>_<binomial>.fasta
    --field-id    (optional) iNaturalist observation field ID for the barcode.
                  Defaults to 2330 (DNA Barcode ITS).
    --field-name  (optional) Observation field name used as a fallback match.
                  Defaults to "DNA Barcode ITS".

Dependencies:
    pip install requests
"""

import argparse
import os
import re
import sys
import time
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL      = "https://api.inaturalist.org/v1"
PER_PAGE      = 200    # max allowed by iNat v1 API
REQUEST_DELAY = 1.0    # seconds between paginated requests

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch DNA Barcode ITS sequences from iNaturalist and write to FASTA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python fetch_barcodes.py --taxon-id 1678285\n"
            "  python fetch_barcodes.py --taxon-id 1678285 --output pallidorubescens.fasta\n"
            "  python fetch_barcodes.py --taxon-id 47219 --field-id 9999\n"
        ),
    )
    parser.add_argument(
        "--taxon-id",
        type=int,
        required=True,
        help="iNaturalist numeric taxon ID (found in the taxon page URL).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output FASTA filename (written inside iNat-barcodes/). "
             "Defaults to barcodes_<taxon_id>_<binomial>.fasta.",
    )
    parser.add_argument(
        "--field-id",
        type=int,
        default=2330,
        help="iNaturalist observation field ID for the barcode (default: 2330, "
             '"DNA Barcode ITS").',
    )
    parser.add_argument(
        "--field-name",
        type=str,
        default="DNA Barcode ITS",
        help='Observation field name used as fallback match (default: "DNA Barcode ITS").',
    )
    return parser.parse_args()

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def fetch_page(
    taxon_id: int,
    field_name: str,
    id_above: Optional[int] = None,
    page: int = 1,
) -> dict:
    """
    Fetch one page of observations for the given taxon, filtered server-side
    to only those that have the named observation field set (any value).
    Uses cursor-style pagination via id_above after the first page.
    """
    params = {
        "taxon_id": taxon_id,
        "per_page": PER_PAGE,
        "order_by": "id",
        "order":    "asc",
        # Empty value => "has this field with any value". This filters on the
        # server so we never page through observations that lack a barcode.
        f"field:{field_name}": "",
    }
    if id_above is not None:
        params["id_above"] = id_above
    else:
        params["page"] = page

    resp = requests.get(
        f"{BASE_URL}/observations",
        params=params,
        timeout=30,
        headers={"Accept": "application/json"},
    )
    resp.raise_for_status()
    return resp.json()


def fetch_taxon_name(taxon_id: int) -> Optional[str]:
    """
    Return the scientific name (binomial) for a taxon ID, or None if it
    cannot be resolved.
    """
    resp = requests.get(
        f"{BASE_URL}/taxa/{taxon_id}",
        timeout=30,
        headers={"Accept": "application/json"},
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if results:
        return (results[0].get("name") or "").strip() or None
    return None

# ---------------------------------------------------------------------------
# Sequence helpers
# ---------------------------------------------------------------------------

def extract_barcode(observation: dict, field_id: int, field_name: str) -> Optional[str]:
    """
    Return the barcode sequence from an observation's ofvs list,
    or None if the field is absent or empty.
    Matches by field ID first, then falls back to field name substring match.
    """
    for ofv in observation.get("ofvs", []):
        matched = (
            ofv.get("field_id") == field_id
            or field_name.lower() in (ofv.get("name") or "").lower()
        )
        if matched:
            value = (ofv.get("value") or "").strip()
            return value if value else None
    return None


def clean_sequence(seq: str) -> str:
    """
    Strip whitespace and non-IUPAC characters, then uppercase.
    Valid characters: A C G T U R Y S W K M B D H V N -
    """
    seq = re.sub(r"\s+", "", seq).upper()
    seq = re.sub(r"[^ACGTURYSWKMBDHVN\-]", "", seq)
    return seq


def get_binomial(obs: dict) -> str:
    """
    Return the scientific name (binomial) recorded on an observation,
    or "sp." if the taxon is missing.
    """
    taxon = obs.get("taxon") or {}
    return (taxon.get("name") or "").strip() or "sp."


def make_fasta_header(obs: dict) -> str:
    """
    Build a FASTA header with underscores between every word:
    >iNat<obs_id>_<binomial>_<place>
    """
    obs_id    = obs.get("id", "unknown")
    binomial  = get_binomial(obs)
    place     = obs.get("place_guess") or "location_unknown"
    title     = f"iNat{obs_id} {binomial} {place}"
    title     = re.sub(r"\s+", "_", title.strip())
    return f">{title}"


def sanitize_for_filename(name: str) -> str:
    """
    Make a string safe for use in a filename: collapse whitespace to
    underscores and drop characters that are awkward across filesystems.
    """
    name = re.sub(r"\s+", "_", name.strip())
    name = re.sub(r"[^A-Za-z0-9._-]", "", name)
    return name

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    taxon_id   = args.taxon_id
    field_id   = args.field_id
    field_name = args.field_name

    OUTPUT_DIR = "iNat-barcodes"

    # Resolve the taxon's binomial for filename/record keeping.
    print("Resolving taxon name ...", end=" ", flush=True)
    try:
        binomial = fetch_taxon_name(taxon_id)
    except requests.RequestException as exc:
        binomial = None
        print(f"could not resolve ({exc}).")
    else:
        print(binomial or "not found.")

    # Build the output path: <iNat-barcodes>/barcodes_<taxon_id>_<binomial>.fasta
    if args.output:
        filename = os.path.basename(args.output)
    else:
        suffix   = f"_{sanitize_for_filename(binomial)}" if binomial else ""
        filename = f"barcodes_{taxon_id}{suffix}.fasta"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output = os.path.join(OUTPUT_DIR, filename)

    print(f"Taxon ID:     {taxon_id}")
    print(f"Taxon name:   {binomial or 'unknown'}")
    print(f"Field:        {field_name!r} (ID {field_id})")
    print(f"Output file:  {output}\n")

    # ---- First page ----
    print("Fetching page 1 ...", end=" ", flush=True)
    data = fetch_page(taxon_id, field_name, page=1)

    total_results = data.get("total_results", 0)
    print(f"{total_results} observations with the {field_name!r} field.")

    if total_results == 0:
        print(
            f"\nNo observations with the {field_name!r} field. Suggestions:\n"
            "  - Confirm the taxon ID is correct at: "
            f"https://www.inaturalist.org/taxa/{taxon_id}\n"
            "  - Check the field name with --field-name (it must match the\n"
            "    iNaturalist observation field name exactly).\n"
            "  - The taxon may be inactive or merged."
        )
        sys.exit(0)

    all_observations = data.get("results", [])
    last_id = all_observations[-1]["id"] if all_observations else None

    # ---- Subsequent pages ----
    while len(all_observations) < total_results and last_id is not None:
        time.sleep(REQUEST_DELAY)
        fetched_so_far = len(all_observations)
        upper = min(fetched_so_far + PER_PAGE, total_results)
        print(
            f"Fetching observations {fetched_so_far + 1}-{upper} "
            f"(id_above={last_id}) ...",
            end=" ", flush=True,
        )
        data    = fetch_page(taxon_id, field_name, id_above=last_id)
        results = data.get("results", [])
        print(f"got {len(results)} records.")

        if not results:
            break

        all_observations.extend(results)
        last_id = results[-1]["id"]

    print(f"\nRetrieved {len(all_observations)} observations total.")

    # ---- Extract barcodes ----
    records = []
    for obs in all_observations:
        barcode = extract_barcode(obs, field_id, field_name)
        if barcode:
            seq = clean_sequence(barcode)
            if seq:
                records.append((obs, seq))

    print(f"Observations with a non-empty barcode: {len(records)}")

    if not records:
        print(
            "\nNo barcode sequences found. Possible causes:\n"
            "  - The field ID or name does not match. Try --field-id or --field-name.\n"
            "  - Observations have the field but the value is blank."
        )
        sys.exit(0)

    # ---- Write FASTA ----
    with open(output, "w", encoding="utf-8") as fh:
        for obs, seq in records:
            fh.write(make_fasta_header(obs) + "\n")
            fh.write(seq + "\n")
            fh.write("\n")

    print(f"\nWrote {len(records)} FASTA records to: {output}")
    print("Done.")


if __name__ == "__main__":
    main()
