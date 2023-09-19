import time
from os import path

import schedule

from kami_reports.constant import ROOT_DIR
from kami_reports.report_bot import (
    create_gdrive_folders,
    deliver_account_reports,
    deliver_board_reports,
    deliver_comercial_reports,
    get_contacts_from_json,
)


def main():
    current_folders_id = create_gdrive_folders()
    contacts = get_contacts_from_json(
        path.join(ROOT_DIR, 'messages/contacts.json')
    )
    schedule.every().monday.at('09:00').do(
        deliver_account_reports, current_folders_id, contacts
    )
    schedule.every().tuesday.at('09:00').do(
        deliver_account_reports, current_folders_id, contacts
    )
    schedule.every().wednesday.at('09:00').do(
        deliver_account_reports, current_folders_id, contacts
    )
    schedule.every().thursday.at('09:00').do(
        deliver_account_reports, current_folders_id, contacts
    )
    schedule.every().friday.at('09:00').do(
        deliver_account_reports, current_folders_id, contacts
    )
    schedule.every().monday.at('08:00').do(
        deliver_comercial_reports, current_folders_id, contacts
    )
    schedule.every().tuesday.at('08:00').do(
        deliver_comercial_reports, current_folders_id, contacts
    )
    schedule.every().wednesday.at('08:00').do(
        deliver_comercial_reports, current_folders_id, contacts
    )
    schedule.every().thursday.at('08:00').do(
        deliver_comercial_reports, current_folders_id, contacts
    )
    schedule.every().friday.at('08:00').do(
        deliver_comercial_reports, current_folders_id, contacts
    )
    schedule.every().monday.at('07:00').do(
        deliver_board_reports, current_folders_id, contacts
    )
    schedule.every().tuesday.at('07:00').do(
        deliver_board_reports, current_folders_id, contacts
    )
    schedule.every().wednesday.at('07:00').do(
        deliver_board_reports, current_folders_id, contacts
    )
    schedule.every().thursday.at('07:00').do(
        deliver_board_reports, current_folders_id, contacts
    )
    schedule.every().friday.at('07:00').do(
        deliver_board_reports, current_folders_id, contacts
    )

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
