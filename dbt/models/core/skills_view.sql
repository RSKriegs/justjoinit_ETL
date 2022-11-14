{{
  config(
    materialized='view',
    schema='offers'
  )
}}

--A view for skills utilized in 'Skills' section in Looker Studio dashboard.
WITH CTE as (
  SELECT id_jjit,skills_name_0
  FROM `justjoinit-offers.offers.offers-table`
  UNION ALL
  SELECT id_jjit, skills_name_1
  FROM `justjoinit-offers.offers.offers-table`
  UNION ALL
  SELECT id_jjit, skills_name_2
  FROM `justjoinit-offers.offers.offers-table`)

SELECT *
from CTE