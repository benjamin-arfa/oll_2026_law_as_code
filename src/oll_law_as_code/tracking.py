"""MLflow experiment tracking via Databricks Free Edition."""

import os

from dotenv import load_dotenv
import mlflow


def setup_tracking() -> str:
    """Configure MLflow to track experiments on Databricks.

    Returns the experiment name.
    """
    load_dotenv()

    mlflow.set_tracking_uri("databricks")

    experiment_name = os.getenv(
        "MLFLOW_EXPERIMENT_NAME", "/Users/default/oll-law-as-code"
    )
    mlflow.set_experiment(experiment_name)

    mlflow.dspy.autolog(
        log_compiles=True,
        log_evals=True,
        log_traces_from_compile=True,
    )

    return experiment_name
