from os import path

from kami_reports.constant import ROOT_DIR
from kami_reports.report_bot import (
    create_gdrive_folders,
    deliver_board_reports,
    deliver_reports,
    get_contacts_from_json,
)


def main():
    current_folders_id = create_gdrive_folders()
    contacts = get_contacts_from_json(
        path.join(ROOT_DIR, 'messages/contacts.json')
    )
    deliver_board_reports(current_folders_id, contacts)


if __name__ == '__main__':
    main()
