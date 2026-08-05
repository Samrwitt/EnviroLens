"""Demo script: sync synthetic aggregate data through the mock DHIS2 connector."""

from __future__ import annotations

import json

from database.session import SessionLocal
from integrations.dhis2_mock.router import DataValue, DataValueSet, import_data_value_sets
from pipelines.paths import JSON_DIR


def main():
    path = JSON_DIR / "dhis2_mock_payload.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = [DataValue(**v) for v in payload["dataValueSets"]["dataValues"]]
    db = SessionLocal()
    try:
        result = import_data_value_sets(DataValueSet(dataValues=values), db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
