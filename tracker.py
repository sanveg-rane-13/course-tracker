"""
Root of script to track NCSU Courses

Author:
    Sanveg Rane
"""
import course_fetcher as fetcher
import email_handler as emailer


def perform_operation():
    """
    Performs the basic function of the script:
        1) Fetches course details for all courses registered
        2) For each student create object of all courses registered by him
        3) Send email to each student with the status of each course
    """
    # Step 1: Fetch course details for all the courses registered by the student
    courses_details = fetch_course_data()

    # Step 2: Map all course details to each student subscribed to the course
    student_details = get_students_details(courses_details)

    # Step 3: Send email with details
    send_emails(student_details)


def fetch_course_data():
    """
    Fetch course details
    Returns:
        Dict of course and its details
    """
    print("Fetching course details")
    courses_details = fetcher.get_courses()
    # for cr_name, cr_det in courses_details.items():
    #     print(cr_name + " : " + str(cr_det))

    return courses_details


def get_students_details(courses_details):
    """
    Fetch student details with course details mapped for each student
    Args:
        courses_details: Dict of course and its details

    Returns:
        Dict of email ID of student and all courses registered to
    """
    print("Parsing student data")
    students_details = fetcher.map_details_to_students(courses_details)
    # for email, details in students_details.items():
    #     print(email + " : " + str(details))

    return students_details


def send_emails(student_details):
    """
    Send the processed details of courses to the email addresses of each student
    Args:
        student_details: Dict of email ID of student and all courses registered to
    """
    emailer.send_details_to_students(student_details)


if __name__ == '__main__':
    perform_operation()