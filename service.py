import datetime
import sched
import time

from kami_reports.report_bot import deliver_reports


def main():
    s = sched.scheduler(time.time, time.sleep)

    while True:
        try:
            now = datetime.datetime.now()

            if now.weekday() < 5 and now.hour == 6:
                deliver_reports()

            time.sleep(3600)

        except Exception as e:
            print(f'An error occurred: {str(e)}')


if __name__ == '__main__':
    main()
