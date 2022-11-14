{{
  config(
    materialized='view',
    schema='offers'
  )
}}

--the logic behind this query is that it assumes that the shortest Id_jjit key is the original one.
--The MIN() clause works like SELECT TOP 1 Id_jjit FROM [table] ORDER BY ASC - and as original keys are assumed as the shortest ones, they would be included.
--I am not 100% if this applies to all records, but at least to each that I have verified.
--I deduplicated that due to API shortcomings that multiplicated offers only because they were advertised for multiple locations.
--I excluded some columns from GROUP BY clause as well to perform deduplication correctly.
WITH ids_after_deduplication AS 
(
  SELECT MIN(Id_jjit) AS Id_jjit
  from `justjoinit-offers.offers.offers-table`
  GROUP BY Title
    ,Marker_icon
    ,Workplace_type
    ,Company_name
    ,Company_url
    ,Experience_level
    ,Remote_interview
    ,Remote
    ,Open_to_hire_Ukrainians
    ,Company_size_from
    ,Company_size_to
    ,if_permanent
    ,salary_from_permanent
    ,salary_to_permanent
    ,salary_currency_permanent
    ,if_b2b
    ,salary_from_b2b
    ,salary_to_b2b
    ,salary_currency_b2b
    ,if_mandate
    ,salary_from_mandate
    ,salary_to_mandate
    ,salary_currency_mandate
    ,if_other
    ,salary_from_other
    ,salary_to_other
    ,salary_currency_other
    ,skills_name_0
    ,skills_value_0
    ,skills_name_1
    ,skills_value_1
    ,skills_name_2
    ,skills_value_2
)

SELECT original_table.*
from `justjoinit-offers.offers.offers-table` original_table
RIGHT JOIN ids_after_deduplication ON original_table.Id_jjit=ids_after_deduplication.Id_jjit