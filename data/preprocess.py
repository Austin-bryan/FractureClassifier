from __future__ import annotations

from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    Float,
    String,
    select,
    func,
    case,
    and_,
    cast,
)
from sqlalchemy import union_all

# ------------------------------------------------------------
# Paths: preprocess.py and dataset.csv are in the same folder
# ------------------------------------------------------------
HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "dataset.csv"
OUT_MD = HERE / "stats.md"


# ------------------------------------------------------------
# Markdown writer that DOES NOT need tabulate
# ------------------------------------------------------------
def write_md_table(f, df: pd.DataFrame) -> None:
    """
    Write a simple GitHub-flavored markdown table with no third-party deps.
    This avoids pandas.to_markdown() which requires 'tabulate'.
    """
    if df is None or df.empty:
        f.write("_(no rows)_\n")
        return

    # Convert everything to safe string form
    cols = [str(c) for c in df.columns.tolist()]
    rows = df.astype(object).where(pd.notna(df), "").astype(str).values.tolist()

    # Header
    f.write("| " + " | ".join(cols) + " |\n")
    f.write("| " + " | ".join(["---"] * len(cols)) + " |\n")

    # Rows
    for r in rows:
        # Escape pipes so markdown doesn’t break
        safe = [cell.replace("|", "\\|") for cell in r]
        f.write("| " + " | ".join(safe) + " |\n")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"dataset.csv not found next to preprocess.py: {CSV_PATH}")

    # 1) Load CSV
    df = pd.read_csv(CSV_PATH)

    # Normalize column names minimally (your dataset is already well-formed)
    # This keeps your existing names, but strips accidental whitespace.
    df.columns = [c.strip() for c in df.columns]

    # 2) Create an in-memory SQLite engine (no database file, disappears after run)
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)

    # 3) Load into SQL table
    df.to_sql("dataset", engine, if_exists="replace", index=False)

    # 4) Define table schema explicitly (NO reflection)
    #    This matches the columns you showed earlier.
    metadata = MetaData()
    dataset = Table(
        "dataset",
        metadata,
        Column("filestem", String),
        Column("patient_id", Integer),
        Column("study_number", Integer),
        Column("timehash", Integer),
        Column("gender", String),
        Column("age", Float),
        Column("laterality", String),
        Column("projection", Integer),
        Column("initial_exam", Integer),
        Column("ao_classification", String),
        Column("cast", Integer),
        Column("diagnosis_uncertain", Integer),
        Column("osteopenia", Integer),
        Column("fracture_visible", Integer),
        Column("metal", Integer),
        Column("pixel_spacing", Float),
        Column("device_manufacturer", String),
    )

    # Helpers to treat blank strings as NULL (for ao_classification and laterality)
    ao_clean = func.nullif(func.trim(dataset.c.ao_classification), "")
    lat_clean = func.nullif(func.trim(dataset.c.laterality), "")

    # 5) Queries as OBJECTS (no SQL strings)

    overview_q = (
        select(
            func.count().label("total_rows"),
            func.count(func.distinct(dataset.c.patient_id)).label("unique_patients"),
            func.sum(case((dataset.c.fracture_visible == 1, 1), else_=0)).label("visible_fracture_rows"),
            func.sum(case((dataset.c.fracture_visible == 0, 1), else_=0)).label("not_visible_fracture_rows"),
            func.sum(case((ao_clean.is_(None), 1), else_=0)).label("ao_blank_or_null_rows"),
        )
        .select_from(dataset)
    )

    laterality_q = (
        select(
            func.coalesce(lat_clean, "NULL").label("laterality"),
            func.count().label("n"),
        )
        .select_from(dataset)
        .group_by(func.coalesce(lat_clean, "NULL"))
        .order_by(func.count().desc())
    )

    projection_q = (
        select(
            dataset.c.projection.label("projection"),
            func.count().label("n"),
        )
        .select_from(dataset)
        .group_by(dataset.c.projection)
        .order_by(func.count().desc())
    )

    ao_top_q = (
        select(
            func.coalesce(ao_clean, "NULL").label("ao_classification"),
            func.count().label("n"),
        )
        .select_from(dataset)
        .group_by(func.coalesce(ao_clean, "NULL"))
        .order_by(func.count().desc())
        .limit(30)
    )

    lat_x_proj_q = (
        select(
            func.coalesce(lat_clean, "NULL").label("laterality"),
            dataset.c.projection.label("projection"),
            func.count().label("n"),
        )
        .select_from(dataset)
        .group_by(func.coalesce(lat_clean, "NULL"), dataset.c.projection)
        .order_by(func.coalesce(lat_clean, "NULL"), func.count().desc())
    )

    visible_x_proj_q = (
        select(
            dataset.c.projection.label("projection"),
            dataset.c.fracture_visible.label("fracture_visible"),
            func.count().label("n"),
        )
        .select_from(dataset)
        .group_by(dataset.c.projection, dataset.c.fracture_visible)
        .order_by(dataset.c.projection, dataset.c.fracture_visible)
    )

    # Distinct projections per patient (how many patients have 1 vs 2 vs more views)
    per_patient = (
        select(
            dataset.c.patient_id.label("patient_id"),
            func.count(func.distinct(dataset.c.projection)).label("distinct_projections"),
        )
        .select_from(dataset)
        .group_by(dataset.c.patient_id)
    ).subquery()

    projections_per_patient_q = (
        select(
            per_patient.c.distinct_projections.label("distinct_projections"),
            func.count().label("patient_count"),
        )
        .select_from(per_patient)
        .group_by(per_patient.c.distinct_projections)
        .order_by(per_patient.c.distinct_projections)
    )

    # --- Fracture count per row (0..4) based on semicolons in ao_classification ---
    ao_norm = func.coalesce(ao_clean, "")  # ao_clean already NULLs-out blanks; coalesce makes it safe for string ops

    semicolon_ct = (
        func.length(ao_norm) - func.length(func.replace(ao_norm, ";", ""))
    )

    fracture_count_per_row = case(
        (ao_clean.is_(None), 0),                   # NULL or blank => 0 fractures
        else_=semicolon_ct + 1                     # otherwise => semicolons + 1
    ).label("fracture_count_per_row")

    fracture_count_dist_q = (
        select(
            fracture_count_per_row,
            func.count().label("n"),
        )
        .select_from(dataset)
        .group_by(fracture_count_per_row)
        .order_by(fracture_count_per_row)
    )

    # --- AO/OTA per-fracture distribution (split combined labels by ';' and count independently) ---
    # SQLite lacks a convenient split-to-rows, so we do it with a small UNION ALL of up to 4 tokens.
    # This treats each token as one fracture label and counts them across the dataset.

    token1 = func.trim(func.substr(ao_norm, 1, func.instr(ao_norm, ";") - 1))

    rest1 = func.substr(ao_norm, func.instr(ao_norm, ";") + 1)

    token2 = func.trim(func.substr(rest1, 1, func.instr(rest1, ";") - 1))
    rest2 = func.substr(rest1, func.instr(rest1, ";") + 1)

    token3 = func.trim(func.substr(rest2, 1, func.instr(rest2, ";") - 1))
    rest3 = func.substr(rest2, func.instr(rest2, ";") + 1)

    token4 = func.trim(rest3)

    # If there's no ';', instr(...) returns 0 and substr(..., 1, -1) is messy.
    # Use CASE to safely select either the whole string or the token.
    label_1 = case(
        (ao_clean.is_(None), None),
        (func.instr(ao_norm, ";") == 0, func.trim(ao_norm)),
        else_=token1,
    ).label("ao_label")

    label_2 = case(
        (ao_clean.is_(None), None),
        (func.instr(ao_norm, ";") == 0, None),
        (func.instr(rest1, ";") == 0, func.trim(rest1)),
        else_=token2,
    ).label("ao_label")

    label_3 = case(
        (ao_clean.is_(None), None),
        (func.instr(rest1, ";") == 0, None),
        (func.instr(rest2, ";") == 0, func.trim(rest2)),
        else_=token3,
    ).label("ao_label")

    label_4 = case(
        (ao_clean.is_(None), None),
        (func.instr(rest2, ";") == 0, None),
        else_=token4,
    ).label("ao_label")

    labels_union = union_all(
        select(label_1).select_from(dataset),
        select(label_2).select_from(dataset),
        select(label_3).select_from(dataset),
        select(label_4).select_from(dataset),
    ).subquery()

    ao_per_fracture_dist_q = (
        select(
            labels_union.c.ao_label.label("ao_classification"),
            func.count().label("n"),
        )
        .where(labels_union.c.ao_label.is_not(None))
        .where(func.length(func.trim(labels_union.c.ao_label)) > 0)
        .group_by(labels_union.c.ao_label)
        .order_by(func.count().desc())
        .limit(50)
    )

    # Per-patient flags: has_proj_1, has_proj_2, has_other_proj (anything not 1/2)
    per_patient_proj_flags = (
        select(
            dataset.c.patient_id.label("patient_id"),
            func.max(case((dataset.c.projection == 1, 1), else_=0)).label("has_proj_1"),
            func.max(case((dataset.c.projection == 2, 1), else_=0)).label("has_proj_2"),
            func.max(case((dataset.c.projection.not_in([1, 2]), 1), else_=0)).label("has_other_proj"),
        )
        .select_from(dataset)
        .group_by(dataset.c.patient_id)
    ).subquery()

    # Category per patient (restricted to presence of 1/2; "other" flagged separately)
    proj_pair_category = case(
        (and_(per_patient_proj_flags.c.has_proj_1 == 1, per_patient_proj_flags.c.has_proj_2 == 1), "has_1_and_2"),
        (and_(per_patient_proj_flags.c.has_proj_1 == 1, per_patient_proj_flags.c.has_proj_2 == 0), "only_1"),
        (and_(per_patient_proj_flags.c.has_proj_1 == 0, per_patient_proj_flags.c.has_proj_2 == 1), "only_2"),
        else_="has_neither_1_nor_2",
    ).label("proj_pair_category")

    patient_proj_pair_dist_q = (
        select(
            proj_pair_category,
            func.count().label("patient_count"),
            func.sum(per_patient_proj_flags.c.has_other_proj).label("patients_with_other_proj"),
        )
        .select_from(per_patient_proj_flags)
        .group_by(proj_pair_category)
        .order_by(
            case(
                (proj_pair_category == "has_1_and_2", 0),
                (proj_pair_category == "only_1", 1),
                (proj_pair_category == "only_2", 2),
                else_=3,
            )
        )
    )

    # XOR count (patients with exactly one of 1 or 2)
    patient_proj_xor_q = (
        select(
            func.sum(
                case(
                    (per_patient_proj_flags.c.has_proj_1 + per_patient_proj_flags.c.has_proj_2 == 1, 1),
                    else_=0,
                )
            ).label("patients_with_1_xor_2"),
            func.sum(
                case(
                    (per_patient_proj_flags.c.has_proj_1 + per_patient_proj_flags.c.has_proj_2 == 2, 1),
                    else_=0,
                )
            ).label("patients_with_1_and_2"),
            func.count().label("total_patients"),
        )
        .select_from(per_patient_proj_flags)
    )

    # --- Projection (1/2 only) x fracture_visible (counts + percent within projection) ---

    proj12 = dataset.c.projection.in_([1, 2])

    proj_vis_counts = (
        select(
            dataset.c.projection.label("projection"),
            dataset.c.fracture_visible.label("fracture_visible"),
            func.count().label("n"),
        )
        .select_from(dataset)
        .where(proj12)
        .group_by(dataset.c.projection, dataset.c.fracture_visible)
    ).subquery()

    proj_totals = (
        select(
            dataset.c.projection.label("projection"),
            func.count().label("projection_total"),
        )
        .select_from(dataset)
        .where(proj12)
        .group_by(dataset.c.projection)
    ).subquery()

    projection_x_visibility_q = (
        select(
            proj_vis_counts.c.projection,
            proj_vis_counts.c.fracture_visible,
            proj_vis_counts.c.n,
            proj_totals.c.projection_total,
            (proj_vis_counts.c.n * 1.0 / proj_totals.c.projection_total).label("pct_within_projection"),
        )
        .select_from(proj_vis_counts.join(proj_totals, proj_vis_counts.c.projection == proj_totals.c.projection))
        .order_by(proj_vis_counts.c.projection, proj_vis_counts.c.fracture_visible)
    )

    # --- Fracture count (0..4) x fracture_visible (counts + percent within fracture_count) ---

    fracture_vis_counts = (
        select(
            fracture_count_per_row.label("fracture_count_per_row"),
            dataset.c.fracture_visible.label("fracture_visible"),
            func.count().label("n"),
        )
        .select_from(dataset)
        .group_by(fracture_count_per_row, dataset.c.fracture_visible)
    ).subquery()

    fracture_totals = (
        select(
            fracture_count_per_row.label("fracture_count_per_row"),
            func.count().label("fracture_count_total"),
        )
        .select_from(dataset)
        .group_by(fracture_count_per_row)
    ).subquery()

    fracturecount_x_visibility_q = (
        select(
            fracture_vis_counts.c.fracture_count_per_row,
            fracture_vis_counts.c.fracture_visible,
            fracture_vis_counts.c.n,
            fracture_totals.c.fracture_count_total,
            (fracture_vis_counts.c.n * 1.0 / fracture_totals.c.fracture_count_total).label("pct_within_fracture_count"),
        )
        .select_from(
            fracture_vis_counts.join(
                fracture_totals,
                fracture_vis_counts.c.fracture_count_per_row == fracture_totals.c.fracture_count_per_row,
            )
        )
        .order_by(fracture_vis_counts.c.fracture_count_per_row, fracture_vis_counts.c.fracture_visible)
    )

    # 6) Execute into DataFrames
    overview_df = pd.read_sql(overview_q, engine)
    laterality_df = pd.read_sql(laterality_q, engine)
    projection_df = pd.read_sql(projection_q, engine)
    ao_top_df = pd.read_sql(ao_top_q, engine)
    lat_x_proj_df = pd.read_sql(lat_x_proj_q, engine)
    visible_x_proj_df = pd.read_sql(visible_x_proj_q, engine)
    projections_per_patient_df = pd.read_sql(projections_per_patient_q, engine)
    fracture_count_dist_df = pd.read_sql(fracture_count_dist_q, engine)
    ao_per_fracture_dist_df = pd.read_sql(ao_per_fracture_dist_q, engine)
    patient_proj_pair_dist_df = pd.read_sql(patient_proj_pair_dist_q, engine)
    patient_proj_xor_df = pd.read_sql(patient_proj_xor_q, engine)
    projection_x_visibility_df = pd.read_sql(projection_x_visibility_q, engine)
    fracturecount_x_visibility_df = pd.read_sql(fracturecount_x_visibility_q, engine)

    # 7) Write stats.md (no tabulate)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# Dataset stats\n\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write(f"Source: `{CSV_PATH.name}`\n\n")

        f.write("## Overview\n\n")
        write_md_table(f, overview_df)
        f.write("\n")

        f.write("## Laterality distribution\n\n")
        write_md_table(f, laterality_df)
        f.write("\n")

        f.write("## Projection distribution\n\n")
        write_md_table(f, projection_df)
        f.write("\n")

        f.write("## AO/OTA distribution (top 30, NULL includes blank)\n\n")
        write_md_table(f, ao_top_df)
        f.write("\n")

        f.write("## Laterality x Projection\n\n")
        write_md_table(f, lat_x_proj_df)
        f.write("\n")

        f.write("## Fracture visibility x Projection\n\n")
        write_md_table(f, visible_x_proj_df)
        f.write("\n")

        f.write("## Distinct projections per patient\n\n")
        write_md_table(f, projections_per_patient_df)
        f.write("\n")

        f.write("## Fracture count per row (derived from AO/OTA ';' separators)\n\n")
        f.write("Encoding rule: NULL/blank = 0 fractures, 0 ';' = 1, 1 ';' = 2, 2 ';' = 3, 3 ';' = 4.\n\n")
        write_md_table(f, fracture_count_dist_df)
        f.write("\n")

        f.write("## AO/OTA distribution per fracture (splitting combined labels on ';')\n\n")
        f.write("Combined AO/OTA labels like `A; B` are split and counted independently (A and B each contribute 1).\n\n")
        write_md_table(f, ao_per_fracture_dist_df)
        f.write("\n")

        f.write("## Patient projection coverage (projections 1 & 2 only; projection 3 ignored)\n\n")
        f.write("Patient-level counts for whether a patient has projection 1, projection 2, or both. ")
        f.write("`patients_with_other_proj` flags patients who have any projection outside {1,2} (e.g., 3) and would be affected by removal.\n\n")
        write_md_table(f, patient_proj_pair_dist_df)
        f.write("\n")

        f.write("### Projection 1 & 2 XOR summary\n\n")
        f.write("XOR means the patient has exactly one of {1,2}. `patients_with_1_and_2` means both.\n\n")
        write_md_table(f, patient_proj_xor_df)
        f.write("\n")

        f.write("## Projection x fracture visibility (projections 1 & 2 only)\n\n")
        f.write("Counts and within-projection percentages of `fracture_visible` for projections 1 and 2.\n\n")
        write_md_table(f, projection_x_visibility_df)
        f.write("\n")

        f.write("## Fracture count x fracture visibility\n\n")
        f.write("Derived fracture count per row (0..4) crossed with `fracture_visible`, with within-fracture-count percentages.\n\n")
        write_md_table(f, fracturecount_x_visibility_df)
        f.write("\n")

    print(f"Wrote: {OUT_MD}")


if __name__ == "__main__":
    main()