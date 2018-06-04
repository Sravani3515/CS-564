WITH FourCats AS (SELECT *
                  FROM Categories
                  GROUP BY itemId
                  HAVING COUNT(category) = 4)
SELECT COUNT(*)
FROM FourCats;
