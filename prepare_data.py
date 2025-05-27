"""Prepare the Apogee data for training by downloading and cleaning it.
This script downloads the Apogee catalog, applies quality cuts, and saves the cleaned data.
"""

from pathlib import Path

import requests
import numpy as np
from astropy.table import Table

# Ensure the output directory exists
output_dir = Path("data")
output_dir.mkdir(parents=True, exist_ok=True)

# Download Apogee Catalog
url = "https://data.sdss.org/sas/dr17/apogee/spectro/aspcap/dr17/synspec_rev1/allStarLite-dr17-synspec_rev1.fits"
output_path = output_dir / "allStarLite-dr17-synspec_rev1.fits"

response = requests.get(url, stream=True)
response.raise_for_status()

with open(output_path, "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
print(f"Downloaded APOGEE data file to {output_path}")

# Preprocess Apogee data to keep only good data points


apogee_cat = Table.read(output_path, hdu=1)

apogee_cat = apogee_cat[
    [
        "LOGG",
        "TEFF",
        "LOGG_ERR",
        "TEFF_ERR",
        "FE_H",
        "FE_H_ERR",
        "PARAMFLAG",
        "ASPCAPFLAG",
    ]
]

# Implement the quality cuts primarily based on Isabelle Laing's notebook
param_flags = apogee_cat["PARAMFLAG"]  # each row is an array len = 9
aspcap_flags = apogee_cat["ASPCAPFLAG"]  # each row is a single value

# Define bitmasks for ASPCAPFLAG
teff_bad_mask = 1 << 16  # TEFF_BAD
colorte_bad_mask = 1 << 25  # COLORTE_BAD
logg_bad_mask = 1 << 17  # LOGG_BAD
star_bad_mask = 1 << 23  # STAR_BAD
m_h_bad_mask = 1 << 19  # M_H_BAD


# Define bitmasks for PARAMFLAG
gridedge_bad_mask = 1 << 0  # GRIDEDGE_BAD
calrange_bad_mask = 1 << 1  # CALRANGE_BAD
other_bad_mask = 1 << 2  # OTHER_BAD
teff_cut_mask = 1 << 6  # TEFF_CUT

# Define index positions in PARAMFLAG array
logg_index = 1
teff_index = 0
metal_index = 3
carbon_index = 5
nitrogen_index = 6

teff_param_issues = (
    param_flags[:, teff_index]
    & (gridedge_bad_mask | calrange_bad_mask | other_bad_mask | teff_cut_mask)
) != 0
teff_aspcap_issues = (
    aspcap_flags & (teff_bad_mask | colorte_bad_mask | star_bad_mask)
) != 0
teff_issues = teff_param_issues | teff_aspcap_issues

# LOGG specific issues
logg_param_issues = (
    param_flags[:, logg_index]
    & (gridedge_bad_mask | calrange_bad_mask | other_bad_mask)
) != 0
logg_aspcap_issues = (aspcap_flags & (logg_bad_mask | star_bad_mask)) != 0
logg_issues = logg_param_issues | logg_aspcap_issues

# Metal specific issues
metal_param_issues = (
    param_flags[:, metal_index]
    & (gridedge_bad_mask | calrange_bad_mask | other_bad_mask)
) != 0
metal_aspcap_issues = (aspcap_flags & m_h_bad_mask) != 0
metal_issues = metal_param_issues | metal_aspcap_issues

feh_abnormal = (
    np.isnan(apogee_cat["FE_H"])
    | (apogee_cat["FE_H"] > 10)
    | (apogee_cat["FE_H"] == 0)
    | (apogee_cat["FE_H_ERR"] == 0)
    | np.isnan(apogee_cat["FE_H_ERR"])
)

# LOGG
logg_abnormal = (
    np.isnan(apogee_cat["LOGG"])
    | (apogee_cat["LOGG"] >= 6)
    | (apogee_cat["LOGG"] == 0)
    | (apogee_cat["LOGG_ERR"] == 0)
    | np.isnan(apogee_cat["LOGG_ERR"])
)

# TEFF
teff_abnormal = (
    np.isnan(apogee_cat["TEFF"])
    | (apogee_cat["TEFF"] > 10000)
    | (apogee_cat["TEFF"] == 0)
    | (apogee_cat["TEFF_ERR"] == 0)
    | np.isnan(apogee_cat["TEFF_ERR"])
)


apogee_cat = apogee_cat[
    (
        ~teff_issues
        & ~logg_issues
        & ~metal_issues
        & ~feh_abnormal
        & ~logg_abnormal
        & ~teff_abnormal
    )
]

apogee_cat.remove_columns(["PARAMFLAG", "ASPCAPFLAG"])
apogee_cat = apogee_cat.to_pandas()

# Use the "Good Label" cuts from Laroche and Speagle closing stellar label gap paper
good_labels = (apogee_cat["TEFF"] / apogee_cat["TEFF_ERR"]) > 30
good_labels &= apogee_cat["LOGG_ERR"] < 0.4
good_labels &= apogee_cat["FE_H_ERR"] < 0.2

apogee_cat = apogee_cat[good_labels]
# Save the cleaned data as parquet file
apogee_cat.to_parquet(output_dir / "apogee_cleaned.parquet", index=False)
print(f"Cleaned data saved to {output_dir / 'apogee_cleaned.parquet'}")
