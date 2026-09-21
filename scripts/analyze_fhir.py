"""Validate the synthetic FHIR examples and export an analytics-ready summary.

Covers two layers of the portfolio:
  1. The original single-patient (P001) walkthrough, stored as five separate
     FHIR resource files in data/ -- kept as the interoperability "worked
     example" the README walks through resource by resource.
  2. A larger synthetic cohort (P002 onward), stored as one FHIR Bundle in
     data/cohort-bundle.json -- demonstrating the same validation and
     extraction logic applied at a more realistic scale.

Uses only the Python standard library so the portfolio workflow is easy to
run and audit.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "outputs"

P001_FILES = {
    "patient": "patient-P001.json",
    "condition": "condition-P001-diabetes.json",
    "observation": "observation-P001-hba1c.json",
    "medication": "medicationrequest-P001-metformin.json",
    "encounter": "encounter-P001.json",
}

ICD10_SYSTEM = "http://hl7.org/fhir/sid/icd-10-cm"
LOINC_SYSTEM = "http://loinc.org"
UCUM_SYSTEM = "http://unitsofmeasure.org"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def coding(resource: dict) -> dict:
    return resource.get("code", {}).get("coding", [{}])[0]


def summarize_patient(patient_id: str, resources: dict, checks: dict) -> dict:
    patient = resources["patient"]
    condition = resources["condition"]
    observation = resources["observation"]
    medication = resources["medication"]
    encounter = resources["encounter"]

    patient_ref = f"Patient/{patient_id}"
    prefix = patient_id

    checks[f"{prefix}:patient_resource_type"] = patient.get("resourceType") == "Patient"
    checks[f"{prefix}:condition_resource_type"] = condition.get("resourceType") == "Condition"
    checks[f"{prefix}:observation_resource_type"] = observation.get("resourceType") == "Observation"
    checks[f"{prefix}:medication_resource_type"] = medication.get("resourceType") == "MedicationRequest"
    checks[f"{prefix}:encounter_resource_type"] = encounter.get("resourceType") == "Encounter"
    checks[f"{prefix}:condition_patient_reference"] = condition.get("subject", {}).get("reference") == patient_ref
    checks[f"{prefix}:observation_patient_reference"] = observation.get("subject", {}).get("reference") == patient_ref
    checks[f"{prefix}:medication_patient_reference"] = medication.get("subject", {}).get("reference") == patient_ref
    checks[f"{prefix}:encounter_patient_reference"] = encounter.get("subject", {}).get("reference") == patient_ref
    checks[f"{prefix}:diagnosis_uses_icd10cm"] = coding(condition).get("system") == ICD10_SYSTEM
    checks[f"{prefix}:observation_uses_loinc"] = coding(observation).get("system") == LOINC_SYSTEM
    checks[f"{prefix}:observation_uses_ucum"] = observation.get("valueQuantity", {}).get("system") == UCUM_SYSTEM

    return {
        "patient_id": patient_id,
        "gender": patient.get("gender"),
        "birth_date": patient.get("birthDate"),
        "diagnosis_code": coding(condition).get("code"),
        "diagnosis": condition.get("code", {}).get("text"),
        "observation_loinc": coding(observation).get("code"),
        "observation_text": observation.get("code", {}).get("text"),
        "observation_value": observation.get("valueQuantity", {}).get("value"),
        "observation_unit": observation.get("valueQuantity", {}).get("code"),
        "medication": medication.get("medicationCodeableConcept", {}).get("text"),
        "encounter_status": encounter.get("status"),
    }


def load_p001(checks: dict) -> dict:
    resources = {name: load_json(DATA / filename) for name, filename in P001_FILES.items()}
    return summarize_patient("P001", resources, checks)


def load_cohort(checks: dict) -> list[dict]:
    bundle_path = DATA / "cohort-bundle.json"
    if not bundle_path.exists():
        return []

    bundle = load_json(bundle_path)
    checks["cohort_bundle:resource_type"] = bundle.get("resourceType") == "Bundle"

    by_patient: dict[str, dict] = {}
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        rtype = resource.get("resourceType")
        if rtype == "Patient":
            patient_id = resource.get("id")
            by_patient.setdefault(patient_id, {})["patient"] = resource
        else:
            ref = resource.get("subject", {}).get("reference", "")
            patient_id = ref.split("/")[-1] if "/" in ref else None
            if not patient_id:
                continue
            key = {
                "Condition": "condition",
                "Observation": "observation",
                "MedicationRequest": "medication",
                "Encounter": "encounter",
            }.get(rtype)
            if key:
                by_patient.setdefault(patient_id, {})[key] = resource

    summaries = []
    for patient_id in sorted(by_patient, key=lambda pid: int(pid[1:])):
        resources = by_patient[patient_id]
        if len(resources) != 5:
            checks[f"{patient_id}:complete_resource_set"] = False
            continue
        summaries.append(summarize_patient(patient_id, resources, checks))

    return summaries


def main() -> None:
    checks: dict[str, bool] = {}

    p001_summary = load_p001(checks)
    cohort_summaries = load_cohort(checks)
    all_summaries = [p001_summary] + cohort_summaries

    OUTPUT.mkdir(exist_ok=True)

    fieldnames = list(p001_summary.keys())
    with (OUTPUT / "clinical_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_summaries:
            writer.writerow(row)

    report = {
        "all_checks_passed": all(checks.values()),
        "patients_validated": len(all_summaries),
        "checks_run": len(checks),
        "checks_failed": [name for name, passed in checks.items() if not passed],
        "summary": all_summaries,
    }
    with (OUTPUT / "validation_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    print(f"Validated {len(all_summaries)} synthetic patients ({len(checks)} checks)")
    print(f"Checks passed: {sum(checks.values())}/{len(checks)}")
    print(f"Analytics summary: {OUTPUT / 'clinical_summary.csv'}")

    if not all(checks.values()):
        raise SystemExit("One or more validation checks failed")


if __name__ == "__main__":
    main()
