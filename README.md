# FHIR Clinical Data Pipeline

[![Validate FHIR Cohort Pipeline](https://github.com/natheerne-hub/fhir-clinical-data-pipeline/actions/workflows/validate-fhir.yml/badge.svg)](https://github.com/natheerne-hub/fhir-clinical-data-pipeline/actions/workflows/validate-fhir.yml)

### Clinical Interoperability + Analytics Portfolio Project

A healthcare informatics project demonstrating how synthetic clinical
scenarios can be represented as structured FHIR resources, coded with
standard clinical terminologies, conceptually mapped from HL7 v2, validated
with Python, and transformed into an analytics-ready clinical summary — at
both single-patient and cohort scale.

The project is intentionally transparent. It demonstrates interoperability
concepts and a reproducible bridge from structured clinical resources to
downstream analytics, without claiming production EHR integration.

## Healthcare scenario

**Worked example (P001).** Synthetic patient P001 is represented across a
connected clinical record containing a Patient, Type 2 Diabetes Mellitus
Condition, HbA1c Observation of 8.5%, Metformin MedicationRequest, Encounter
and FHIR Bundle — stored as individually readable resource files in `data/`
so each piece of the interoperability model can be inspected on its own.

**Synthetic cohort (P002–P026).** The same resource shapes are generated for
25 additional synthetic patients across five condition profiles — Type 2
diabetes, hypertension, hyperlipidemia, asthma, and hypothyroidism — each
with a clinically coherent ICD-10-CM diagnosis, LOINC-coded observation, and
matching medication order. The cohort is packaged as a single FHIR `Bundle`
(`data/cohort-bundle.json`), generated reproducibly with a fixed random seed.
This demonstrates the same validation and extraction logic operating at a
more realistic scale than a single hand-authored patient record.

No real patient data or protected health information is used anywhere in
this project.

## Interoperability components

| Component | Demonstrated use |
|---|---|
| FHIR | `Patient`, `Condition`, `Observation`, `MedicationRequest`, `Encounter` and `Bundle` resources, for both a single worked example and a 25-patient synthetic cohort |
| HL7 v2 | Example admission message and conceptual FHIR mapping |
| ICD-10-CM | Diagnosis representation across 5 condition profiles |
| LOINC | Laboratory / vital-sign observation coding |
| UCUM | Standardized observation units |
| Python | Resource/reference validation and analytics extraction across all 26 patients |
| CSV / JSON | Human-readable analytics and validation outputs |

## Reproducible workflow

Run from the repository root:

```bash
python scripts/generate_cohort.py --n 25 --seed 7
python scripts/analyze_fhir.py
```

`generate_cohort.py` uses only the Python standard library and a fixed seed
to regenerate `data/cohort-bundle.json` from scratch — the bundle is fully
reproducible, not hand-authored.

`analyze_fhir.py` then:

- loads the five P001 resource files **and** every patient entry in the
  cohort bundle;
- verifies expected `resourceType` values for every resource;
- checks that each `Condition`, `Observation`, `MedicationRequest` and
  `Encounter` references its own `Patient`;
- checks ICD-10-CM, LOINC and UCUM system identifiers on every diagnosis,
  observation and unit;
- extracts a compact patient-level analytics record for all 26 patients;
- writes `outputs/clinical_summary.csv` and `outputs/validation_report.json`;
- exits with an error if any validation check fails.

A GitHub Actions workflow (badge above) regenerates the cohort and re-runs
this validation on every push, so the badge reflects a live, reproducible
check rather than a one-time manual run.

## Analytics-ready output

The generated summary contains, per patient:

`patient_id · gender · birth_date · diagnosis_code · diagnosis · observation_loinc · observation_text · observation_value · observation_unit · medication · encounter_status`

Across the full synthetic population (P001 + 25-patient cohort) this
currently captures 5 distinct ICD-10-CM diagnoses, 5 LOINC-coded
observations, and 5 matching medication classes, while retaining the link
back to each patient's FHIR source resources. `validation_report.json`
records every individual check (313 checks across 26 patients in the
current dataset) plus a list of any that failed.

## Repository structure

```
data/                     FHIR JSON resources
  patient-P001.json                 Individual P001 worked-example resources
  condition-P001-diabetes.json
  observation-P001-hba1c.json
  medicationrequest-P001-metformin.json
  encounter-P001.json
  bundle-P001.json                  Bundle form of the P001 worked example
  cohort-bundle.json                Reproducible 25-patient synthetic cohort
hl7/                       Sample HL7 v2 admission message
docs/                       HL7-to-FHIR mapping notes
scripts/
  analyze_fhir.py                   Validation + analytics workflow (P001 + cohort)
  generate_cohort.py                Reproducible synthetic cohort generator
outputs/                    Analytics-ready CSV and validation report
.github/workflows/          CI pipeline that regenerates and re-validates the cohort
```

## What this project demonstrates

- **Clinical data modeling** — separating demographics, diagnoses, labs,
  medication and encounters into appropriate resources, for one patient and
  for a cohort.
- **Terminology awareness** — ICD-10-CM, LOINC and UCUM rather than free
  text alone, across 5 distinct condition profiles.
- **Interoperability reasoning** — connecting HL7 v2 concepts to FHIR
  resources.
- **Data-quality validation** — checking resource types, patient references
  and coding systems before analysis, at scale (313 checks, not one).
- **Analytics transformation** — extracting interoperable clinical data into
  a simple tabular output across a whole synthetic population.
- **Reproducibility** — the cohort is generated by a seeded script and
  re-validated by CI on every push, not hand-maintained.
- **Privacy-safe development** — all records are synthetic.

## Scope and limitations

This is a portfolio and educational interoperability demonstration, not a
production FHIR server, certified interface engine, medical device or
clinical system. The examples have not been validated against a live EHR
implementation or organization-specific FHIR profiles. The validation
script checks selected portfolio invariants; it is not a substitute for
full FHIR profile/schema validation.

## Why it matters for healthcare analytics

Healthcare analytics depends on more than models and dashboards. Data must
first be represented consistently, coded meaningfully and checked before
transformation — and that check needs to hold up across a population, not
just a single hand-picked example. This project demonstrates the upstream
interoperability and data-quality layer that supports reliable clinical and
population-health analytics.

## Author

**Dr. Natheer Soliman, MD**
Healthcare Data Analytics · Clinical Analytics · Health Informatics

[GitHub Profile](https://github.com/natheerne-hub)
