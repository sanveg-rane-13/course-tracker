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
import requests as req
import logging as logger
import src.json_handler as json_hndlr
import copy
from lxml import html
from resources.config import Config as config


def init_courses_data():
    """
    The method performs:
        Parses the JSON of students opting courses and creates list
        Fetches data for each course
        Updates the course as per availability

    Returns:
        List of courses with their statuses
    """
    student_courses = json_hndlr.read_json(config.student_course_loc)
    courses_details = parse_course_data(student_courses)
    update_course_status(courses_details)
    clean_invalid_subjects(courses_details)

    file_loc = config.temp_loc + config.course_file_name
    json_hndlr.write_json(courses_details, file_loc)


def parse_course_data(student_courses):
    """
    Parse the JSON config to create list of subjects to fetch
    Used at load to create a temporary storage of all courses
    Args:
        student_courses: JSON extracted from resources

    Returns:
        List if student courses to be fetched for status
    """
    course_details_map = {}
    stud_info_map = {}
    course_term_map = json_hndlr.read_json(config.course_term_loc)

    for student_data in student_courses.values():
        stud_info_map[student_data["email"]] = student_data["name"]

        # iterating all courses in the object
        for cr_num, cr_term in student_data["courses"].items():
            c_subject = student_data["subject"]
            course_name = get_course_name(c_subject, cr_num, cr_term)

            # create a new course entry in course details
            if course_name not in course_details_map:
                course_detail = {
                    'subject': c_subject,
                    'num': cr_num,
                    'term': course_term_map[cr_term],
                    "stud_info": {}
                }
                course_details_map[course_name] = course_detail

            # add student email details to the course
            course_details_map[course_name]["stud_info"][student_data["email"]] = student_data["name"]

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
            logger.error("Invalid course:" + course_name)
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


def clean_invalid_subjects(course_details):
    """
    Remove courses whoes data was not available on the website
    Args:
        course_details: Updated details of all subjects
    """
    cr_to_del = []
    for cr_name, cr_detail in course_details.items():
        if 'invalid' in cr_detail and cr_detail['invalid'] == True:
            cr_to_del.append(cr_name)

    for cr_name in cr_to_del:
        del course_details[cr_name]


def update_crs_details_and_get_updates():
    """
    The method performs following tasks:
        - Read saved courses
        - Fetch updated data
        - Compare and return list of updated courses
        - Save the updated course details in json
    Returns:
        list of courses which have been updated with statuses
    """
    try:
        cr_details_file_loc = config.temp_loc + config.course_file_name
        current_data = json_hndlr.read_json(cr_details_file_loc)

        updated_data = copy.deepcopy(current_data)
        update_course_status(updated_data)
        logger.info("Fetched updated data")

        changes = compare_and_get_updates(current_data, updated_data)
        logger.debug("Number of courses updated: {}".format(str(len(changes))))

        json_hndlr.write_json(updated_data, cr_details_file_loc)
    except Exception as error:
        logger.error("Error updating course statuses: " + str(error), error)

    return changes


def compare_and_get_updates(saved_details, updated_details):
    """
    Compare updated course status
    Args:
        saved_details: old details before update
        updated_details: fetched details

    Returns:
        Dict of updates in courses
    """
    updates_courses = []
    for cr_name, cr_details in saved_details.items():
        new_crs_data = updated_details[cr_name]
        if cr_details["status"] != new_crs_data["status"]:
            logger.info("Course status updated: {}".format(cr_name))
            updates_courses.append(cr_name)

    return updates_courses


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


def get_course_data(course_list, get_all_data):
    """
    For the courses passed, get details of each course
    Args:
        course_list: List of courses to return data
        get_all_data: boolean, if set to true, return data for all courses

    Returns:
        Dict of course name and corresponding data
    """

    try:
        cr_details_file_loc = config.temp_loc + config.course_file_name
        courses_data = json_hndlr.read_json(cr_details_file_loc)
    except Exception as error:
        logger.error("Error fetching courses file", error)

    fetched_data = {}
    if courses_data is not None:
        # if flag set, return entire data
        if get_all_data is True:
            fetched_data = courses_data

        else:
            # fetch course in generated course file
            for cr_name in course_list:
                crs_det = courses_data[cr_name]
                if crs_det is not None:
                    fetched_data[cr_name] = crs_det

    return fetched_data


def map_courses_to_emails(courses_details):
    """
    Map courses list to each email
    Returns
        Dict of email ids with courses registered
        eg. {"email": [courses]}
    """
    stud_crs_map = {}

    for cr_name, cr_dets in courses_details.items():
        students = cr_dets["stud_info"]
        for email in students.keys():
            if email not in stud_crs_map:
                stud_crs_map[email] = []
            stud_crs_map[email].append(cr_name)

    return stud_crs_map
