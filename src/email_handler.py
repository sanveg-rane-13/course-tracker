"""
Module to send email

Author:
    Sanveg Rane
"""
import logging as logger

from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from httplib2 import Http
from resources.config import Config as Config
from oauth2client import file, client, tools

SCOPE = 'https://www.googleapis.com/auth/gmail.compose'  # Allows sending only, not reading


def init():
    """
    Check if email sender is initialized. If not initialize sender
    """
    init_gmail_api_new()


def init_gmail_api_new():
    """
    Init the service to send emails
    """
    global service
    global email_sender

    email_sender = Config.sender_email
    logger.info("Attempting to initiate gmail api")

    try:
        store = file.Storage('credentials.json')
        creds = store.get()

        if not creds or creds.invalid:
            logger.debug("Re-fetching credentials")
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPE)
            creds = tools.run_flow(flow, store)

        service = build('gmail', 'v1', http=creds.authorize(Http()))
        logger.info("Successfully initialized gmail api")
    except Exception as error:
        logger.error("Error initializing gmail api: {}".format(error))


def init_sender_email_details():
    """
    Initialize the details of email sender globally
    """
    global details
    details = {
        'server': Config.smtp_server,
        'port': Config.port,
        'sender_email': Config.sender_email,
        'sender_pass': Config.sender_pass
    }


def send_courses_updates(courses, student_crs_map):
    """
    Send emails of updated courses
    Args:
        courses: Details of all updated courses
        student_crs_map: List of courses subscribed by each student
    """
    for email_id, updated_courses in student_crs_map.items():
        send_update_email(email_id, updated_courses, courses)


def send_update_email(receiver_email, courses_list, courses_data):
    if service is None:
        logger.error("Error Sending email: Gmail API not configured.")
        return

    email_body = create_update_message_body(receiver_email, courses_list, courses_data)
    message = create_email(receiver_email, Config.email_update_header, email_body)

    try:
        sent_message = (service.users()
                        .messages()
                        .send(userId=email_sender, body=message)
                        .execute())
        logger.debug("Message sent successfully: {}".format(sent_message['id']))
    except Exception as error:
        logger.error("Error sending email: {}".format(error))


def create_update_message_body(receiver_email, course_names_list, courses_data):
    try:
        receiver = courses_data[course_names_list[0]]["stud_email"][receiver_email]
    except Exception as error:
        receiver = "Course Tracker User"
        logger.error("Error fetching receiver name: {}".format(error))

    msg_line_one = "Hello " + receiver + "," + "\n\n"
    msg_line_two = "Following courses statuses have been updated in website: \n\n"
    message = msg_line_one + msg_line_two

    # create the statuses message
    for cr_name in course_names_list:
        cr_detail = courses_data[cr_name]
        if 'invalid' not in cr_detail:
            msg_course_line = cr_name + ":\n" \
                              + "\tname = " + cr_detail['name'] + ",\n"
            for index in range(len(cr_detail['status'])):
                msg_course_line += "\tlocation = " + cr_detail['location'][index] \
                                   + "\t# " \
                                   + "availability = " + cr_detail['status'][index] + "\n"

            message += msg_course_line + "\n"

    msg_portal_line = "\nRegister courses at: " + Config.reg_url
    msg_last_line = "\n\nThank you."
    message += msg_portal_line + msg_last_line

    email_body = "{}".format(message)
    return email_body


def send_test_email(course_updates):
    """
    Send test email to owner to verify process
    Args:
        course_updates: Data saved in json to be sent to admin
    """
    if service is None:
        logger.error("Error Sending email: Gmail API not configured.")

    # adding status of each course to be sent to admin
    courses_body = ""

    if course_updates is not None:

        for cr_name, cr_detail in course_updates.items():
            course_det_text = cr_name + " - " + cr_detail['name'] + ": \n"

            for index in range(len(cr_detail['status'])):
                course_det_text += "\tlocation = " + cr_detail['location'][index] \
                                   + "\t# " \
                                   + "availability = " + cr_detail['status'][index] + "\n"

            courses_body += course_det_text

    # creating test body
    test_body = "Status updated job executed successfully!"
    test_body = test_body + "\n\n" + courses_body
    email_body = "{}".format(test_body)

    message = create_email(Config.test_receiver, Config.email_update_header, email_body)

    try:
        sent_message = (service.users()
                        .messages()
                        .send(userId=email_sender, body=message)
                        .execute())
        logger.debug("Message sent successfully: {}".format(sent_message['id']))
    except Exception as error:
        logger.error("Error sending email: {}".format(error))


def create_email(receiver_email, subject, message_body):
    message = MIMEText(message_body)
    message['to'] = receiver_email
    message['from'] = Config.owner
    message['subject'] = subject

    encoded_message = urlsafe_b64encode(message.as_bytes())
    return {'raw': encoded_message.decode()}
