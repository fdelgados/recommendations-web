SELECT
    c.course_id,
    c.title,
    c.description,
    c.syllabus,
    c.course_type_id AS course_type,
    c.category_id AS category,
    c.methodology_id AS methodology,
    c.price_range_id AS price_range,
    c.duration_id AS duration,
    c.is_flexible AS flexible,
    langs.code AS `language`,
    c.location_id AS `location`,
    c.updated_on
FROM
	EM_CURSOS COURSES
LEFT JOIN
	languages langs
ON
	langs.id = c.lang_id
LEFT JOIN
	duration_types dur
ON
	dur.id = c.duration
WHERE
	c.is_indexable = 1
ORDER BY
    c.updated_on DESC;
