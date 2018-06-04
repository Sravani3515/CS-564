WITH Sellers AS (SELECT DISTINCT seller
                 FROM Items)

SELECT COUNT(*) 
FROM Users
WHERE rating > 1000
AND userId IN (SELECT * FROM Sellers);


