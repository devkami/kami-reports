import datetime
import time

from kami_reports.report_bot import deliver_reports, report_bot_logger


def main():
    while True:
        try:
            now = datetime.datetime.now()
            report_bot_logger.info(
                f"Última leitura: {now.strftime('%d-%m-%Y %H:%M:%s')}"
            )
            if now.weekday() < 5 and now.hour == 8:
                deliver_reports()
            time.sleep(3600)
        except Exception as e:
            report_bot_logger.exception('An error occurred: ', e)


if __name__ == '__main__':
    main()
