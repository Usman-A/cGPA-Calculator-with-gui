import requests
from getpass import getpass
from bs4 import BeautifulSoup

MCMASTER_GRADES_URL = 'https://csprd.mcmaster.ca/psc/prcsprd/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSS_MY_CRSEHIST.GBL?Page=SSS_MY_CRSEHIST&Action=U'

class AuthenticationError(ValueError):
    def __init__(self, name, age):
        self.name = name
        self.age = age

def fetch_grade_data(*, mac_id: str, password: str) -> BeautifulSoup:
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
        data = { "userid" : mac_id, "pwd" : password },
        headers = dict(referer=MCMASTER_GRADES_URL)
    )
    requests_session.close()
    
    grade_soup = BeautifulSoup(result.content, "html.parser")
    
    # validate authentication
    if grade_soup.body.find('span', attrs={'id' : 'login_error'}):
        raise AuthenticationError("Login failed, please recheck user/pass")
    
    return grade_soup
        

gradeData = soup.find_all('span', attrs=({'class' : 'PSEDITBOX_DISPONLY'}))
unitData = soup.find_all('span', attrs=({'class' : 'PSEDITBOX_DISPONLY'}))

print("Converting from 12 Scale to 4.0... \n")

gradeConversion = {
    'A+' : 4.0, 'A' : 3.9, 'A-' : 3.7,
    'B+' : 3.3, 'B' : 3.0, 'B-' : 2.7,
    'C+' : 2.3, 'C' : 2.0, 'C-' : 1.7,
    'D+' : 1.3, 'D' : 1.0, 'D-' : 0.7,
    'F' : 0,
}

zipData = zip(gradeData, unitData)

gradeTotal = 0
unitTotal = 0
for (grades, units) in zipData:
    if grades.text in gradeConversion:
        gradeTotal += gradeConversion[grades.text] * float(units.text)
        unitTotal += float(units.text)

print("Your Cumulative GPA on the 4.0 Scale is: {0:.3f}".format(gradeTotal/unitTotal))
