# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from db_access import (date_first, history_licenses_summary, history_licenses_service,
                       history_newlicenses_summary, history_newlicenses_service,
                       history_holders_summary, history_holders_service,
                       history_synholders_summary, date_order_first, history_nextlicenses_summary)
from db_access import ERROR_STATE, SUCCESS_STATE

from matplotlib import pyplot, axes
from matplotlib.ticker import IndexLocator, AutoMinorLocator, NullLocator

from textwrap import wrap

from timestamp import dump_date
from rustat import ases


def plot_licenses(db):
    # first_timestamp = date_first(db)
    first_timestamp = date_order_first(db)

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)

    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    # start_date = datetime.strptime(dump_date[0], '%Y-%m-%d').replace(tzinfo=timezone.utc)

    now_date = datetime.now(timezone.utc)
    if now_date.day < 10:
        stop_date = now_date.replace(day=1)
    else:
        stop_date = datetime(year=now_date.year + now_date.month // 12, month=now_date.month % 12 + 1, day=1,
                             tzinfo=timezone.utc)

    cur_date = start_date
    prev_date = start_date.replace(year=cur_date.year - (1 // cur_date.month), month=(cur_date.month - 2) % 12 + 1)

    license_count = []
    newlicense_count = []
    nextlicense_count = []
    holders_count = []
    synholders_count = []
    license_service_count = []
    date_ticks = []

    while cur_date <= stop_date:
        prev_timestamp = int(prev_date.timestamp())
        cur_timestamp = int(cur_date.timestamp())
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Licenses: {}".
        #      format(cur_date.year, cur_date.month, cur_date.day,
        #             cur_timestamp, history_licenses_summary(db, cur_timestamp)))
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Services: {}".
        #      format(cur_date.year, cur_date.month, cur_date.day,
        #             cur_timestamp, len(history_licenses_service(db, cur_timestamp))))
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> New Licenses: {}".
        #      format(cur_date.year, cur_date.month, cur_date.day,
        #             cur_timestamp, history_newlicenses_summary(db, cur_timestamp, prev_timestamp)))
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> New Services: {}".
        #     format(cur_date.year, cur_date.month, cur_date.day,
        #            cur_timestamp, len(history_newlicenses_service(db, cur_timestamp, prev_timestamp))))
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Holders: {}".
        #      format(cur_date.year, cur_date.month, cur_date.day,
        #             cur_timestamp, history_holders_summary(db, cur_timestamp)))
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Services: {}".
        #      format(cur_date.year, cur_date.month, cur_date.day,
        #             cur_timestamp, len(history_holders_service(db, cur_timestamp))))
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Sync Holders: {}".
        #      format(cur_date.year, cur_date.month, cur_date.day,
        #             cur_timestamp, history_synholders_summary(db, cur_timestamp, 735, 698)))
        print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Next Licenses: {}".
              format(cur_date.year, cur_date.month, cur_date.day,
                     cur_timestamp, history_nextlicenses_summary(db, cur_timestamp, prev_timestamp)))

        date_ticks.append(prev_date.strftime("%Y %b"))
        # license_count.append(history_licenses_summary(db,cur_timestamp))
        # newlicense_count.append(history_newlicenses_summary(db, cur_timestamp, prev_timestamp))
        # holders_count.append(history_holders_summary(db, cur_timestamp))
        # synholders_count.append(history_synholders_summary(db, cur_timestamp, 735, 698))
        nextlicense_count.append(history_nextlicenses_summary(db, cur_timestamp, prev_timestamp))

        # license_service_count.append(history_holders_service(db, cur_timestamp))
        # license_count.append(ases.pop(0))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    pyplot.figure(figsize=(20, 12))
    xy = pyplot.axes()
    # xy.fill_between(date_ticks, min(license_count), license_count)
    # xy.fill_between(date_ticks, min(newlicense_count), newlicense_count)
    # xy.fill_between(date_ticks, min(holders_count), holders_count)
    # xy.fill_between(date_ticks, min(synholders_count), synholders_count)
    xy.xaxis.set_major_locator(IndexLocator(4,0))
    xy.xaxis.set_minor_locator(AutoMinorLocator(4))
    xy.tick_params(axis='x', labelrotation=60)

    # pyplot.xlim(0, len(date_ticks))
    # pyplot.grid(linewidth=0.1)
    pyplot.xlabel("Дата")
    pyplot.ylabel("Количество новых лицензий на будущее")
    pyplot.title("Количество новых лицензий на будущее по месяцам")

    pyplot.bar(date_ticks, nextlicense_count, label="Новые лицензии на будущее")
    # xy_second = xy.twinx()
    # xy_second.plot(date_ticks, license_count, label="Всего лицензий", linewidth=0.5, color="red")
    # xy_second.set_ylabel("Всего лицензий")

    # last_license_service = sorted(license_service_count[-1], key=lambda e: e[2], reverse=True)
    # last_services_id, last_services_name, last_service_count = list(zip(*last_license_service))

    # for service_id, service_name in list(zip(last_services_id, last_services_name)):
    # for service_id, service_name in (last_license_service[0][0:2],):
    #    license_service = []
    #    for cur_license_count in license_service_count:
    #        service_count = list(filter(lambda cur_license: service_id == cur_license[0], cur_license_count))
    #        license_service.append(service_count[0][2] if len(service_count) > 0 else 0)
    #    pyplot.plot(date_ticks, license_service, label='\n'.join(wrap(service_name, 60)))
    # pyplot.plot(date_ticks, license_count, label="Автономные системы")

    # from numpy import arange

    # x_bars = arange(12)
    # pyplot.xlim(0, 12)
    # xy.xaxis.set_minor_locator(NullLocator())
    # width_bars = 0.3
    # pyplot.bar(x_bars+2.5 * width_bars, newlicense_count[-12::], width=width_bars, label="Новые лицензии 2023")
    # pyplot.bar(x_bars+1.5 * width_bars, newlicense_count[-24:-12], width=width_bars, label="Новые лицензии 2022")
    # pyplot.bar(x_bars+width_bars/2, newlicense_count[-36:-24], width=width_bars, label="Новые лицензии 2021")
    # pyplot.xticks(x_bars, list(map(lambda d: d[4:], date_ticks[-12::])))

    for t in xy.get_xticklabels():
        t.set_horizontalalignment('right')

    # pyplot.legend()
    pyplot.savefig('nextlicenses.png')
    pyplot.show()
    return SUCCESS_STATE
