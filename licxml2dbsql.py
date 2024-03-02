# -*- coding: utf-8 -*-

import sqlite3
import xml.etree.ElementTree as XMLTree
import logging
from datetime import datetime

from db_access import db_close, add_order, add_holder, add_license, add_service, add_ownership, add_lic_status_name
from db_access import EMPTY_STATE


DONE = 0
STOP_AND_EXIT = 1

XML_NAME = "data-20240302T0000-structure-20220708T0000.xml"
# XML_NAME = "datatext.xml"
DB_NAME = "LicComm.sqlite3"


def main():
    exit_status_code = DONE

    db = None
    licenses = None
    try:
        db = sqlite3.connect(DB_NAME)
        licenses = XMLTree.parse(XML_NAME).getroot()
    except sqlite3.DatabaseError as e:
        logging.critical("Database open error - {}".format(e))
        exit_status_code = STOP_AND_EXIT
    except XMLTree.ParseError as e:
        logging.critical("XML parser error - {}".format(e))     
        exit_status_code = STOP_AND_EXIT

    if db is not None and licenses is not None:
        for record in licenses:
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
            for lic_data in record:
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

            registration = EMPTY_STATE
            if lic_record['registration'] is not None:
                registration = add_order(db, lic_record['registration']['num'],
                                         int(datetime.strptime(
                                             lic_record['registration']['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()))
            reregistration = EMPTY_STATE
            if lic_record['reregistration'] is not None:
                reregistration = add_order(db, lic_record['reregistration']['num'],
                                           int(datetime.strptime(
                                               lic_record['reregistration']['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()))
            prolongation = EMPTY_STATE
            if lic_record['prolongation'] is not None:
                prolongation = add_order(db, lic_record['prolongation']['num'],
                                         int(datetime.strptime(
                                             lic_record['prolongation']['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()))
            suspend_resume = EMPTY_STATE
            if lic_record['suspension_resume'] is not None:
                suspend_resume = add_order(db, lic_record['suspension_resume']['num'],
                                           int(datetime.strptime(
                                               lic_record['suspension_resume']['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()))
            termination = EMPTY_STATE
            if lic_record['termination'] is not None:
                termination = add_order(db, lic_record['termination']['num'],
                                        int(datetime.strptime(
                                            lic_record['termination']['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()))

            holder = add_holder(db, lic_record['name'], ownership, lic_record['name_short'], lic_record['name_brand'],
                                lic_record['addr_legal'], lic_record['inn'], lic_record['ogrn'])

            date_start = None
            if lic_record['date_start'] is not None:
                date_start = int(datetime.strptime(lic_record['date_start'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())

            date_end = None
            if lic_record['date_end'] is not None:
                date_end = int(datetime.strptime(lic_record['date_end'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())

            date_service_start = None
            if lic_record['date_service_start'] is not None:
                date_service_start = int(datetime.strptime(lic_record['date_service_start'], '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())

            add_license(db, holder,
                        lic_record['licence_num'],
                        lic_record['licence_num_old'],
                        lic_status_name,
                        date_start, date_end, date_service_start,
                        service_name,
                        lic_record['territory'],
                        registration, reregistration, prolongation, suspend_resume, termination)

    db_close(db)
    return exit_status_code
    
    
if __name__ == '__main__':
    exit(main())
    