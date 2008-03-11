create table hugReaction (username varchar(64), item varchar(255), primary key(username));
create table lastseen (username varchar(64), last_seen float, last_words varchar(255), primary key(username));
create table urllist (username varchar(64), time float, message varchar(255));
