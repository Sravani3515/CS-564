WITH Sellers AS (
    SELECT DISTINCT I.seller
    FROM Items I
),

Bidders AS (
    SELECT DISTINCT B.userId
    FROM Bids B
)

SELECT COUNT(*)
FROM Sellers S, Bidders B
WHERE S.seller = B.userId;