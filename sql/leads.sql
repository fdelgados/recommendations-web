SELECT 
	l.user_id,
	l.course_id
FROM 
	leads l
LEFT JOIN
	courses c
ON
	c.course_id = l.leads
WHERE
	l.valid = 1
AND
	l.created_on >= DATE_SUB(NOW(), INTERVAL 1 YEAR) 
ORDER BY
	l.created_on DESC
LIMIT 50000;