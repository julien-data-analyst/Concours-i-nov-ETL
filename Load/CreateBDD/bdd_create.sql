-- Active: 1766845709641@@127.0.0.1@5432@concoursinovv112
-- Création des différentes tables pour notre bdd
drop table if exists Competition_Publisher;
drop table if exists Location ;
drop table if exists Project ;
drop table if exists Competition ;
drop table if exists Publisher ;
drop table if exists Department ;
drop table if exists Region ;
drop table if exists Theme ;
drop table if exists Company ;

create table if not exists Publisher (
	id SERIAL primary key,
	name VARCHAR(100) not null,
	web_url VARCHAR(200) not null
);

create table if not exists Competition(
	vague SERIAL primary key,
	titre VARCHAR(100) not null,
	web_url TEXT not null,
	pdf_url TEXT not null,
	description TEXT not null,
	presentation TEXT not null,
	parution DATE not null
);

create table if not exists Competition_Publisher(
	id SERIAL PRIMARY KEY,
	id_pu INTEGER references Publisher(id),
	vague_comp INTEGER REFERENCES Competition(vague)
);

create table if not exists Region (
	id SERIAL primary key,
	name VARCHAR(50) not null
);

create table if not exists Department (
	id SERIAL primary key,
	name VARCHAR(50) not null,
	dep_number char(2) not null,
	id_reg INTEGER references Region(id)
);

create table if not exists Theme (
	id SERIAL primary key,
	theme varchar(200) not null,
	general_theme varchar(20) not null
);

create table if not exists Company (
	id SERIAL primary key,
	name varchar(50) not null,
	activity text
);

create table if not exists Project (
	id SERIAL primary key,
	name VARCHAR(50) not null,
	pdf_page integer not null,
	description text,
	project_amount bigint,
	project_allowance bigint,
	beginning_year integer,
	ending_year integer,
	month_dury integer,
	vague INTEGER REFERENCES Competition(vague),
	id_them INTEGER references Theme(id),
	id_comp INTEGER references Company(id)
);

create table if not exists Location (
	id SERIAL primary key,
	id_dep INTEGER references Department(id),
	id_proj INTEGER references Project(id)
);


