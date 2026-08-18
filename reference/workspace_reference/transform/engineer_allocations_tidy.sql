-- Reshape raw.engineer_allocations_raw into a tidy, queryable model.
--
-- The source sheet is not a flat table:
--   row 1  merged week banners ("w/c 03/08" spanning 10 columns, then "w/c 10/08")
--   row 2  day/session headers ("Mon (AM)", "Mon (PM)", ... x2 weeks)
--   rows 3+ one row per engineer, 20 half-day slots each
--   then a blank row, an "Additional" banner, and a second block of note rows
--
-- So raw.engineer_allocations_raw keeps the sheet verbatim (all text, nothing
-- skipped) and this view does the interpretation. Row positions are located by
-- their marker text rather than hardcoded line numbers, so the view survives rows
-- being added above or below.
--
-- Apply with:
--   ./orchestrate/warehouse/pg.sh psql -f transform/engineer_allocations_tidy.sql
--
-- Then:
--   select * from raw.engineer_allocations order by engineer, week_commencing, slot;

CREATE OR REPLACE VIEW raw.engineer_allocations AS
WITH src AS (
    SELECT
        _smart_source_lineno AS ln,
        col_01,
        ARRAY[col_02, col_03, col_04, col_05, col_06, col_07, col_08, col_09, col_10,
              col_11, col_12, col_13, col_14, col_15, col_16, col_17, col_18, col_19,
              col_20, col_21] AS slots
    FROM raw.engineer_allocations_raw
),

-- Locate the structural rows by their marker text.
markers AS (
    SELECT
        (SELECT min(ln) FROM src WHERE btrim(col_01) = 'Engineer')   AS week_row,
        (SELECT min(ln) FROM src WHERE btrim(col_01) = 'Additional') AS additional_row
),

-- Row 1: week banners, only populated in the first column of each week block.
week_labels_raw AS (
    SELECT p, nullif(btrim(label), '') AS label
    FROM src, markers, unnest(src.slots) WITH ORDINALITY AS t(label, p)
    WHERE src.ln = markers.week_row
),
-- Forward-fill the merged banner across its block.
week_labels AS (
    SELECT
        p,
        first_value(label) OVER (PARTITION BY grp ORDER BY p) AS week_commencing
    FROM (
        SELECT p, label, count(label) OVER (ORDER BY p) AS grp
        FROM week_labels_raw
    ) g
),

-- Row 2 (immediately after the week row): day/session headers.
slot_labels AS (
    SELECT p, nullif(btrim(label), '') AS slot
    FROM src, markers, unnest(src.slots) WITH ORDINALITY AS t(label, p)
    WHERE src.ln = markers.week_row + 1
),

-- Engineer rows sit between the header rows and the "Additional" banner.
allocation_rows AS (
    SELECT src.ln, btrim(src.col_01) AS engineer, src.slots
    FROM src, markers
    WHERE src.ln > markers.week_row + 1
      AND (markers.additional_row IS NULL OR src.ln < markers.additional_row)
      AND nullif(btrim(src.col_01), '') IS NOT NULL
)

SELECT
    a.engineer,
    w.week_commencing,
    s.slot,
    split_part(s.slot, ' ', 1)                      AS day_of_week,
    btrim(split_part(s.slot, '(', 2), ')')          AS session,
    nullif(btrim(v.allocation), '')                 AS allocation,
    a.ln                                            AS source_lineno,
    t.p                                             AS source_column
FROM allocation_rows a
CROSS JOIN LATERAL unnest(a.slots) WITH ORDINALITY AS t(allocation_raw, p)
JOIN week_labels w ON w.p = t.p
JOIN slot_labels s ON s.p = t.p
CROSS JOIN LATERAL (SELECT t.allocation_raw AS allocation) v
WHERE s.slot IS NOT NULL;
