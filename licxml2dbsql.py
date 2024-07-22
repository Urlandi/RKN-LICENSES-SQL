# -*- coding: utf-8 -*-

import sqlite3
import xml.etree.ElementTree as XMLTree
import logging
from datetime import datetime, timezone

from db_access import db_close, add_order, add_holder, add_license, add_service, add_ownership, add_lic_status_name
from db_access import EMPTY_STATE

import sys
import fileinput

import cProfile

DONE = 0
STOP_AND_EXIT = 1

USAGE_MSG = """
Convert open RKN data license XML preformatted file to SQLite DB 
Usage:
    licxml2dbsql.py <file> 
    or 
    cat <file> | licxml2dbsql.py  
"""

DB_NAME = "LicComm.sqlite3"

def main():

    input_flow_name = "-"

    args = sys.argv[1:]
    if len(args) > 0:
        input_flow_name = args[-1]

    exit_status_code = DONE

    db = None
    licenses = None
    try:
        db = sqlite3.connect(DB_NAME)
    except sqlite3.DatabaseError as e:
        logging.critical("Database open error - {}".format(e))
        exit_status_code = STOP_AND_EXIT

    if db is not None:
        try:
            for record_line in fileinput.input(input_flow_name, encoding="utf-8"):
                records = XMLTree.fromstring(record_line)
                lic_record = {'name': None,
                              'ownership': None,
                              'name_short': None,
                              'name_brand': None,
                              'addr_legal': None,
                              'inn': None,
                              'ogrn': None,
                              'licence_num': None,
                              'licence_num_old': None,
                              'lic_status_name': None,
                              'date_start': None,
                              'date_end': None,
                              'date_service_start': None,
                              'service_name': None,
                              'territory': None,
                              'registration': None,
                              'reregistration': None,
                              'prolongation': None,
                              'suspension_resume': None,
                              'termination': None}
                for lic_data in records:
                    if len(lic_data) == 0:
                        if lic_data.text is None:
                            continue
                        lic_record[lic_data.tag] = " ".join(lic_data.text.split())
                        if len(lic_record[lic_data.tag]) == 0:
                            lic_record[lic_data.tag] = None
                        continue
                    else:
                        lic_record[lic_data.tag] = {'num': None, 'date': None}
                        lic_record[lic_data.tag].update(dict(map(lambda order: (order.tag, order.text), lic_data)))

                lic_status_name = add_lic_status_name(db, lic_record['lic_status_name'])

                service_name = add_service(db, lic_record['service_name'])

                ownership = add_ownership(db, lic_record['ownership'])

                tz_cur = timezone.utc
                date_fmt = '%Y-%m-%d'

                registration = EMPTY_STATE
                if lic_record['registration'] is not None:
                    registration = add_order(db, lic_record['registration']['num'],
                                             int(datetime.strptime(
                                                 lic_record['registration']['date'], date_fmt).
                                                 replace(tzinfo=tz_cur).timestamp()))

                reregistration = EMPTY_STATE
                if lic_record['reregistration'] is not None:
                    reregistration = add_order(db, lic_record['reregistration']['num'],
                                               int(datetime.strptime(
                                                   lic_record['reregistration']['date'], date_fmt).
                                                   replace(tzinfo=tz_cur).timestamp()))

                prolongation = EMPTY_STATE
                if lic_record['prolongation'] is not None:
                    prolongation = add_order(db, lic_record['prolongation']['num'],
                                             int(datetime.strptime(
                                                 lic_record['prolongation']['date'], date_fmt).
                                                 replace(tzinfo=tz_cur).timestamp()))

                suspend_resume = EMPTY_STATE
                if lic_record['suspension_resume'] is not None:
                    suspend_resume = add_order(db, lic_record['suspension_resume']['num'],
                                               int(datetime.strptime(
                                                   lic_record['suspension_resume']['date'], date_fmt).
                                                   replace(tzinfo=tz_cur).timestamp()))

                termination = EMPTY_STATE
                if lic_record['termination'] is not None:
                    termination = add_order(db, lic_record['termination']['num'],
                                            int(datetime.strptime(
                                                lic_record['termination']['date'], date_fmt).
                                                replace(tzinfo=tz_cur).timestamp()))

                holder = add_holder(db, lic_record['name'], ownership, lic_record['name_short'],
                                    lic_record['name_brand'],
                                    lic_record['addr_legal'], lic_record['inn'], lic_record['ogrn'])

                date_start = None
                if lic_record['date_start'] is not None:
                    date_start = int(datetime.strptime(lic_record['date_start'], date_fmt).
                                     replace(tzinfo=tz_cur).timestamp())

                date_end = None
                if lic_record['date_end'] is not None:
                    date_end = int(datetime.strptime(lic_record['date_end'], date_fmt).
                                   replace(tzinfo=tz_cur).timestamp())

                date_service_start = None
                if lic_record['date_service_start'] is not None:
                    date_service_start = int(datetime.strptime(lic_record['date_service_start'], date_fmt).
                                             replace(tzinfo=tz_cur).timestamp())

                add_license(db, holder,
                            lic_record['licence_num'],
                            lic_record['licence_num_old'],
                            lic_status_name,
                            date_start, date_end, date_service_start,
                            service_name,
                            lic_record['territory'],
                            registration, reregistration, prolongation, suspend_resume, termination)
        except IOError:
            logging.critical("Input read error in '{}'".format(input_flow_name))
            exit_status_code = STOP_AND_EXIT
        except XMLTree.ParseError as e:
            logging.critical("XML parser error - {}".format(e))
            logging.critical("{}: {}".format(fileinput.filelineno(), record_line))
            exit_status_code = STOP_AND_EXIT

    db_close(db)
    return exit_status_code
    
    
if __name__ == '__main__':
    cProfile.run("main()")
    exit(0)
    