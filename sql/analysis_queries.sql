-- The encounters table is refreshed by python -m src.run_pipeline.
SELECT COUNT(*) AS encounters, COUNT(DISTINCT patient_nbr) AS unique_patients,
       ROUND(100.0 * SUM(readmit_30d) / COUNT(*), 2) AS early_readmit_pct FROM encounters;

SELECT age_group, COUNT(*) AS encounters, SUM(readmit_30d) AS early_readmissions,
       ROUND(100.0 * AVG(readmit_30d), 2) AS early_readmit_pct
FROM encounters GROUP BY age_group ORDER BY age_group;

SELECT stay_group, COUNT(*) AS encounters, SUM(readmit_30d) AS early_readmissions,
       ROUND(100.0 * AVG(readmit_30d), 2) AS early_readmit_pct
FROM encounters GROUP BY stay_group ORDER BY stay_group;

SELECT prior_inpatient_group, COUNT(*) AS encounters, SUM(readmit_30d) AS early_readmissions,
       ROUND(100.0 * AVG(readmit_30d), 2) AS early_readmit_pct
FROM encounters GROUP BY prior_inpatient_group ORDER BY prior_inpatient_group;

SELECT medication_change, COUNT(*) AS encounters, SUM(readmit_30d) AS early_readmissions,
       ROUND(100.0 * AVG(readmit_30d), 2) AS early_readmit_pct
FROM encounters GROUP BY medication_change ORDER BY medication_change;

SELECT admission_type_id, COUNT(*) AS encounters, SUM(readmit_30d) AS early_readmissions,
       ROUND(100.0 * AVG(readmit_30d), 2) AS early_readmit_pct
FROM encounters GROUP BY admission_type_id ORDER BY admission_type_id;

SELECT race, COUNT(*) AS encounters, SUM(readmit_30d) AS early_readmissions,
       ROUND(100.0 * AVG(readmit_30d), 2) AS early_readmit_pct
FROM encounters GROUP BY race ORDER BY race;

SELECT primary_diagnosis_group, COUNT(*) AS encounters, SUM(readmit_30d) AS early_readmissions,
       ROUND(100.0 * AVG(readmit_30d), 2) AS early_readmit_pct
FROM encounters GROUP BY primary_diagnosis_group ORDER BY primary_diagnosis_group;

SELECT 'Primary cohort' AS cohort, COUNT(*) AS encounters, ROUND(100.0*AVG(readmit_30d),2) AS early_readmit_pct FROM encounters
UNION ALL
SELECT 'Exclude death/hospice', COUNT(*), ROUND(100.0*AVG(readmit_30d),2) FROM encounters WHERE death_hospice_disposition=0;
