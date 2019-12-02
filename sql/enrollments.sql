SELECT
	u.user_id,
 	ec.course_id,
 	e.created_on
FROM 
	users u
JOIN 
	enrollments_users eu
ON 
	eu.user_id = u.user_id            
JOIN 
	enrollments e
ON 
	eu.id_user_enrollment = e.id_user_enrollment
JOIN 
	enrollments_courses ec 
ON 
	ec.id_enrollment_course = e.id_enrollment_course
AND 
	e.created_on >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
ORDER BY
	e.created_on DESC;