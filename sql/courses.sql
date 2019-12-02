SELECT
    c.course_id,
    c.title,
    c.description,
    c.syllabus,
    m.description AS methodology,
    cat.description AS category,
    fam.description AS family,
    c.type AS course_type,
    prange.description AS price_range,
    dur.description AS duration,
    langs.description AS `language`,
    c.updated_on
FROM
	EM_CURSOS COURSES
LEFT JOIN
    methodologies m
ON
	m.id = c.methodology_id
LEFT JOIN
	categories cat
ON
	cat.id = c.id_categ
LEFT JOIN
	categories fam
ON
	fam.id = c.id_categ_lev1
LEFT JOIN
	price_ranges prange
ON
	c.price_range = prange.id_price_range
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
