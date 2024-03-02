--
-- File generated with SQLiteStudio v3.0.2 on Сб мар 2 20:53:07 2024
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: services
DROP TABLE IF EXISTS services;
CREATE TABLE services (id INTEGER UNIQUE NOT NULL PRIMARY KEY ASC AUTOINCREMENT, service_name TEXT NOT NULL UNIQUE);
INSERT INTO services (id, service_name) VALUES (0, 'неизвестно');

-- Table: ownerships
DROP TABLE IF EXISTS ownerships;
CREATE TABLE ownerships (id INTEGER UNIQUE NOT NULL PRIMARY KEY ASC AUTOINCREMENT, ownership TEXT NOT NULL UNIQUE);
INSERT INTO ownerships (id, ownership) VALUES (0, 'неизвестно');

-- Table: lic_status_names
DROP TABLE IF EXISTS lic_status_names;
CREATE TABLE lic_status_names (id INTEGER UNIQUE NOT NULL PRIMARY KEY ASC AUTOINCREMENT, lic_status_name TEXT UNIQUE NOT NULL);
INSERT INTO lic_status_names (id, lic_status_name) VALUES (0, 'неизвестно');

-- Table: holders
DROP TABLE IF EXISTS holders;
CREATE TABLE holders (id INTEGER UNIQUE NOT NULL PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, ownership INTEGER NOT NULL REFERENCES ownerships (id), name_short TEXT, name_brand TEXT, addr_legal TEXT, inn TEXT, ogrn TEXT);
INSERT INTO holders (id, name, ownership, name_short, name_brand, addr_legal, inn, ogrn) VALUES (0, 'неизвестно', 0, 'неизвестно', 'неизвестно', 'неизвестно', '0', '0');

-- Table: licenses
DROP TABLE IF EXISTS licenses;
CREATE TABLE licenses (id INTEGER NOT NULL UNIQUE PRIMARY KEY ASC AUTOINCREMENT, holder INTEGER REFERENCES holders (id) NOT NULL, license_num INTEGER UNIQUE NOT NULL, license_num_old INTEGER, lic_status_name INTEGER NOT NULL REFERENCES lic_status_names (id), date_start INTEGER NOT NULL, date_end INTEGER NOT NULL, date_service_start INTEGER, service_name INTEGER REFERENCES services (id) NOT NULL, territory TEXT, registration INTEGER REFERENCES orders (id) NOT NULL, reregistration INTEGER REFERENCES orders (id) NOT NULL, prolongation INTEGER REFERENCES orders (id) NOT NULL, suspension_resume INTEGER REFERENCES orders (id) NOT NULL, termination INTEGER REFERENCES orders (id) NOT NULL);
INSERT INTO licenses (id, holder, license_num, license_num_old, lic_status_name, date_start, date_end, date_service_start, service_name, territory, registration, reregistration, prolongation, suspension_resume, termination) VALUES (0, 0, 0, 0, 0, 0, 0, 0, 0, 'неизвестно', 0, 0, 0, 0, 0);

-- Table: orders
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (id INTEGER UNIQUE NOT NULL PRIMARY KEY ASC AUTOINCREMENT, num TEXT, date INTEGER NOT NULL);
INSERT INTO orders (id, num, date) VALUES (0, 'неизвестно', 0);

-- Index: name_index
DROP INDEX IF EXISTS name_index;
CREATE INDEX name_index ON holders (name);

COMMIT TRANSACTION;
