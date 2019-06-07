"""
Config properties - Add all config properties here and use the class in scripts
Author:
    Sanveg Rane
"""
import os


class Config:
    # CONFIG FILES
    course_file_name = os.environ.get("COURSES_FILE", "trail-student-courses.json")
    student_course_loc = "./resources/" + course_file_name
    course_term_loc = "./resources/course-term.json"

    temp_loc = "./tmp/"
    course_file_name = "courses_data.json"
    studnt_file_name = "student_data.json"

    # LOGGING
    log_directory = "./tracker-app.log"

    # NCSU STATUS EXTRACTION
    search_URL = "https://www.acs.ncsu.edu/php/coursecat/search.php"
    reg_url = "https://portalsp.acs.ncsu.edu"
    course_avail_xpath = "//*[@class=\"table section-table table-striped table-condensed\"]/tr[#ROW#]/td[4]"
    course_loc_xpath = "//*[@class=\"table section-table table-striped table-condensed\"]/tr[#ROW#]/td[6]"
    course_name_xpath = "//*[@class=\"course\"]/h1/small"

    # EMAIL SENDER
    smtp_server = "smtp.gmail.com"
    port = 587

    sender_email = os.environ.get("SMTP_ID", "email")
    sender_pass = os.environ.get("SMTP_PASS", "password")
    email_header = "NCSU Courses status"
    email_update_header = "NCSU Courses updates"
    owner = "Sanveg Rane"
    test_receiver = "srsanrocks1@gmail.com"

    # SCHEDULER
    cr_update_schdlr_hrs = os.environ.get("CRS_UPDATE_TRIGGER_HRS", "2")
