import datetime
import sched
import time

from kami_reports.report_bot import deliver_reports, report_bot_logger


def main():
    s = sched.scheduler(time.time, time.sleep)
    while True:
        try:
            now = datetime.datetime.now()

            if now.weekday() < 5 and now.hour == 21:
                deliver_reports()

            time.sleep(3600)

        except Exception as e:
            report_bot_logger.exception('An error occurred: ', e)


if __name__ == '__main__':
    main()
