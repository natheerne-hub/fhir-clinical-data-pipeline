"""Validate the synthetic FHIR example and export an analytics-ready summary.

Uses only the Python standard library so the portfolio workflow is easy to run.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "outputs"

FILES = {
    "patient": "patient-P001.json",
    "condition": "condition-P001-diabetes.json",
    "observation": "observation-P001-hba1c.json",
    "medication": "medicationrequest-P001-metformin.json",
    "encounter": "encounter-P001.json",
}


def load_json(filename: str) -> dict:
    with (DATA / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def coding(resource: dict) -> dict:
    return resource.get("code", {}).get("coding", [{}])[0]


def main() -> None:
    resources = {name: load_json(filename) for name, filename in FILES.items()}
    patient = resources["patient"]
    condition = resources["condition"]
    observation = resources["observation"]
    medication = resources["medication"]
    encounter = resources["encounter"]

    patient_ref = f"Patient/{patient.get('id')}"
    checks = {
        "patient_resource_type": patient.get("resourceType") == "Patient",
        "condition_resource_type": condition.get("resourceType") == "Condition",
        "observation_resource_type": observation.get("resourceType") == "Observation",
        "medication_resource_type": medication.get("resourceType") == "MedicationRequest",
        "encounter_resource_type": encounter.get("resourceType") == "Encounter",
        "condition_patient_reference": condition.get("subject", {}).get("reference") == patient_ref,
        "observation_patient_reference": observation.get("subject", {}).get("reference") == patient_ref,
        "medication_patient_reference": medication.get("subject", {}).get("reference") == patient_ref,
        "encounter_patient_reference": encounter.get("subject", {}).get("reference") == patient_ref,
        "diagnosis_uses_icd10cm": coding(condition).get("system") == "http://hl7.org/fhir/sid/icd-10-cm",
        "hba1c_uses_loinc": coding(observation).get("system") == "http://loinc.org",
        "hba1c_uses_ucum": observation.get("valueQuantity", {}).get("system") == "http://unitsofmeasure.org",
    }

    summary = {
        "patient_id": patient.get("id"),
        "gender": patient.get("gender"),
        "birth_date": patient.get("birthDate"),
        "diagnosis_code": coding(condition).get("code"),
        "diagnosis": condition.get("code", {}).get("text"),
        "hba1c_loinc": coding(observation).get("code"),
        "hba1c_value": observation.get("valueQuantity", {}).get("value"),
        "hba1c_unit": observation.get("valueQuantity", {}).get("code"),
        "medication": medication.get("medicationCodeableConcept", {}).get("text"),
        "encounter_status": encounter.get("status"),
    }

    OUTPUT.mkdir(exist_ok=True)

    with (OUTPUT / "clinical_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary.keys())
        writer.writeheader()
        writer.writerow(summary)

    report = {
        "all_checks_passed": all(checks.values()),
        "checks": checks,
        "summary": summary,
    }
    with (OUTPUT / "validation_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    print(f"Validated {len(resources)} FHIR resources")
    print(f"Checks passed: {sum(checks.values())}/{len(checks)}")
    print(f"Analytics summary: {OUTPUT / 'clinical_summary.csv'}")

    if not all(checks.values()):
        raise SystemExit("One or more validation checks failed")


if __name__ == "__main__":
    main()
