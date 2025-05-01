-- init.sql
USE chall;

CREATE TABLE
	IF NOT EXISTS USERS (
		id char(36) not null primary key default (UUID ()),
		username varchar(255) not null unique,
		password varchar(255) not null,
		css varchar(255) default null,
		pow_challenge char(16) default null
	);

CREATE TABLE
	IF NOT EXISTS POSTS (
		id char(36) not null primary key default (UUID ()),
		user_id char(36) not null references USERS,
		title varchar(255) not null,
		content text not null
	);

CREATE TABLE
	IF NOT EXISTS NOTES (
		id integer not null primary key AUTO_INCREMENT,
		user_id char(36) not null references USERS,
		post_id char(36) not null references POSTS ON DELETE CASCADE,
		content text not null
	);

