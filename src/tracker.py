"""
Root of script to track NCSU Courses

Author:
    Sanveg Rane
"""
import logging as logger
import resources.log_config  # added to setup logging config

from apscheduler.schedulers.blocking import BlockingScheduler
from src import course_fetcher as fetcher, email_handler as emailer
from resources.config import Config as config

# initializing scheduler
scheduler = BlockingScheduler()
course_fetcher_hrs_interval = int(config.cr_update_schdlr_hrs)


def initialize_course_data():
    """
    Read course data initially and save in temp file
    Executed on start up
    """
    logger.info("Initializing course data")
    fetcher.init_courses_data()


@scheduler.scheduled_job('interval', hours=course_fetcher_hrs_interval)
def track_course_status_and_update_students():
    """
    Scheduled task to perform following functions:
        - Update the statuses of courses
        - Check if any course updated
        - Send notifications for each updated course
    """
    logger.info("Course-updater job triggered!")
    all_courses, course_updates = fetcher.update_crs_details_and_get_updates()
    send_updates(all_courses, course_updates)


def send_updates(all_courses, course_updates):
    """
    Send the processed details of courses to the email addresses of each student
    Args:
        all_courses: All courses data to send test mail to admin
        course_updates: List of course names to send emails
    """
    if len(course_updates) <= 0:
        logger.info("No courses to update")
        emailer.send_test_email(all_courses)
        return

    courses_data = fetcher.get_course_data(course_updates, False)

    # send mails
    logger.info("Sending update emails")
    std_crs_email_map = fetcher.map_courses_to_emails(courses_data)
    emailer.send_courses_updates(courses_data, std_crs_email_map)

    emailer.send_test_email(all_courses)


def send_status_emails():
    """
    Send status email to each subscribed student
    """
    logger.info("Sending status emails")
    courses_data = fetcher.get_course_data([], True)
    std_crs_map = fetcher.map_courses_to_emails(courses_data)
    emailer.send_courses_updates(courses_data, std_crs_map)


def main():
    """
    Starting to schedule jobs
        - Load course data and student data in json files
        - Schedule jobs
    """
    logger.info("Starting Script")
    initialize_course_data()
    emailer.init()

    logger.info("Course update Job scheduled at every {} hours.".format(course_fetcher_hrs_interval))
    scheduler.start()


def test_flow():
    logger.info("Starting Test Script")
    initialize_course_data()
    emailer.init()
    track_course_status_and_update_students()


# main method to trigger script
if __name__ == '__main__':
    main()
    # test_flow()
