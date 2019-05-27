"""
The module performs:
 1) Read JSON data from files
 2) Process and order courses data
 3) Fetch statuses for each course
 4) Map details to each student

Enter the student details and required courses to track in the student-courses.json file
The json will be moved to a no sql DB if required to load

Author:
    Sanveg Rane
"""
import json
import requests as req
import logging as logger
from lxml import html
from resources.config import Config as config


def get_courses():
    """
    The method performs:
        Parses the JSON of students opting courses and creates list
        Fetches data for each course
        Updates the course as per availability

    Returns:
        List of courses with their statuses
    """
    student_courses = read_json(config.student_course_loc)
    courses_details = parse_course_data(student_courses)
    update_course_status(courses_details)

    return courses_details


def parse_course_data(student_courses):
    """
    Parse the JSON config to create list of subjects to fetch
    Args:
        student_courses: JSON extracted from resources

    Returns:
        List if student courses to be fetched for status
    """
    course_details_map = {}
    course_term_map = read_json(config.course_term_loc)

    for course_data in student_courses.values():
        for cr_num, cr_term in course_data["courses"].items():
            c_subject = course_data["subject"]
            course_name = get_course_name(c_subject, cr_num, cr_term)
            if course_name not in course_details_map:
                #  adding course details in map to easily iterate over
                course_detail = {
                    'subject': c_subject,
                    'num': cr_num,
                    'term': course_term_map[cr_term]
                }
                course_details_map[course_name] = course_detail

    return course_details_map


def update_course_status(courses):
    """
    For each course fetch details and adds to the course
    If data for course is not available, it sets flag invalid as True
    Args:
        courses: list of courses to query data for
    """
    for detail in courses.values():
        subject_data = get_search_details_page(detail)
        if subject_data is not None:
            fetch_status_from_response(detail, subject_data)


def get_search_details_page(course):
    """
    Fetch course details HTML from NCSU search script
    Args:
        course: Details of the course to make post request

    Returns:
        HTML page retrieved from the endpoint converted from string

    """
    course_name = course["subject"] + "-" + course["num"]
    logger.info("Searching status for: " + course_name)

    search_url = config.search_URL
    params = {
        'subject': course["subject"],
        'course-number': course["num"],
        'term': course["term"],
        'course-inequality': '=',
        'to': '1',
        'table-only': '0'
    }

    resp = req.post(search_url, data=params)

    if resp:
        data = resp.json()
        if data:
            # return the HTML retrieved from the endpoint for the course
            logger.debug("Fetched Data for course: " + course_name)
            return html.fromstring(data['html'])
    else:
        logger.error("Error fetching data for course: " + course_name)


def fetch_status_from_response(course_detail, html_page):
    """
    Parse the HTML and use xpath to fetch course status and location of course
    Args:
        course_detail: Details of the course
        html_page: Extracted page from search script result

    Returns:
        Course detail with course status and course location
    """
    row_number = 1
    course_invalid = False
    course_detail['location'] = []
    course_detail['status'] = []

    while True:
        row_num = str(row_number)  # track the row number in table
        avail_xpath = config.course_avail_xpath.replace("#ROW#", row_num)
        cr_loc_xpath = config.course_loc_xpath.replace("#ROW#", row_num)

        try:
            avail_data = html_page.xpath(avail_xpath)
            loc_data = html_page.xpath(cr_loc_xpath)

            # stop iterating if data is not found at row (table ended)
            if avail_data is None or len(avail_data) == 0:
                if row_number == 1:
                    # if no rows available course could be invalid / not available / not scheduled
                    course_invalid = True
                break

            loc_raw_data = loc_data[0].text_content()
            avail_raw_data = avail_data[0].text_content()

            course_detail['location'].insert((row_number - 1), loc_raw_data)
            course_detail['status'].insert((row_number - 1), avail_raw_data)

        except Exception as error:
            print("Error in reading xpath" + str(error))
            break

        row_number += 1  # increasing table row number

    # if course is not invalid, fetch name else set invalid flag
    if course_invalid is True:
        course_detail['invalid'] = True
    else:
        name_data = html_page.xpath(config.course_name_xpath)
        name_raw_data = name_data[0].text_content()
        course_detail['name'] = name_raw_data


def map_details_to_students(courses_details):
    """
    Map details of each course to the student who has opted for the course
    Args:
        courses_details: Updated details of all subjects

    Returns:
        Dict of student email mapped to details of all courses opted for
    """
    student_details = {}
    details_map = read_json(config.student_course_loc)

    for details in details_map.values():
        stud_course_data = {}
        stud_email = details["email"]

        for cr_num, cr_term in details['courses'].items():
            course_name = get_course_name(details['subject'], cr_num, cr_term)
            course_details = courses_details[course_name]
            if course_details is not None:
                stud_course_data[course_name] = course_details

        if stud_email in student_details:
            # if same email exists with different subject, merge the courses into same object as we send single email
            student_details[stud_email]['courses'].update(stud_course_data)
        else:
            # create new entry in the dict
            details['courses'] = stud_course_data
            student_details[stud_email] = details
            del student_details[stud_email]["subject"]

    return student_details


def get_course_name(subject, course_id, term):
    """
    Course is defined as subject + : + number + - + term. eg. CSC:501-2198
    Args:
        subject: Subject of course
        course_id: Course id / number
        term: Term taking the course

    Returns:
        Name of the subject to map the subject uniquely
    """
    return subject + ":" + course_id + " - " + term


def read_json(file_path):
    """
    Read json object from the file
    Args:
        file_path: Path of the json file, eg. path-to-file/file-name.json

    Returns:
        Json object retrieved from the file
    """
    with open(file_path, mode="r", encoding="UTF-8") as json_file:
        data = json.load(json_file)

    return data
