from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
#from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys
import re
import datetime
import time
import sys
import csv


CREDENTIALS_PATH = "data\credentials.csv"
#DRIVER_PATH = "drivers\msedgedriver.exe"
DRIVER_PATH = "drivers\chromedriver94.exe"
CLASSES_PATH = "data\classes.csv"
WEBSITE_PATH = "https://prodigit.uniroma1.it/"


# get credentialis from credentials.csv
def get_credentials(file):
    rows = []
    with open(file, 'r') as f:
        csvreader = csv.reader(f)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row)
            break
    return rows[0]


# input data in website login page
def inputData(usr, pwd):
    username = driver.find_element_by_name("Username")
    password = driver.find_element_by_name("Password")
    # clear
    username.clear()
    password.clear()
    # input keys
    username.send_keys(usr)
    password.send_keys(pwd)

    submit_btn = driver.find_element_by_xpath(
        '//*[@id="LoginUserFormTable1_b"]/div/table/tbody/tr[2]/td[6]/div/input')

    # print("ok")

    try:
        action = ActionChains(driver)
        action.move_to_element(submit_btn).click().perform()
    except:
        print("coud not click")
        pass


# function that closes stupid cookie banner
def closeCookieBanner():
    try:
        cookie_banner = driver.find_element_by_xpath(
            '//*[@id="cookieChoiceDismiss"]')
        cookie_banner.click()
        print("eating cookies..\n")

    except:
        pass


# simple function that builds a list from the csv containing all the classess to book
def get_classes(file):
    rows = []
    with open(file, 'r') as f:
        csvreader = csv.reader(f)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row)
    return rows


# The Classroom Object
class Classroom:
    def __init__(self, class_id, building_id, mon, tue, wed, thu, fri, sat, sun):
        self.class_id = class_id
        self.building_id = building_id
        self.mon = mon
        self.tue = tue
        self.wed = wed
        self.thu = thu
        self.fri = fri
        self.sat = sat
        self.sun = sun


# Creates a queue wiht all the classroom object
def createQueue(fromcsv_list):
    l = fromcsv_list
    queue = []
    for elem in l:
        if elem != []:
            new_q_element = Classroom(
                elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7], elem[8]
            )
            queue.append(new_q_element)
        else:
            continue
    return queue


# Simple function to get the next monday
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


# function  that books all classrooms in queue
def BookClassess(queue):
    for elem in queue:
        try:
            print(f"booking class n. {str(elem.class_id)}...")
            bookClass(elem)
            print(f"class n. {str(elem.class_id)} booked succesfully!")
        except:
            print(
                f"something went wrong booking class n. {str(elem.class_id)}")


# function that books a single class
def bookClass(theClass):

    # book seats
    book_seats_section = driver.find_element_by_xpath(
        '/html/body/form/section/nav/ul/ul/li[2]/a/fontx')
    book_seats_section.click()

    driver.implicitly_wait(1)

    # selects "Codice Edificio"
    building_id_dropdown = Select(
        driver.find_element_by_name("codiceedificio"))

    building_id_dropdown.select_by_visible_text(theClass.building_id)

    # selects "Aula"

    classroom_id_dropdown = Select(driver.find_element_by_name("aula"))
    pattern = re.compile(
        f'.*{theClass.class_id}.*'
    )
    for option in classroom_id_dropdown.options:
        value = option.text
        if pattern.search(value):
            option.click()
            break
    """
    
    lastp = "-P0" + theClass.class_id[0] + "L0" + theClass.class_id[1:3]

    classroom_id_dropdown.select_by_visible_text(
        "AULA " + theClass.class_id + " -- " + theClass.building_id + lastp)
    """

    # selects "Settimana"
    week_dropdown = Select(driver.find_element_by_name("selezsettimana"))
    week_dropdown.select_by_visible_text(
        next_weekday(datetime.date.today(), 0).strftime("%d/%m/%Y"))

    weeklist = [theClass.mon, theClass.tue, theClass.wed,
                theClass.thu, theClass.fri, theClass.sat, theClass.sun]

    # selects all classess
    for i in range(6):
        if weeklist[i] != '':
            day_dropdown_from = Select(
                driver.find_element_by_name("dalleore"+str(i+1)))
            day_dropdown_from.select_by_visible_text(
                weeklist[i][0:2]+":00")

            day_dropdown_to = Select(
                driver.find_element_by_name("alleore"+str(i+1)))
            day_dropdown_to.select_by_visible_text(weeklist[i][3:5]+":00")

        else:
            continue

    # green pass checkbox
    try:
        driver.find_element_by_name("dichiarazione").click()
    except:
        pass

    driver.implicitly_wait(.2)

    # reserve button
    driver.find_element_by_xpath(
        "/html/body/form/section/article/table[7]/tbody/tr/td[1]/div/a[1]"
    ).click()

    # close button
    driver.find_element_by_xpath(
        "/html/body/font/p[5]/font/font/font/font/font/font/b/font/a/span/img"
    ).click()


### PROGRAM STARTS HERE ###

print("STARTING PROCESS..\n")

credentials = get_credentials(CREDENTIALS_PATH)

Username = credentials[0]
Password = credentials[1]


# opens driver window
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)

# goes to site
driver.get(WEBSITE_PATH)
driver.implicitly_wait(1)

# close the cookie banner
closeCookieBanner()
driver.implicitly_wait(1)


# try login the first time
print("logging in...\n")
inputData(Username, Password)
driver.implicitly_wait(.2)

# bruteforce crappy slow website
count = 0
while True:
    if count >= 5:
        print(
            "\n***\n\nA fatal error occurred trying to login!\n\n***\nCheck if user and password is correct\n\nWindow will close in 7 seconds")
        driver.quit()
        time.sleep(7)
        sys.exit()

    try:
        bad_elem = driver.find_element_by_xpath(
            '//*[@id="LoginUserFormTable1_b"]/div/table/tbody/tr[1]/td/div/font')
    except:
        break
    if len(bad_elem.text) > 0:
        try:
            inputData(Username, Password)
            driver.implicitly_wait(.2)
            count += 1
        except:
            pass

time.sleep(.5)

infostud_btn = driver.find_element_by_xpath(
    '/html/body/form/div/table/tbody/tr[3]/td/div/a')

infostud_btn.click()

print("logged in succesfully!\n")
driver.implicitly_wait(1)

# setup queue
classes_list = get_classes(CLASSES_PATH)
q = createQueue(classes_list)


# books classes
BookClassess(q)

# end program
driver.quit()
print("\nMy work here is done\n")
print("Window will close in 7 seconds")
time.sleep(7)
sys.exit()
