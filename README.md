# FHIR Clinical Data Pipeline

## Clinical Interoperability + Analytics Portfolio Project

A healthcare informatics project demonstrating how a synthetic clinical scenario can be represented as structured **FHIR resources**, coded with standard clinical terminologies, conceptually mapped from **HL7 v2**, validated with Python, and transformed into a small analytics-ready clinical summary.

The project is intentionally small and transparent. It demonstrates interoperability concepts and a reproducible bridge from structured clinical resources to downstream analytics without claiming production EHR integration.

## Healthcare scenario

Synthetic patient `P001` is represented across a connected clinical record containing a Patient, Type 2 Diabetes Mellitus Condition, HbA1c Observation of 8.5%, Metformin MedicationRequest, Encounter and FHIR Bundle. No real patient data or protected health information is used.

## Interoperability components

| Component | Demonstrated use |
|---|---|
| FHIR | Patient, Condition, Observation, MedicationRequest, Encounter and Bundle resources |
| HL7 v2 | Example admission message and conceptual FHIR mapping |
| ICD-10-CM | Diagnosis representation |
| LOINC | HbA1c laboratory coding |
| UCUM | Standardized observation units |
| Python | Resource/reference validation and analytics extraction |
| CSV / JSON | Human-readable analytics and validation outputs |

## Reproducible workflow

Run from the repository root:

```bash
python scripts/analyze_fhir.py
```

The script uses only the Python standard library. It:

1. loads five core FHIR JSON resources;
2. verifies expected `resourceType` values;
3. checks that Condition, Observation, MedicationRequest and Encounter reference `Patient/P001`;
4. checks ICD-10-CM, LOINC and UCUM system identifiers;
5. extracts a compact patient-level analytics record;
6. writes `outputs/clinical_summary.csv` and `outputs/validation_report.json`;
7. exits with an error if a validation check fails.

## Analytics-ready output

The generated summary contains:

`patient_id` · `gender` · `birth_date` · `diagnosis_code` · `diagnosis` · `hba1c_loinc` · `hba1c_value` · `hba1c_unit` · `medication` · `encounter_status`

For the current synthetic record this captures ICD-10-CM `E11`, LOINC `4548-4`, HbA1c `8.5 %`, Metformin 500 mg and the encounter status while retaining the link back to the FHIR source resources.

## Repository structure

```text
data/       FHIR JSON resources
hl7/        sample HL7 v2 admission message
docs/       HL7-to-FHIR mapping notes
scripts/    reproducible Python validation/analytics workflow
outputs/    analytics-ready CSV and validation report
```

## What this project demonstrates

- **Clinical data modeling** — separating demographics, diagnoses, labs, medication and encounters into appropriate resources.
- **Terminology awareness** — ICD-10-CM, LOINC and UCUM rather than free text alone.
- **Interoperability reasoning** — connecting HL7 v2 concepts to FHIR resources.
- **Data-quality validation** — checking resource types, patient references and coding systems before analysis.
- **Analytics transformation** — extracting interoperable clinical data into a simple tabular output.
- **Privacy-safe development** — all records are synthetic.

## Scope and limitations

This is a **portfolio and educational interoperability demonstration**, not a production FHIR server, certified interface engine, medical device or clinical system. The examples have not been validated against a live EHR implementation or organization-specific FHIR profiles. The validation script checks selected portfolio invariants; it is not a substitute for full FHIR profile/schema validation.

## Why it matters for healthcare analytics

Healthcare analytics depends on more than models and dashboards. Data must first be represented consistently, coded meaningfully and checked before transformation. This project demonstrates the upstream interoperability and data-quality layer that supports reliable clinical and population-health analytics.

## Author

**Dr. Natheer Soliman, MD**  
Healthcare Data Analytics · Clinical Analytics · Health Informatics

[GitHub Profile](https://github.com/natheerne-hub)
