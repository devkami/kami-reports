from report_bot import deliver_account_reports, deliver_comercial_reports, deliver_board_reports, delete_old_files, create_gdrive_folders, get_contacts_from_json, report_bot_logger
import threading as th
import time
from constant import CURRENT_WEEKDAY, COMERCIAL_WEEK
from datetime import datetime

def delivery_reports():
    while True:
        current_time = datetime.now()
        if current_time.strftime("%I:%M %p") == '06:21 AM' and CURRENT_WEEKDAY in COMERCIAL_WEEK:
            current_folders_id = create_gdrive_folders()
            contacts = get_contacts_from_json('messages/contacts.json')   
            delete_old_files('data/out')                   
            deliver_board_reports(current_folders_id, contacts)
            deliver_comercial_reports(current_folders_id, contacts)
            deliver_account_reports(current_folders_id, contacts)
        time.sleep(60)

def main_thread():
    report_bot_logger.info('Start Execution.')
    while True:        
        time.sleep(1)

def run_bot():
    th_update_globals = th.Thread(target=delivery_reports, daemon=True)
    th_main_thread = th.Thread(target=main_thread)
    th_update_globals.start()
    th_main_thread.start()

if __name__ == '__main__':
    run_bot()