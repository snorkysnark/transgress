UPDATE pages
SET content = tmp.content
FROM pages_update AS tmp
WHERE pages.id = tmp.id;

DROP TABLE pages_update;
