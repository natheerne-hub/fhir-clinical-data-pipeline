"""Generate a synthetic multi-patient FHIR cohort as a single Bundle resource.

This extends the project's original single-patient (P001) example with a
larger, reproducible synthetic cohort so the interoperability + analytics
workflow can be demonstrated at scale. No real patient data or protected
health information is used anywhere; every value is generated with a fixed
random seed.

Usage:
    python scripts/generate_cohort.py [--out data/cohort-bundle.json] [--n 25] [--seed 7]
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Each condition profile ties together a coherent, clinically plausible
# ICD-10-CM diagnosis, a LOINC-coded observation with a realistic value
# range and UCUM unit, and a matching medication order.
CONDITION_PROFILES = [
    {
        "diagnosis_code": "E11",
        "diagnosis_display": "Type 2 diabetes mellitus",
        "diagnosis_text": "Type 2 Diabetes Mellitus",
        "loinc_code": "4548-4",
        "loinc_display": "Hemoglobin A1c/Hemoglobin.total in Blood",
        "obs_text": "HbA1c",
        "value_range": (6.5, 11.0),
        "unit": "%",
        "unit_code": "%",
        "medication": "Metformin 500 mg",
    },
    {
        "diagnosis_code": "I10",
        "diagnosis_display": "Essential (primary) hypertension",
        "diagnosis_text": "Essential Hypertension",
        "loinc_code": "8480-6",
        "loinc_display": "Systolic blood pressure",
        "obs_text": "Systolic Blood Pressure",
        "value_range": (130, 175),
        "unit": "mmHg",
        "unit_code": "mm[Hg]",
        "medication": "Lisinopril 10 mg",
    },
    {
        "diagnosis_code": "E78.5",
        "diagnosis_display": "Hyperlipidemia, unspecified",
        "diagnosis_text": "Hyperlipidemia",
        "loinc_code": "2089-1",
        "loinc_display": "Cholesterol in LDL [Mass/volume] in Serum or Plasma",
        "obs_text": "LDL Cholesterol",
        "value_range": (130, 210),
        "unit": "mg/dL",
        "unit_code": "mg/dL",
        "medication": "Atorvastatin 20 mg",
    },
    {
        "diagnosis_code": "J45.909",
        "diagnosis_display": "Unspecified asthma, uncomplicated",
        "diagnosis_text": "Asthma",
        "loinc_code": "20150-9",
        "loinc_display": "Forced expiratory volume in 1 second",
        "obs_text": "FEV1",
        "value_range": (55, 85),
        "unit": "% predicted",
        "unit_code": "%",
        "medication": "Albuterol 90 mcg inhaler",
    },
    {
        "diagnosis_code": "E03.9",
        "diagnosis_display": "Hypothyroidism, unspecified",
        "diagnosis_text": "Hypothyroidism",
        "loinc_code": "3016-3",
        "loinc_display": "Thyrotropin [Units/volume] in Serum or Plasma",
        "obs_text": "TSH",
        "value_range": (5.5, 18.0),
        "unit": "mIU/L",
        "unit_code": "m[IU]/L",
        "medication": "Levothyroxine 75 mcg",
    },
]

ENCOUNTER_STATUSES = ["finished", "finished", "finished", "in-progress"]


def random_birth_date(rng: random.Random) -> str:
    today = date(2026, 9, 21)
    age_years = rng.randint(24, 88)
    birth = today - timedelta(days=age_years * 365 + rng.randint(0, 364))
    return birth.isoformat()


def random_effective_datetime(rng: random.Random) -> str:
    day = rng.randint(1, 28)
    month = rng.randint(1, 9)
    hour = rng.randint(7, 17)
    minute = rng.choice([0, 15, 30, 45])
    return f"2026-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00+02:00"


def build_patient(patient_id: str, rng: random.Random) -> dict:
    gender = rng.choice(["male", "female"])
    return {
        "resourceType": "Patient",
        "id": patient_id,
        "gender": gender,
        "birthDate": random_birth_date(rng),
    }


def build_condition(patient_id: str, profile: dict) -> dict:
    return {
        "resourceType": "Condition",
        "id": f"condition-{patient_id}",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active",
            }]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "code": {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                "code": profile["diagnosis_code"],
                "display": profile["diagnosis_display"],
            }],
            "text": profile["diagnosis_text"],
        },
    }


def build_observation(patient_id: str, profile: dict, rng: random.Random) -> dict:
    low, high = profile["value_range"]
    value = round(rng.uniform(low, high), 1)
    return {
        "resourceType": "Observation",
        "id": f"observation-{patient_id}",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory" if profile["obs_text"] != "Systolic Blood Pressure" else "vital-signs",
                "display": "Laboratory" if profile["obs_text"] != "Systolic Blood Pressure" else "Vital Signs",
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": profile["loinc_code"],
                "display": profile["loinc_display"],
            }],
            "text": profile["obs_text"],
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": random_effective_datetime(rng),
        "valueQuantity": {
            "value": value,
            "unit": profile["unit"],
            "system": "http://unitsofmeasure.org",
            "code": profile["unit_code"],
        },
    }


def build_medication_request(patient_id: str, profile: dict) -> dict:
    return {
        "resourceType": "MedicationRequest",
        "id": f"medicationrequest-{patient_id}",
        "status": "active",
        "intent": "order",
        "subject": {"reference": f"Patient/{patient_id}"},
        "medicationCodeableConcept": {"text": profile["medication"]},
    }


def build_encounter(patient_id: str, rng: random.Random) -> dict:
    return {
        "resourceType": "Encounter",
        "id": f"encounter-{patient_id}",
        "status": rng.choice(ENCOUNTER_STATUSES),
        "subject": {"reference": f"Patient/{patient_id}"},
    }


def build_cohort(n: int, rng: random.Random) -> list[dict]:
    entries = []
    for i in range(1, n + 1):
        patient_id = f"P{i + 1:03d}"  # P002, P003, ... continues from the existing P001 example
        profile = CONDITION_PROFILES[(i - 1) % len(CONDITION_PROFILES)]

        patient = build_patient(patient_id, rng)
        condition = build_condition(patient_id, profile)
        observation = build_observation(patient_id, profile, rng)
        medication = build_medication_request(patient_id, profile)
        encounter = build_encounter(patient_id, rng)

        for resource in (patient, condition, observation, medication, encounter):
            entries.append({"resource": resource})

    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "data" / "cohort-bundle.json"))
    parser.add_argument("--n", type=int, default=25,
                         help="Number of additional synthetic patients to generate (P002 onward)")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    entries = build_cohort(args.n, rng)

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "total": len(entries),
        "entry": entries,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(bundle, handle, indent=2)
        handle.write("\n")

    n_patients = len(entries) // 5
    print(f"Wrote synthetic cohort bundle to {out_path}")
    print(f"  Patients: {n_patients}  Resources: {len(entries)}")


if __name__ == "__main__":
    main()
