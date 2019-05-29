"""
Root of script to track NCSU Courses

Author:
    Sanveg Rane
"""
from src import course_fetcher as fetcher, email_handler as emailer
import logging as logger
import resources.log_config
from resources.config import Config as config
from apscheduler.schedulers.blocking import BlockingScheduler

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
    course_updates = fetcher.update_crs_details_and_get_updates()
    send_update_emails(course_updates)


def send_update_emails(courses_list):
    """
    Send the processed details of courses to the email addresses of each student
    Args:
        courses_list: List of course names to send emails
    """
    if len(courses_list) <= 0:
        logger.info("No courses to update")
        emailer.send_test_email()
        return

    logger.info("Sending update emails")
    courses_data = fetcher.get_course_data(courses_list, False)
    std_crs_map = fetcher.map_courses_to_emails(courses_data)

    # send mails
    emailer.send_courses_updates(courses_data, std_crs_map)
    emailer.send_test_email()


def send_status_emails():
    """
    Send status email to each subscribed student
    """
    logger.info("Sending status emails")
    courses_data = fetcher.get_course_data([], False)
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

    logger.info("Course update Job scheduled at every {} hours.".format(course_fetcher_hrs_interval))
    scheduler.start()


# main method to trigger script
if __name__ == '__main__':
    main()
