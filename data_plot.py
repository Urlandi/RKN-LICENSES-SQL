# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from db_access import date_first, history_licenses_summary, history_licenses_service
from db_access import ERROR_STATE, SUCCESS_STATE


def plot_licenses(db):
    first_timestamp = date_first(db)

    if first_timestamp is None:
        return ERROR_STATE

    first_date = datetime.fromtimestamp(first_timestamp, timezone.utc)
    start_date = datetime(year=first_date.year + first_date.month // 12, month=first_date.month % 12 + 1, day=1,
                          tzinfo=timezone.utc)

    stop_date = datetime.now(timezone.utc).replace(day=1)

    prev_date = 0
    cur_date = start_date
    while cur_date <= stop_date:
        cur_timestamp = int(cur_date.timestamp())
        # print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Licenses: {}".
        #      format(cur_date.year, cur_date.month, cur_date.day,
        #             cur_timestamp, history_licenses_summary(db, cur_timestamp)))
        print("Year: {}, Month: {}, Day: {}, Timestamp: {} -> Services: {}".
              format(cur_date.year, cur_date.month, cur_date.day,
                     cur_timestamp, len(history_licenses_service(db, cur_timestamp))))

        prev_date = cur_date
        cur_date = cur_date.replace(year=cur_date.year + cur_date.month // 12, month=cur_date.month % 12 + 1)

    return SUCCESS_STATE
