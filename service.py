import datetime
import sched
import time
from os import path

from kami_reports.messages.messages import get_contacts_from_json
from kami_reports.report_bot import (
    SOURCE_DIR,
    deliver_reports,
    report_bot_logger,
    send_message_by_group,
)


def main():
    s = sched.scheduler(time.time, time.sleep)
    while True:
        try:
            now = datetime.datetime.now()

            if now.weekday() < 5 and now.hour == 4:
                deliver_reports()

            if now.day == 14:
                contacts = get_contacts_from_json(
                    path.join(SOURCE_DIR, 'messages/contacts.json')
                )
                send_message_by_group(
                    template_name='geral',
                    group='test',
                    message_dict={
                        'subject': 'KAMI Report Bot | Atualizações da Versão: 0.5.0'
                    },
                    contacts=contacts,
                )

            time.sleep(3600)

        except Exception as e:
            report_bot_logger.exception('An error occurred: ', e)


if __name__ == '__main__':
    main()
