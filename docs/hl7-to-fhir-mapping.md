# HL7 v2 to FHIR Mapping

This educational example shows how common HL7 v2 segments can map conceptually to FHIR resources.

| HL7 v2 segment | Meaning | FHIR resource / element |
|---|---|---|
| PID | Patient identification | Patient |
| PV1 | Patient visit | Encounter |
| DG1 | Diagnosis | Condition |
| OBX | Observation/result | Observation |

## Coding systems used

- ICD-10-CM: diagnosis coding example (`E11`).
- LOINC: laboratory observation coding example (`4548-4` for HbA1c).
- UCUM: units of measure (`%`).

## Important note

HL7 v2-to-FHIR transformation is not always a one-to-one conversion. Production mappings depend on the message type, local implementation guides, profiles, terminology, and source-system conventions.

All patient data in this repository are synthetic and are provided for educational and portfolio purposes only.
