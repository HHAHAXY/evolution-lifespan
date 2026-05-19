"""Download and merge AnAge life-history traits with the Zoonomia species list.

Outputs a single table keyed on species with columns:
    species, t_max_years, t_dev_days, body_mass_g, zoonomia_assembly
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

ANAGE_URL = "https://genomics.senescence.info/species/dataset.zip"
ANAGE_MEMBER = "anage_data.txt"
ANAGE_LOCAL = RAW_DIR / "anage_data.txt"

# Zoonomia 240-mammal species table. Replace if you have a preferred mirror.
ZOONOMIA_URL = (
    "https://raw.githubusercontent.com/broadinstitute/CGLR/main/data/zoonomia_species.tsv"
)
ZOONOMIA_LOCAL = RAW_DIR / "zoonomia_species.tsv"


# --------------------------------------------------------------------------- #
# AnAge
# --------------------------------------------------------------------------- #
def download_anage(force: bool = False) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if ANAGE_LOCAL.exists() and not force:
        return ANAGE_LOCAL
    print(f"[anage] downloading {ANAGE_URL}")
    r = requests.get(ANAGE_URL, timeout=60)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        # The archive contains anage_data.txt at the root.
        member = next(n for n in zf.namelist() if n.endswith(ANAGE_MEMBER))
        with zf.open(member) as src, open(ANAGE_LOCAL, "wb") as dst:
            dst.write(src.read())
    return ANAGE_LOCAL


def parse_anage(path: Path | None = None) -> pd.DataFrame:
    path = path or download_anage()
    df = pd.read_csv(path, sep="\t")
    df["species"] = (df["Genus"].str.strip() + "_" + df["Species"].str.strip())
    out = pd.DataFrame({
        "species": df["species"],
        "t_max_years": pd.to_numeric(df["Maximum longevity (yrs)"], errors="coerce"),
        # AnAge gives gestation/incubation in days — a good proxy for developmental time.
        "t_dev_days": pd.to_numeric(
            df.get("Gestation/Incubation (days)"), errors="coerce"
        ),
        "body_mass_g": pd.to_numeric(df["Adult weight (g)"], errors="coerce"),
    })
    return out.dropna(subset=["species"]).drop_duplicates("species")


# --------------------------------------------------------------------------- #
# Zoonomia
# --------------------------------------------------------------------------- #
def download_zoonomia(force: bool = False) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if ZOONOMIA_LOCAL.exists() and not force:
        return ZOONOMIA_LOCAL
    print(f"[zoonomia] downloading {ZOONOMIA_URL}")
    r = requests.get(ZOONOMIA_URL, timeout=60)
    r.raise_for_status()
    ZOONOMIA_LOCAL.write_bytes(r.content)
    return ZOONOMIA_LOCAL


def parse_zoonomia(path: Path | None = None) -> pd.DataFrame:
    """Return one row per species present in the Zoonomia alignment.

    Expected columns include a scientific name and an assembly identifier.
    Adjust the column names if your local copy uses a different schema.
    """
    path = path or download_zoonomia()
    df = pd.read_csv(path, sep="\t")
    # Heuristic column resolution — Zoonomia tables vary across releases.
    name_col = next(
        c for c in df.columns
        if c.lower() in {"species", "scientific_name", "scientificname"}
    )
    asm_col = next(
        (c for c in df.columns if "assembly" in c.lower() or "accession" in c.lower()),
        None,
    )
    out = pd.DataFrame({
        "species": df[name_col].str.strip().str.replace(" ", "_"),
        "zoonomia_assembly": df[asm_col] if asm_col else pd.NA,
    })
    return out.dropna(subset=["species"]).drop_duplicates("species")


# --------------------------------------------------------------------------- #
# Merge
# --------------------------------------------------------------------------- #
def build_dataset() -> pd.DataFrame:
    anage = parse_anage()
    zoo = parse_zoonomia()
    merged = zoo.merge(anage, on="species", how="inner")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "lifespan_traits.tsv"
    merged.to_csv(out_path, sep="\t", index=False)
    print(
        f"[merge] {len(merged)} species with AnAge + Zoonomia coverage "
        f"-> {out_path}"
    )
    return merged


if __name__ == "__main__":
    build_dataset()
