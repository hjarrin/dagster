from dagster_dbt import DagsterDbtTranslator


def test_get_manifest_version():
    translator = DagsterDbtTranslator()
    manifest = {
        "metadata": {
            "dbt_schema_version": "https://schemas.getdbt.com/dbt/manifest/v12.json",
        }
    }
    assert translator.get_manifest_version(manifest) == 12
