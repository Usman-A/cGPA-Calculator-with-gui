import requests
from getpass import getpass
from bs4 import BeautifulSoup

s = requests.session()

url = 'https://csprd.mcmaster.ca/psc/prcsprd/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSS_MY_CRSEHIST.GBL?Page=SSS_MY_CRSEHIST&Action=U'

macid = input("Please enter your macid: ")
password = getpass("Please enter your password: ")

result = s.post(
    url,
    data = { "userid" : macid, "pwd" : password },
    headers = dict(referer=url)
)

s.close()

soup = BeautifulSoup(result.content, "html.parser")

error = soup.body.find('span', attrs={'id' : 'login_error'})
if error:
    print("Login Failed.\n")
    quit(1)
else:
    print("Login Successful. \n")

print("Retreiving Grades... \n")

gradeData = soup.find_all('span', attrs=({'class' : 'PSEDITBOX_DISPONLY'}))[2::4]
unitData = soup.find_all('span', attrs=({'class' : 'PSEDITBOX_DISPONLY'}))[3::4]

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
