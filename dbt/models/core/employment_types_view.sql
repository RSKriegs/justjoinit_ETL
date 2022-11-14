{{
  config(
    materialized='view',
    schema='offers'
  )
}}

--A view for skills utilized in 'Employment types' related filters & graphs
WITH CTE as (
  SELECT id_jjit, CASE WHEN if_permanent=True THEN 'permanent' ELSE NULL END as Employment_type
  FROM `justjoinit-offers.offers.offers-table`
  UNION ALL
  SELECT id_jjit, CASE WHEN if_b2b=True THEN 'B2B' ELSE NULL END
  FROM `justjoinit-offers.offers.offers-table`
  UNION ALL
  SELECT id_jjit, CASE WHEN if_mandate=True THEN 'mandate' ELSE NULL END
  FROM `justjoinit-offers.offers.offers-table`
  UNION ALL
  SELECT id_jjit, CASE WHEN if_other=True THEN 'other' ELSE NULL END
  FROM `justjoinit-offers.offers.offers-table`)

SELECT Id_jjit, Employment_type
from CTE