# -*- coding: utf-8 -*-

import sqlite3
import logging

ERROR_STATE = None
EMPTY_STATE = 0
SUCCESS_STATE = 0


def db_close(db):
    if db is not None:
        db.commit()
        db.close()


_cached_ids = {}
_new_holder_id = 1


def saved_id(get_id):
    def get_saved_id(db, *args):
        str_args = list(map(lambda a: str(a), args))
        hash_args = ','.join(str_args)
        if hash_args in _cached_ids:
            return _cached_ids[hash_args]
        db_id = get_id(db, *args)
        if db_id is not None and EMPTY_STATE < db_id:
            _cached_ids[hash_args] = db_id
        return db_id
    return get_saved_id


@saved_id
def holder_id(db, name, ownership, addr_legal, inn, ogrn):

    if db is None:
        return ERROR_STATE

    db_query = "SELECT holders.id FROM holders\
    WHERE holders.name = ? AND holders.ownership = ? AND holders.addr_legal {} AND holders.inn {} AND holders.ogrn {}\
    LIMIT 1".format('IS NULL' if addr_legal is None else '= ?',
                    'IS NULL' if inn is None else '= ?',
                    'IS NULL' if ogrn is None else '= ?')

    db_query_params = [name, ownership,]
    if addr_legal is not None:
        db_query_params.append(addr_legal)
    if inn is not None:
        db_query_params.append(inn)
    if ogrn is not None:
        db_query_params.append(ogrn)

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, db_query_params)

        ids = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if ids is None or len(ids) == 0:
        return EMPTY_STATE

    return ids[0]


@saved_id
def holder_cached_only_id(db, name, ownership, addr_legal, inn, ogrn):
    return EMPTY_STATE


@saved_id
def holder_save_id(db, name, ownership, addr_legal, inn, ogrn):
    global _new_holder_id
    db_id = _new_holder_id
    _new_holder_id = _new_holder_id + 1
    return db_id


@saved_id
def lic_status_name_id(db, lic_status_name):

    if db is None:
        return ERROR_STATE

    db_query = "SELECT lic_status_names.id FROM lic_status_names WHERE lic_status_names.lic_status_name = ? LIMIT 1"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, (lic_status_name,))

        ids = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if ids is None or len(ids) == 0:
        return EMPTY_STATE

    return ids[0]


@saved_id
def order_id(db, num, date):

    if db is None:
        return ERROR_STATE

    db_query = ("SELECT orders.id FROM orders WHERE orders.num {} AND orders.date = ? LIMIT 1".
                format('IS NULL' if num is None else '= ?'))

    db_query_params = [date,]
    if num is not None:
        db_query_params.insert(0, num)

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, db_query_params)

        ids = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if ids is None or len(ids) == 0:
        return EMPTY_STATE

    return ids[0]


@saved_id
def ownership_id(db, ownership):

    if db is None:
        return ERROR_STATE

    db_query = "SELECT ownerships.id FROM ownerships WHERE ownerships.ownership = ? LIMIT 1"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, (ownership,))

        ids = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if ids is None or len(ids) == 0:
        return EMPTY_STATE

    return ids[0]


@saved_id
def service_id(db, service_name):

    if db is None:
        return ERROR_STATE

    db_query = "SELECT services.id FROM services WHERE services.service_name = ? LIMIT 1"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, (service_name,))

        ids = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if ids is None or len(ids) == 0:
        return EMPTY_STATE

    return ids[0]


def add_holder(db, name, ownership, name_short, name_brand, addr_legal, inn, ogrn):

    if db is None:
        return ERROR_STATE

    if name is None:
        return EMPTY_STATE

    db_id = holder_cached_only_id(db, name, ownership, addr_legal, inn, ogrn)
    if db_id is not None and EMPTY_STATE < db_id:
        return db_id
    else:
        global _new_holder_id
        db_id = _new_holder_id

    db_query_insert = "INSERT INTO holders(id, name, ownership, name_short, name_brand, addr_legal, inn, ogrn)\
    VALUES(?, ?, ?, ?, ?, ?, ?, ?)"

    db_cursor = db.cursor()

    try:
        db_cursor.execute(db_query_insert, (db_id, name, ownership, name_short, name_brand, addr_legal, inn, ogrn,))
        
    except (sqlite3.DatabaseError, sqlite3.IntegrityError) as e:
        
        logging.critical("Database insert error - {}".format(e))
        return ERROR_STATE

    return holder_save_id(db, name, ownership, addr_legal, inn, ogrn)


def add_lic_status_name(db, lic_status_name):

    if db is None:
        return ERROR_STATE

    if lic_status_name is None:
        return EMPTY_STATE

    db_id = lic_status_name_id(db, lic_status_name)
    if db_id is not None and EMPTY_STATE < db_id:
        return db_id

    db_query_insert = "INSERT INTO lic_status_names(lic_status_name) VALUES(?)"

    db_cursor = db.cursor()

    try:
        db_cursor.execute(db_query_insert, (lic_status_name,))
        
    except (sqlite3.DatabaseError, sqlite3.IntegrityError) as e:
        
        logging.critical("Database insert error - {}".format(e))
        return ERROR_STATE

    return lic_status_name_id(db, lic_status_name)


def add_order(db, num, date):

    if db is None:
        return ERROR_STATE

    if date is None:
        return EMPTY_STATE

    db_id = order_id(db, num, date)
    if db_id is not None and EMPTY_STATE < db_id:
        return db_id

    db_query_insert = "INSERT INTO orders(num, date) VALUES(?, ?)"

    db_cursor = db.cursor()

    try:
        db_cursor.execute(db_query_insert, (num, date,))
        
    except (sqlite3.DatabaseError, sqlite3.IntegrityError) as e:
        
        logging.critical("Database insert error - {}".format(e))
        return ERROR_STATE

    return order_id(db, num, date)


def add_ownership(db, ownership):

    if db is None:
        return ERROR_STATE

    if ownership is None:
        return EMPTY_STATE

    db_id = ownership_id(db, ownership)
    if db_id is not None and EMPTY_STATE < db_id:
        return db_id

    db_query_insert = "INSERT INTO ownerships(ownership) VALUES(?)"

    db_cursor = db.cursor()

    try:
        db_cursor.execute(db_query_insert, (ownership,))
        
    except (sqlite3.DatabaseError, sqlite3.IntegrityError) as e:
        
        logging.critical("Database insert error - {}".format(e))
        return ERROR_STATE

    return ownership_id(db, ownership)


def add_service(db, service_name):

    if db is None:
        return ERROR_STATE

    if service_name is None:
        return EMPTY_STATE

    db_id = service_id(db, service_name)
    if db_id is not None and EMPTY_STATE < db_id:
        return db_id

    db_query_insert = "INSERT INTO services(service_name) VALUES(?)"

    db_cursor = db.cursor()

    try:
        db_cursor.execute(db_query_insert, (service_name,))
        
    except (sqlite3.DatabaseError, sqlite3.IntegrityError) as e:
        
        logging.critical("Database insert error - {}".format(e))
        return ERROR_STATE

    return service_id(db, service_name)


def add_license(db, holder, license_num, license_old, lic_status_name, date_start, date_end, date_service_start,
                service_name, territory, registration, reregistration, prolongation, suspension_resume, termination):

    if db is None:
        return ERROR_STATE

    db_query_insert = "INSERT INTO licenses(holder, license_num, license_num_old, lic_status_name,\
    date_start, date_end, date_service_start, service_name, territory,\
    registration, reregistration, prolongation, suspension_resume, termination)\
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    db_cursor = db.cursor()

    try:
        db_cursor.execute(db_query_insert, (holder, license_num, license_old, lic_status_name,
                                            date_start, date_end, date_service_start,
                                            service_name, territory,
                                            registration, reregistration,
                                            prolongation, suspension_resume, termination,))
        
    except (sqlite3.DatabaseError, sqlite3.IntegrityError) as e:
        
        logging.critical("Database insert error - {} at {}".format(e, license_num))
        return ERROR_STATE

    return SUCCESS_STATE


def date_first(db):
    if db is None:
        return ERROR_STATE

    db_query = "SELECT MIN(licenses.date_start,\
    (SELECT MIN(orders.date) FROM orders WHERE orders.id > 0)) as first_date FROM\
     licenses WHERE licenses.date_start ORDER BY first_date ASC LIMIT 1"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query)

        min_dates = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if min_dates is None or len(min_dates) == 0:
        return EMPTY_STATE

    return min_dates[0]


def history_licenses_summary(db, date_timestamp):
    if db is None:
        return ERROR_STATE

    db_query = "SELECT count(licenses.license_num) FROM licenses WHERE (\
    ((licenses.registration > 0 AND (SELECT orders.date FROM orders WHERE licenses.registration = orders.id) < ?) OR\
    (licenses.registration = 0 AND licenses.date_start < ?)) AND\
    ((licenses.termination > 0 AND (SELECT orders.date FROM orders WHERE licenses.termination = orders.id) >= ?) OR\
    (licenses.termination = 0 AND licenses.date_end >=?))) LIMIT 1"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, (date_timestamp, date_timestamp, date_timestamp, date_timestamp,))

        licenses_count = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if licenses_count is None or len(licenses_count) == 0:
        return EMPTY_STATE

    return licenses_count[0]


def history_licenses_service(db, date_timestamp):
    if db is None:
        return ERROR_STATE

    db_query = "SELECT services.id, services.service_name, count(licenses.license_num) AS lic_count FROM licenses JOIN\
    services ON licenses.service_name = services.id WHERE (\
    ((licenses.registration > 0 AND (SELECT orders.date FROM orders WHERE licenses.registration = orders.id) < ?) OR\
    (licenses.registration = 0 AND licenses.date_start < ?)) AND\
    ((licenses.termination > 0 AND (SELECT orders.date FROM orders WHERE licenses.termination = orders.id) >= ?) OR\
    (licenses.termination = 0 AND licenses.date_end >= ?))) GROUP BY services.id ORDER BY lic_count DESC"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, (date_timestamp, date_timestamp, date_timestamp, date_timestamp,))

        licenses_count = db_cursor.fetchall()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if licenses_count is None or len(licenses_count) == 0:
        return EMPTY_STATE

    return licenses_count


def history_newlicenses_summary(db, date_timestamp, date_last_timestamp):
    if db is None:
        return ERROR_STATE

    db_query = "SELECT count(licenses.license_num) FROM licenses WHERE (\
    ((licenses.registration > 0 AND (SELECT orders.date FROM orders WHERE licenses.registration = orders.id) >= ? AND\
    (SELECT orders.date FROM orders WHERE licenses.registration = orders.id) < ?) OR\
    (licenses.registration = 0 AND licenses.date_start >= ? AND licenses.date_start < ?))) LIMIT 1"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, (date_last_timestamp, date_timestamp, date_last_timestamp, date_timestamp,))

        licenses_count = db_cursor.fetchone()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if licenses_count is None or len(licenses_count) == 0:
        return EMPTY_STATE

    return licenses_count[0]


def history_newlicenses_service(db, date_timestamp, date_last_timestamp):
    if db is None:
        return ERROR_STATE

    db_query = "SELECT services.id, services.service_name, count(licenses.license_num) AS lic_count FROM licenses JOIN\
    services ON licenses.service_name = services.id WHERE (\
    ((licenses.registration > 0 AND (SELECT orders.date FROM orders WHERE licenses.registration = orders.id) >= ?) AND\
    (SELECT orders.date FROM orders WHERE licenses.registration = orders.id) < ?) OR\
    (licenses.registration = 0 AND licenses.date_start >= ? AND licenses.date_start < ?))) GROUP BY services.id ORDER BY lic_count DESC"

    try:
        db_cursor = db.cursor()
        db_cursor.execute(db_query, (date_last_timestamp, date_timestamp, date_last_timestamp, date_timestamp,))

        licenses_count = db_cursor.fetchall()

    except sqlite3.DatabaseError as e:
        logging.critical("Database select error - {}".format(e))
        return ERROR_STATE

    if licenses_count is None or len(licenses_count) == 0:
        return EMPTY_STATE

    return licenses_count
