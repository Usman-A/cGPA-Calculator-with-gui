"""
Contains the logic for scraping data off a McMaster site

reworked by: @usman-a (github)
authored by: @abdullahnafees (github)
"""
import requests
from bs4 import BeautifulSoup

MCMASTER_GRADES_URL = "https://csprd.mcmaster.ca/psc/prcsprd/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSS_MY_CRSEHIST.GBL?Page=SSS_MY_CRSEHIST&Action=U"

# converts letter grades to the 12pt (1st item in tuple) and 4pt scale (2nd item in tuple)
GRADE_LETTER_TO_NUM_SCALE = {
    "A+": [12, 4.0],
    "A": [11, 3.9],
    "A-": [10, 3.7],
    "B+": [9, 3.3],
    "B": [8, 3.0],
    "B-": [7, 2.7],
    "C+": [6, 2.3],
    "C": [5, 2.0],
    "C-": [4, 1.7],
    "D+": [3, 1.3],
    "D": [2, 1.0],
    "D-": [1, 0.7],
    "F": [0, 0],
}


class AuthenticationError(ValueError):
    def __init__(self, name, age):
        self.name = name
        self.age = age


def fetch_grade_data(mac_id: str, password: str) -> BeautifulSoup:
    """
    This function authenticates and fetches raw grade data from the McMaster Grade site

    Args:
        mac_id (string): your MAC ID
        password (string): account password

    Returns:
    A beautiful soup object that can be used for parsing
    """
    # request data
    requests_session = requests.session()
    result = requests_session.post(
        MCMASTER_GRADES_URL,
        data={"userid": mac_id, "pwd": password},
        headers=dict(referer=MCMASTER_GRADES_URL),
    )
    requests_session.close()

    grade_soup = BeautifulSoup(result.content, "html.parser")

    # validate authentication
    if grade_soup.body.find("span", attrs={"id": "login_error"}):
        raise AuthenticationError("Login failed, please recheck user/pass")

    return grade_soup


def parse_grades(soup: BeautifulSoup) -> list:
    """
    Given the beautiful soup obj of the McMaster webpage, this function will return a list of tuple-3's
    containing the course code, units, and grade.

    Args:
        soup (BeautifulSoup): soup obj of the McMater Webpage

    Returns:
    list of (course code, course unit, course grade)
    """
    # getting the required HTML Properties, the class is used by 4 things, course_name, course_units, grade, and semester
    course_data = soup.find_all("span", attrs=({"class": "PSEDITBOX_DISPONLY"}))

    course_id = course_data[0::4]
    course_grade = course_data[2::4]
    course_units = course_data[3::4]

    return zip(course_id, course_units, course_grade)


def calculate_avg(grade_data: list) -> tuple:
    """
    Given course data returns a tuple of the 12pt and 4pt averages

    Args:
        grade_data (list): list of course data

    Returns:
        tuple: 12pt and 4pt avg
    """
    total_units = 0

    # 1st index is for 12pt scale, second is for 4pt scale
    grade_total = [0, 0]

    for (_, units, grades) in grade_data:
        # this ignores things like withdrawals (W), and transfer-credits ("T") as they don't affect your GPA
        if grades.text in GRADE_LETTER_TO_NUM_SCALE:
            # 1st index is for 12pt scale, second is for 4pt scale
            grade_total[0] += GRADE_LETTER_TO_NUM_SCALE[grades.text][0] * float(
                units.text
            )
            grade_total[1] += GRADE_LETTER_TO_NUM_SCALE[grades.text][1] * float(
                units.text
            )
            total_units += float(units.text)

    avg_12pt = grade_total[0] / total_units
    avg_4pt = grade_total[1] / total_units

    return (round(avg_12pt, 3), round(avg_4pt, 3))
