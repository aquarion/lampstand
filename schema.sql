CREATE TABLE hugReaction (username varchar(64), item varchar(255), primary key(username));
CREATE TABLE lastseen (username varchar(64), last_seen float, last_words varchar(255), primary key(username));
CREATE TABLE urllist (username varchar(64), time float, message varchar(255));
CREATE TABLE vote (id int, item varchar(64), vote_count tinyint);
