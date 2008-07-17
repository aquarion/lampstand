CREATE TABLE hugReaction (username varchar(64), item varchar(255), primary key(username));
CREATE TABLE lastseen (username varchar(64), last_seen float, last_words varchar(255), primary key(username));
CREATE TABLE nickserv (server varchar(255) PRIMARY KEY, password varchar(255));
CREATE TABLE urllist (username varchar(64), time float, message varchar(255));
CREATE TABLE vote (id INTEGER PRIMARY KEY, username varchar(64), item varchar(64), vote tinyint, time float, textline varchar(255));
