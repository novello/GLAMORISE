-- create and populate size table
use anp;

DROP TABLE IF EXISTS size;
CREATE TABLE size(
    size INTEGER,
    relation VARCHAR(255)
);

INSERT INTO size SELECT COUNT(*), "ANP" FROM ANP;

-- create history table
DROP TABLE IF EXISTS history;
CREATE TABLE history(
    content VARCHAR(1000)
);

-- add fulltext index for publication (only run once)
ALTER TABLE ANP ADD FULLTEXT(FIELD);
ALTER TABLE ANP ADD FULLTEXT(BASIN);
ALTER TABLE ANP ADD FULLTEXT(STATE);
ALTER TABLE ANP ADD FULLTEXT(OPERATOR);

