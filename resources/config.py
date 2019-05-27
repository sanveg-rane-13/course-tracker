"""
Config properties - Add all config properties here and use the class in scripts
Author:
    Sanveg Rane
"""
import os


class Config:
    student_course_loc = "./resources/student-courses.json"
    # student_course_loc = "./resources/trail-student-courses.json"
    course_term_loc = "./resources/course-term.json"

    log_directory = "./tracker-app.log"

    search_URL = "https://www.acs.ncsu.edu/php/coursecat/search.php"
    course_avail_xpath = "//*[@class=\"table section-table table-striped table-condensed\"]/tr[#ROW#]/td[4]"
    course_loc_xpath = "//*[@class=\"table section-table table-striped table-condensed\"]/tr[#ROW#]/td[6]"
    course_name_xpath = "//*[@class=\"course\"]/h1/small"

    smtp_server = "smtp.gmail.com"
    port = 465
    sender_email = os.environ.get("SMTP_ID", "email")
    sender_pass = os.environ.get("SMTP_PASS", "password")
    email_header = "NCSU Courses status"

    owner = "Sanveg Rane"
    reg_url = "https://portalsp.acs.ncsu.edu"

    scheduler_hrs = os.environ.get("TRIGGER_HRS", "10")
