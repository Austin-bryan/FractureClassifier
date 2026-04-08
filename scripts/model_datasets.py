from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd
from sqlalchemy import (
    MetaData,
    Table,
    and_,
    cast,
    create_engine,
    func,
    literal,
    select,
    String,
)
from sqlalchemy.engine import Engine

# Internal sentinel for empty ao_classification values.
_NULL_CLASS: Final[str] = ""


class ModelDataQuery:
    def __init__(self, dataset_csv: Path | str) -> None:
        self.dataset_csv = Path(dataset_csv)

        if not self.dataset_csv.exists():
            raise FileNotFoundError(f"Could not find dataset CSV at: {self.dataset_csv}")

        self.engine: Engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        self.metadata = MetaData()

        self._load_csv()
        self.dataset = Table("dataset", self.metadata, autoload_with=self.engine)

    def _load_csv(self) -> None:
        dataframe = pd.read_csv(self.dataset_csv)
        dataframe.columns = [column.strip() for column in dataframe.columns]
        dataframe.to_sql("dataset", self.engine, if_exists="replace", index=False)

    def _get_model_data(
        self,
        projections: list[int],
        min_class_size: int,
        max_class_count: int,
    ) -> list[str]:
        if not projections:
            raise ValueError("projections must contain at least one projection value")

        if min_class_size < 1:
            raise ValueError("min_class_size must be at least 1")

        if max_class_count < 1:
            raise ValueError("max_class_count must be at least 1")

        dataset = self.dataset

        filestem_expr = cast(dataset.c.filestem, String)
        laterality_expr = cast(dataset.c.laterality, String)
        projection_expr = cast(dataset.c.projection, String)
        class_raw_expr = cast(dataset.c.ao_classification, String)

        trimmed_filestem = func.trim(filestem_expr)
        trimmed_class = func.trim(class_raw_expr)

        class_name_expr = func.coalesce(
            func.nullif(trimmed_class, ""),
            literal(_NULL_CLASS),
        ).label("class_name")

        normalized = (
            select(
                filestem_expr.label("filestem"),
                laterality_expr.label("laterality"),
                projection_expr.label("projection"),
                class_name_expr,
            )
            .where(
                and_(
                    dataset.c.filestem.is_not(None),
                    trimmed_filestem != "",
                    laterality_expr == "R",
                    projection_expr.in_([str(projection) for projection in projections]),
                )
            )
            .cte("normalized")
        )

        eligible_classes = (
            select(
                normalized.c.class_name,
                func.count().label("class_count"),
            )
            .group_by(normalized.c.class_name)
            .having(func.count() >= min_class_size)
            .order_by(
                func.count().desc(),
                normalized.c.class_name.asc(),
            )
            .limit(max_class_count)
            .cte("eligible_classes")
        )

        query = (
            select(normalized.c.filestem)
            .join(
                eligible_classes,
                normalized.c.class_name == eligible_classes.c.class_name,
            )
            .order_by(
                eligible_classes.c.class_count.desc(),
                normalized.c.class_name.asc(),
                normalized.c.filestem.asc(),
            )
        )

        with self.engine.connect() as connection:
            result = connection.execute(query)
            return [str(row[0]) for row in result.fetchall()]

    def get_modelA_data(self, min_class_size: int, max_class_count: int) -> list[str]:
        return self._get_model_data(
            projections=[1],
            min_class_size=min_class_size,
            max_class_count=max_class_count,
        )

    def get_modelB_data(self, min_class_size: int, max_class_count: int) -> list[str]:
        return self._get_model_data(
            projections=[2],
            min_class_size=min_class_size,
            max_class_count=max_class_count,
        )

    def get_modelU_data(self, min_class_size: int, max_class_count: int) -> list[str]:
        return self._get_model_data(
            projections=[1, 2],
            min_class_size=min_class_size,
            max_class_count=max_class_count,
        )


# Example usage
if __name__ == "__main__":
    query = ModelDataQuery("../data/dataset.csv")

    model_a_stems = query.get_modelA_data(min_class_size=200, max_class_count=6)
    model_b_stems = query.get_modelB_data(min_class_size=200, max_class_count=6)
    model_u_stems = query.get_modelU_data(min_class_size=200, max_class_count=6)

    print(f"Model A stems: {len(model_a_stems)}")
    print(f"Model B stems: {len(model_b_stems)}")
    print(f"Model U stems: {len(model_u_stems)}")

    print("\nFirst 10 Model A stems:")
    for stem in model_a_stems[:10]:
        print(stem)

    print("\nFirst 10 Model B stems:")
    for stem in model_b_stems[:10]:
        print(stem)