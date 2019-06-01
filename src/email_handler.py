"""
Module to send email

Author:
    Sanveg Rane
"""
import smtplib
import ssl
import logging as logger
from resources.config import Config as config


# def send_details_to_students(courses_details):
#     sender = init_and_get_email_sender()

# if sender is not None:
#     for email_address, details in courses_list:
#         send_email(email_address, details, sender)


def send_courses_updates(courses, student_crs_map):
    """
    Send emails of updated courses
    Args:
        courses: Details of all updated courses
        student_crs_map: List of courses subscribed by each student
    """
    sender = init_and_get_email_sender()
    if sender is not None:
        for email_id, updated_courses in student_crs_map.items():
            send_update_email(email_id, updated_courses, courses, sender)
        sender.quit()


def send_courses_statuses(courses, student_crs_map):
    """
    Send emails with status of all courses
    Args:
        courses: Details of all updated courses
        student_crs_map: List of courses subscribed by each student
    """
    sender = init_and_get_email_sender()


def init_and_get_email_sender():
    """
    Create SMTP server and login
    Returns:
        Email sender
    """
    email_details = get_email_sender_details()
    logger.info("Initializing SMTP sender using: " + email_details['sender_email'])

    try:
        server = smtplib.SMTP(email_details['server'], email_details['port'])
        server.ehlo()

        context = ssl.create_default_context()
        server.starttls(context=context)

        server.login(email_details['sender_email'], email_details['sender_pass'])
        logger.debug("Successfully created SMTP sender")
        return server

    except Exception as error:
        logger.error("Error creating mail server", error)


def get_email_sender_details():
    details = {
        'server': config.smtp_server,
        'port': config.port,
        'sender_email': config.sender_email,
        'sender_pass': config.sender_pass
    }

    return details


def send_update_email(receiver_email, courses_list, courses_data, sender):
    email_body = create_update_message_body(receiver_email, courses_list, courses_data)

    if sender is None:
        logger.error("Error sending update email: Sender not configured")
        return

    try:
        sender.sendmail(config.sender_email, receiver_email, email_body)
        logger.info("Sent Email to {} successfully".format(receiver_email))
    except Exception as error:
        logger.error("Error sending email", error)


def create_update_message_body(receiver_email, courses_list, courses_data):
    subject = config.email_update_header
    sender = config.owner

    try:
        receiver = courses_data[courses_list[0]]["stud_info"][receiver_email]
    except Exception as error:
        receiver = "Course Tracker User"
        logger.error("Error fetching receiver name")

    msg_line_one = "Hello " + receiver + "," + "\n\n"
    msg_line_two = "Following courses statuses have been updated in website: \n\n"
    message = msg_line_one + msg_line_two

    # create the statuses message
    for cr_name in courses_list:
        cr_detail = courses_data[cr_name]
        if 'invalid' not in cr_detail:
            msg_course_line = cr_name + ":\n" \
                              + "\tname = " + cr_detail['name'] + ",\n";
            for index in range(len(cr_detail['status'])):
                msg_course_line += "\tlocation = " + cr_detail['location'][index] \
                                   + "\t# " \
                                   + "availability = " + cr_detail['status'][index] + "\n"

            message += msg_course_line + "\n"

    msg_portal_line = "\nRegister courses at: " + config.reg_url
    msg_last_line = "\n\nThank you."
    message += msg_portal_line + msg_last_line

    email_body = "From: {}\nSubject: {}\n\n{}".format(sender, subject, message)
    return email_body


def send_email(receiver_email, receiver_dets, sender):
    """
    Send email with details
    Args:
        receiver_email: emailId of receiver
        receiver_dets: Details of all the courses registered and their statuses
        sender: Logged in SMTP server
    """
    email_body = create_message_body(receiver_dets)
    try:
        # sender.sendmail(config.sender_email, receiver_email, email_body)
        logger.info("Sent Email to {} successfully".format(receiver_email))
    except Exception as error:
        logger.error("Error sending email", error)


def create_message_body(receiver_dets):
    """
    Iterate over the course details fetched and create message string to send
    Args:
        receiver_dets: JSON containing details of the student and registered courses

    Returns:
        String containing headers and body for email
    """
    subject = config.email_header
    sender = config.owner

    msg_line_one = "Hello " + receiver_dets['name'] + ",\n\n"
    msg_line_two = "Please find your course statuses on NCSU website: \n\n"
    message = msg_line_one + msg_line_two

    for cr_name, cr_detail in receiver_dets['courses'].items():
        if 'invalid' not in cr_detail:
            msg_course_line = cr_name + ":\n" \
                              + "\tname = " + cr_detail['name'] + ",\n" \
                              + "\tavailability = " + cr_detail['status'][0] + ",\n" \
                              + "\tlocation = " + cr_detail['location'][0] + "\n\n"

            message += msg_course_line

    msg_portal_line = "\nRegister courses at: " + config.reg_url
    msg_last_line = "\n\nThank you."

    message += msg_portal_line + msg_last_line

    email_body = "From: {}\nSubject: {}\n\n{}".format(sender, subject, message)
    return email_body


def send_test_email():
    """
    Send test email to owner to verify process
    """
    sender = init_and_get_email_sender()
    if sender is None:
        logger.error("Error sending test email: Sender not configured")
        return

    receiver = config.test_receiver
    owner = config.owner

    test_header = "Update Job Execution"
    test_body = "Test executed successfully"
    email_body = "From: {}\nSubject: {}\n\n{}".format(owner, test_header, test_body)

    try:
        sender.sendmail(config.sender_email, receiver, email_body)
        logger.info("Sent Update job Test Email to {} successfully".format(receiver))
    except Exception as error:
        logger.error("Error sending job update email", error)
