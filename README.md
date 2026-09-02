# FHIR Clinical Data Pipeline

A hands-on healthcare interoperability portfolio project demonstrating how synthetic clinical data can be represented with FHIR, standardized with clinical terminologies, and conceptually mapped from HL7 v2 messages.

## Project goals

- Understand core FHIR resources and references.
- Represent diagnoses with ICD-10-CM.
- Represent laboratory observations with LOINC and UCUM units.
- Demonstrate a simple HL7 v2 message and its conceptual mapping to FHIR.
- Build a foundation for later Python/SQL healthcare analytics work.

## Current synthetic patient scenario

Patient `P001` has a Type 2 Diabetes Mellitus condition, an HbA1c observation of 8.5%, a Metformin medication order, and a sample encounter. The resources are also collected in a FHIR Bundle.

## Repository structure

```text
data/
  patient-P001.json
  condition-P001-diabetes.json
  observation-P001-hba1c.json
  medicationrequest-P001-metformin.json
  encounter-P001.json
  bundle-P001.json
hl7/
  sample-admission.hl7
docs/
  hl7-to-fhir-mapping.md
```

## Standards demonstrated

| Standard | Role in this project |
|---|---|
| FHIR | Structured healthcare resources and references |
| HL7 v2 | Example healthcare message exchange |
| ICD-10-CM | Diagnosis coding |
| LOINC | Laboratory observation coding |
| UCUM | Standard units of measure |

## Data privacy

All patient records in this repository are fully synthetic examples created for learning and portfolio demonstration. No real patient data or protected health information is used.

## Next phase

The next phase will add a reproducible transformation/analytics workflow using Python and SQL, followed by data-quality checks and a small healthcare analytics output.

## Author

Dr. Natheer Soliman — Medical Doctor developing skills in Healthcare Data Analytics and Clinical Informatics.
