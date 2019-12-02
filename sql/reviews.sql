SELECT 
	user_id, 
 	course_id, 
	rating, 
	would_recommend,
 	created_on
FROM 
	reviews
WHERE
	email <> 'testuser@testing.com'
AND
	(user_id IS NOT NULL AND user_id <> 0)
AND
	(course_id IS NOT NULL AND course_id <> 0)
AND
	(rating > 0 AND rating <= 10)
ORDER BY
	created_on DESC
LIMIT 40000;