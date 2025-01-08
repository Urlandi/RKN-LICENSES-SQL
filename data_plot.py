# -*- coding: utf-8 -*-

import sqlite3
import logging

from datetime import datetime, timezone
from db_access import (date_first, history_licenses_summary, history_licenses_service,
                       history_newlicenses_summary, history_newlicenses_service,
                       history_holders_summary, history_holders_service,
                       history_synholders_summary, date_order_first, history_nextlicenses_summary, db_close)
from db_access import ERROR_STATE, SUCCESS_STATE

from matplotlib import pyplot, axes
from matplotlib.ticker import IndexLocator, AutoMinorLocator, NullLocator

from textwrap import wrap

from timestamp import dump_date
from rustat import ases


def plot_newlicenses(db):
    first_timestamp = date_first(db)
    # first_timestamp = datetime(year=2024, month=1, day=1, tzinfo=timezone.utc).timestamp()

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)

    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    date_ticks = []
    license_count = []
    newlicense_count = []

    while cur_date <= stop_date:
        prev_timestamp = int(prev_date.timestamp())
        cur_timestamp = int(cur_date.timestamp())

        date_ticks.append(prev_date.strftime("%Y %b"))

        license_count.append(history_licenses_summary(db, cur_timestamp))
        print("Year: {}, Month: {}, Timestamp: {} -> Licenses: {}".
              format(cur_date.year, cur_date.month, cur_timestamp, license_count[-1]))

        newlicense_count.append(history_newlicenses_summary(db, cur_timestamp, prev_timestamp))
        print("Year: {}, Month: {}, Timestamp: {} -> New licenses: {}".
              format(cur_date.year, cur_date.month, cur_timestamp, newlicense_count[-1]))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))

    xy = pyplot.axes()

    xy.xaxis.set_major_locator(IndexLocator(4, 0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    pyplot.xlim(0, len(date_ticks))
    pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")

    pyplot.ylabel("Количество лицензий")
    pyplot.title("Количество лицензий по месяцам")

    pyplot.plot(date_ticks, license_count, color="red")

    xy_newlicenses = xy.twinx()
    xy_newlicenses.bar(date_ticks, newlicense_count)
    xy_newlicenses.set_ylabel("Количество новых лицензий")

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')

    pyplot.savefig('newlicenses_d.png')
    #pyplot.show()
    return SUCCESS_STATE


def plot_ases(db):
    start_date = datetime.strptime(dump_date[0], '%Y-%m-%d').replace(tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    date_ticks = []
    holder_service_count = []
    ases_count = []

    while cur_date <= stop_date:
        prev_timestamp = int(prev_date.timestamp())
        cur_timestamp = int(cur_date.timestamp())

        date_ticks.append(prev_date.strftime("%Y %b"))

        holder_service_count.append(list(
            filter(lambda services: services[0] == 698,
                   history_holders_service(db, cur_timestamp)))[0][2])

        print("Year: {}, Month: {}, Timestamp: {} -> Holders: {}".
              format(cur_date.year, cur_date.month, cur_timestamp, holder_service_count[-1]))

        ases_count.append(ases.pop(0))
        print("Year: {}, Month: {}, Timestamp: {} -> ASes: {}".
              format(cur_date.year, cur_date.month, cur_timestamp, ases_count[-1]))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))

    xy = pyplot.axes()

    xy.xaxis.set_major_locator(IndexLocator(4, 0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    pyplot.xlim(0, len(date_ticks))
    pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")

    pyplot.ylabel("Количество автономных систем и владельцев лицензий")
    pyplot.title("Количество автономных систем и владельцев лицензий по месяцам")

    pyplot.plot(date_ticks, holder_service_count, label="Телематические услуги связи")
    pyplot.plot(date_ticks, ases_count, color="orange", label="Автономные системы")

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')

    pyplot.legend()
    pyplot.savefig('hld_ases_d.png')
    #pyplot.show()
    return SUCCESS_STATE


def plot_lic_services(db):
    first_timestamp = date_first(db)
    # first_timestamp = datetime(year=2024, month=1, day=1, tzinfo=timezone.utc).timestamp()

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)

    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    date_ticks = []
    license_service_count = []

    while cur_date <= stop_date:
        prev_timestamp = int(prev_date.timestamp())
        cur_timestamp = int(cur_date.timestamp())

        date_ticks.append(prev_date.strftime("%Y %b"))

        license_service_count.append(history_licenses_service(db, cur_timestamp))
        print("Year: {}, Month: {}, Timestamp: {} -> Licenses: {}".
              format(cur_date.year, cur_date.month, cur_timestamp, license_service_count[-1]))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))

    xy = pyplot.axes()

    xy.xaxis.set_major_locator(IndexLocator(4, 0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    pyplot.xlim(0, len(date_ticks))
    pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")

    pyplot.ylabel("Количество лицензий")
    pyplot.title("Количество лицензий по месяцам и видам деятельности")

    last_license_service = sorted(license_service_count[-1], key=lambda e: e[2], reverse=True)
    last_services_id, last_services_name, last_service_count = list(zip(*last_license_service))

    for service_id, service_name in list(zip(last_services_id, last_services_name)):
        license_service = []
        for cur_license_count in license_service_count:
            service_count = list(filter(lambda cur_license: service_id == cur_license[0], cur_license_count))
            license_service.append(service_count[0][2] if len(service_count) > 0 else 0)
        pyplot.plot(date_ticks, license_service, label='\n'.join(wrap(service_name, 60)))

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')

    pyplot.legend()
    pyplot.savefig('lic_services_d.png')
    #pyplot.show()
    return SUCCESS_STATE


def plot_hld_services(db):
    first_timestamp = date_first(db)
    # first_timestamp = datetime(year=2024, month=1, day=1, tzinfo=timezone.utc).timestamp()

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)

    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    date_ticks = []
    holder_service_count = []

    while cur_date <= stop_date:
        prev_timestamp = int(prev_date.timestamp())
        cur_timestamp = int(cur_date.timestamp())

        date_ticks.append(prev_date.strftime("%Y %b"))

        holder_service_count.append(history_holders_service(db, cur_timestamp))
        print("Year: {}, Month: {}, Timestamp: {} -> Licenses: {}".
              format(cur_date.year, cur_date.month, cur_timestamp, holder_service_count[-1]))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))

    xy = pyplot.axes()

    xy.xaxis.set_major_locator(IndexLocator(4, 0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    pyplot.xlim(0, len(date_ticks))
    pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")

    pyplot.ylabel("Количество владельцев лицензий")
    pyplot.title("Количество владельцев лицензий по месяцам и видам деятельности")

    last_license_service = sorted(holder_service_count[-1], key=lambda e: e[2], reverse=True)
    last_services_id, last_services_name, last_service_count = list(zip(*last_license_service))

    for service_id, service_name in list(zip(last_services_id, last_services_name)):
        license_service = []
        for cur_license_count in holder_service_count:
            service_count = list(filter(lambda cur_license: service_id == cur_license[0], cur_license_count))
            license_service.append(service_count[0][2] if len(service_count) > 0 else 0)
        pyplot.plot(date_ticks, license_service, label='\n'.join(wrap(service_name, 60)))

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')

    pyplot.legend()
    pyplot.savefig('hld_services_d.png')
    #pyplot.show()
    return SUCCESS_STATE


def plot_services(db):
    first_timestamp = date_first(db)
    # first_timestamp = datetime(year=2024, month=1, day=1, tzinfo=timezone.utc).timestamp()

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)

    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    date_ticks = []
    license_service_count = []

    while cur_date <= stop_date:
        cur_timestamp = int(cur_date.timestamp())

        date_ticks.append(prev_date.strftime("%Y %b"))
        license_service_count.append(len(history_holders_service(db, cur_timestamp)))

        print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Services: {}".
              format(cur_date.year, cur_date.month, cur_date.day,
                     cur_timestamp, license_service_count[-1]))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))

    xy = pyplot.axes()
    xy.fill_between(date_ticks, license_service_count)

    xy.xaxis.set_major_locator(IndexLocator(4, 0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    pyplot.xlim(0, len(date_ticks))
    pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")

    pyplot.ylabel("Количество видов деятельности")
    pyplot.title("Количество видов деятельности по месяцам")

    pyplot.plot(date_ticks, license_service_count)

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')


    pyplot.savefig('services_d.png')
    #pyplot.show()
    return SUCCESS_STATE


def plot_holders(db):
    first_timestamp = date_first(db)
    # first_timestamp = datetime(year=2024, month=1, day=1, tzinfo=timezone.utc).timestamp()

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)

    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    date_ticks = []
    holders_count = []

    while cur_date <= stop_date:
        cur_timestamp = int(cur_date.timestamp())

        date_ticks.append(prev_date.strftime("%Y %b"))
        holders_count.append(history_holders_summary(db, cur_timestamp))

        print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Holders: {}".
              format(cur_date.year, cur_date.month, cur_date.day,
                     cur_timestamp, holders_count[-1]))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))

    xy = pyplot.axes()
    xy.fill_between(date_ticks, holders_count)

    xy.xaxis.set_major_locator(IndexLocator(4, 0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    pyplot.xlim(0, len(date_ticks))
    pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")

    pyplot.ylabel("Количество владельцев лицензий")
    pyplot.title("Количество владельцев лицензий по месяцам")

    pyplot.plot(date_ticks, holders_count)

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')


    pyplot.savefig('holders_d.png')
    #pyplot.show()
    return SUCCESS_STATE


def plot_lastlicenses(db):
    first_timestamp = datetime(year=2021, month=1, day=1, tzinfo=timezone.utc).timestamp()

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)

    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    date_ticks = []
    newlicense_count = []

    while cur_date <= stop_date:
        prev_timestamp = int(prev_date.timestamp())
        cur_timestamp = int(cur_date.timestamp())

        date_ticks.append(prev_date.strftime("%Y %b"))
        newlicense_count.append(history_newlicenses_summary(db, cur_timestamp, prev_timestamp))

        print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> New licenses: {}".
              format(cur_date.year, cur_date.month, cur_date.day,
                     cur_timestamp, newlicense_count[-1]))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))

    xy = pyplot.axes()

    xy.xaxis.set_major_locator(IndexLocator(4, 0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    pyplot.xlim(0, len(date_ticks))
    pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")

    pyplot.ylabel("Количество новых лицензий")
    pyplot.title("Количество новых лицензий по месяцам")

    from numpy import arange

    x_bars = arange(12)
    pyplot.xlim(0, 12)
    xy.xaxis.set_minor_locator(NullLocator())
    width_bars = 0.3
    pyplot.bar(x_bars + 2.5 * width_bars, newlicense_count[-12::], width=width_bars, label="Новые лицензии 2024")
    pyplot.bar(x_bars + 1.5 * width_bars, newlicense_count[-24:-12], width=width_bars, label="Новые лицензии 2023")
    pyplot.bar(x_bars + width_bars / 2, newlicense_count[-36:-24], width=width_bars, label="Новые лицензии 2022")
    pyplot.xticks(x_bars, list(map(lambda d: d[4:], date_ticks[-12::])))

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')

    pyplot.legend()
    pyplot.savefig('lastlicenses_d.png')
    #pyplot.show()
    return SUCCESS_STATE


DONE = 0
STOP_AND_EXIT = 1
DB_NAME = "LicComm.sqlite3"


def main():
    exit_status_code = DONE

    db = None
    try:
        db = sqlite3.connect(DB_NAME)
    except sqlite3.DatabaseError as e:
        logging.critical("Database open error - {}".format(e))
        exit_status_code = STOP_AND_EXIT

    plot_lastlicenses(db)
    db_close(db)
    return exit_status_code


if __name__ == '__main__':
    exit(main())
