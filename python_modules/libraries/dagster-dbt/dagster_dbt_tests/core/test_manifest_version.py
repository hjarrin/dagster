from typing import Any

from dagster_dbt import DagsterDbtTranslator


def test_get_manifest_version() -> None:
    translator = DagsterDbtTranslator()
    manifest: dict[str, Any] = {
        "metadata": {
            "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v12.json",
        }
    }
    assert translator.get_manifest_version(manifest) == 12


def test_get_manifest_version_returns_none_when_missing() -> None:
    translator = DagsterDbtTranslator()

    assert translator.get_manifest_version({}) is None
    assert translator.get_manifest_version({"metadata": {}}) is None
