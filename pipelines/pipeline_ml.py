from __future__ import annotations

from pathlib import Path

from preprocessing.etl import run_default_etl
from training.train import main as train_main


def run_pipeline(project_root: str | Path | None = None, refresh_data: bool = False) -> None:
    """Ejecuta el flujo ML principal: ETL opcional y entrenamiento."""
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[1]
    if refresh_data:
        run_default_etl(root, split_national=False)
    train_main()


if __name__ == "__main__":
    run_pipeline(refresh_data=False)
