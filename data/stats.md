# Dataset stats

Generated: 2026-02-25T04:45:33

Source: `dataset.csv`

## Overview

| total_rows | unique_patients | visible_fracture_rows | not_visible_fracture_rows | ao_blank_or_null_rows |
| --- | --- | --- | --- | --- |
| 20327 | 6091 | 13550 | 0 | 6169 |

## Laterality distribution

| laterality | n |
| --- | --- |
| L | 11135 |
| R | 9192 |

## Projection distribution

| projection | n |
| --- | --- |
| 2 | 10148 |
| 1 | 10086 |
| 3 | 93 |

## AO/OTA distribution (top 30, NULL includes blank)

| ao_classification | n |
| --- | --- |
| NULL | 6169 |
| 23r-M/2.1 | 3221 |
| 23r-M/3.1; 23u-M/2.1 | 1691 |
| 23r-M/3.1; 23u-E/7 | 1537 |
| 23r-M/3.1 | 1501 |
| 23-M/3.1 | 1436 |
| 23-M/2.1 | 1377 |
| 23r-E/2.1; 23u-E/7 | 630 |
| 23r-E/2.1 | 539 |
| 23r-M/2.1; 23u-E/7 | 316 |
| 23r-M/3.1; 23u-M/2.1; 23u-E/7 | 252 |
| 23-M/3.1; 23u-E/7 | 219 |
| 23r-E/2.1; 23u-M/2.1 | 193 |
| 22r-D/2.1 | 90 |
| 23r-E/1 | 86 |
| 22-D/2.1 | 84 |
| 22r-D/2.1; 23u-M/2.1 | 68 |
| 23r-M/3.1; 23u-E/2.1 | 54 |
| 72B(b) | 42 |
| 23u-E/7 | 40 |
| 72B(c) | 38 |
| 23u-M/2.1 | 38 |
| 23r-M/3.1; 23u-E/1 | 34 |
| 23-M/2.1; 23u-E/7 | 31 |
| 22-D/4.1 | 31 |
| 23r-M/2.1; 23u-M/3.1 | 30 |
| 23r-E/2.1; 23u-M/2.1; 23u-E/7 | 30 |
| 22u-D/2.1 | 25 |
| 23r-E/7 | 20 |
| 23r-E/1; 23u-E/7 | 20 |

## Laterality x Projection

| laterality | projection | n |
| --- | --- | --- |
| L | 2 | 5574 |
| L | 1 | 5514 |
| L | 3 | 47 |
| R | 2 | 4574 |
| R | 1 | 4572 |
| R | 3 | 46 |

## Fracture visibility x Projection

| projection | fracture_visible | n |
| --- | --- | --- |
| 1 |  | 3533 |
| 1 | 1.0 | 6553 |
| 2 |  | 3224 |
| 2 | 1.0 | 6924 |
| 3 |  | 20 |
| 3 | 1.0 | 73 |

## Distinct projections per patient

| distinct_projections | patient_count |
| --- | --- |
| 1 | 128 |
| 2 | 5912 |
| 3 | 51 |

## Fracture count per row (derived from AO/OTA ';' separators)

Encoding rule: NULL/blank = 0 fractures, 0 ';' = 1, 1 ';' = 2, 2 ';' = 3, 3 ';' = 4.

| fracture_count_per_row | n |
| --- | --- |
| 0 | 6169 |
| 1 | 8689 |
| 2 | 5103 |
| 3 | 364 |
| 4 | 2 |

## AO/OTA distribution per fracture (splitting combined labels on ';')

Combined AO/OTA labels like `A; B` are split and counted independently (A and B each contribute 1).

| ao_classification | n |
| --- | --- |
| 23r-M/3.1 | 5174 |
| 23r-M/2.1 | 3637 |
| 23u-E/7 | 3209 |
| 23u-M/2.1 | 2333 |
| 23-M/3.1 | 1669 |
| 23r-E/2.1 | 1430 |
| 23-M/2.1 | 1412 |
| 22r-D/2.1 | 162 |
| 23r-E/1 | 106 |
| 22-D/2.1 | 88 |
| 22r-D/4.1 | 83 |
| 23u-M/3.1 | 78 |
| 23u-E/2.1 | 78 |
| 23u-E/1 | 66 |
| 22u-D/2.1 | 62 |
| 72B(b) | 52 |
| 72B(c) | 38 |
| 22-D/4.1 | 31 |
| 23-E/2.1 | 30 |
| 22u-D/1.1 | 26 |
| 23r-E/7 | 24 |
| 22u-D/4.1 | 24 |
| 23u-E/3 | 22 |
| 23r-E/3 | 18 |
| 22r-D/5.1 | 14 |
| 72B.(b) | 10 |
| 23u-E/1.1 | 10 |
| 22r-D/1.1 | 10 |
| 22-D/1.1 | 10 |
| 23r-E/4.1 | 9 |
| 23u-E7 | 8 |
| 23r-E/4.2 | 8 |
| 23r-E/2.2 | 6 |
| 22r-D/1 | 6 |
| 23u-M/2. | 5 |
| 23u-E/4 | 5 |
| 77.5.1A | 4 |
| 23u/E/7 | 4 |
| 23r-M3.1 | 4 |
| 23r-D/2.1 | 4 |
| 22r-D/3.1 | 4 |
| 77.1.1A | 3 |
| 23r-E/2.1, 23u-E/7 | 3 |
| 77.4.1A | 2 |
| 77.3.1C | 2 |
| 77.2.1A | 2 |
| 76.2.A | 2 |
| 23u-D/2.1 | 2 |
| 23-E/7 | 2 |
| 23-E/1 | 2 |

## Patient projection coverage (projections 1 & 2 only; projection 3 ignored)

Patient-level counts for whether a patient has projection 1, projection 2, or both. `patients_with_other_proj` flags patients who have any projection outside {1,2} (e.g., 3) and would be affected by removal.

| proj_pair_category | patient_count | patients_with_other_proj |
| --- | --- | --- |
| has_1_and_2 | 5931 | 51 |
| only_1 | 48 | 26 |
| only_2 | 112 | 6 |

### Projection 1 & 2 XOR summary

XOR means the patient has exactly one of {1,2}. `patients_with_1_and_2` means both.

| patients_with_1_xor_2 | patients_with_1_and_2 | total_patients |
| --- | --- | --- |
| 160 | 5931 | 6091 |

## Projection x fracture visibility (projections 1 & 2 only)

Counts and within-projection percentages of `fracture_visible` for projections 1 and 2.

| projection | fracture_visible | n | projection_total | pct_within_projection |
| --- | --- | --- | --- | --- |
| 1 |  | 3533 | 10086 | 0.35028752726551654 |
| 1 | 1.0 | 6553 | 10086 | 0.6497124727344834 |
| 2 |  | 3224 | 10148 | 0.31769806858494287 |
| 2 | 1.0 | 6924 | 10148 | 0.6823019314150571 |

## Fracture count x fracture visibility

Derived fracture count per row (0..4) crossed with `fracture_visible`, with within-fracture-count percentages.

| fracture_count_per_row | fracture_visible | n | fracture_count_total | pct_within_fracture_count |
| --- | --- | --- | --- | --- |
| 0 |  | 6004 | 6169 | 0.9732533635921543 |
| 0 | 1.0 | 165 | 6169 | 0.02674663640784568 |
| 1 |  | 679 | 8689 | 0.07814478075727932 |
| 1 | 1.0 | 8010 | 8689 | 0.9218552192427207 |
| 2 |  | 93 | 5103 | 0.018224573780129337 |
| 2 | 1.0 | 5010 | 5103 | 0.9817754262198707 |
| 3 | 1.0 | 364 | 364 | 1.0 |
| 4 |  | 1 | 2 | 0.5 |
| 4 | 1.0 | 1 | 2 | 0.5 |

