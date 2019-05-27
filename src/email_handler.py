"""
Module to send email

Author:
    Sanveg Rane
"""
import smtplib
import ssl
import logging as logger
from resources.config import Config as config


def send_details_to_students(student_details):
    sender = init_and_get_email_sender()

    if sender is not None:
        for email_address, details in student_details.items():
            send_email(email_address, details, sender)


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
        sender.sendmail(config.sender_email, receiver_email, email_body)
        logger.info("Sent Email to {} successfully".format(receiver_email))
    except Exception as error:
        logger.error("Error sending email", error)


def get_email_sender_details():
    details = {
        'server': config.smtp_server,
        'port': config.port,
        'sender_email': config.sender_email,
        'sender_pass': config.sender_pass
    }

    return details


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
