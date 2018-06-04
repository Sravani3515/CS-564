WITH MaxCurr AS (SELECT MAX(currently) AS 'max'
                 FROM Items)
SELECT itemId
FROM Items
WHERE currently = (SELECT max FROM MaxCurr);
