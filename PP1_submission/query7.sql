WITH ItemsOver100 AS (
    SELECT DISTINCT itemId
    FROM Bids
    WHERE amount > 100
),

ExpensiveCats AS (
    SELECT DISTINCT C.category
    FROM Categories C, ItemsOver100 I
    WHERE I.itemId = C.itemId
)

SELECT COUNT(*)
FROM ExpensiveCats;