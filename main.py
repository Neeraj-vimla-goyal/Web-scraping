import smtplib
import ssl
import time
import requests
import selectorlib
import os

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def scrape(url):
    """
    Scrape the page from the URL
    """
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def store(_str):
    with open("data.txt", "a") as file:
        file.write(_str + "\n")


def read():
    with open("data.txt", "r") as file:
        content = file.read()
    return content


def get_cred():
    cred_dic = {}
    for key in os.environ:
        if key == "PASSWORD_SCRAPING_APP":
            cred_dic["PASSWORD_SCRAPING_APP"] = os.environ["PASSWORD_SCRAPING_APP"]
        elif key == "SENDER":
            cred_dic["SENDER"] = os.environ["SENDER"]
        elif key == "RECEIVER":
            cred_dic["RECEIVER"] = os.environ["RECEIVER"]
    return cred_dic


def send_email(message, _username, _password, _receiver):
    host = "smtp.gmail.com"
    port = 465

    _loc_username = _username
    _loc_password = _password

    _loc_receiver = _receiver
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(_loc_username, _loc_password)
        server.sendmail(_loc_username, _loc_receiver, message)


if __name__ == "__main__":

    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        file_content = read()

        if extracted not in file_content:

            if extracted != "No upcoming tours":
                body = ""
                store(extracted)
                cred = get_cred()
                user = cred["SENDER"]
                passw = cred["PASSWORD_SCRAPING_APP"]
                receiv = cred["RECEIVER"]
                body = "Subject: New Tour Info-" + "\n" + "Hi " + receiv + ", " + "We have got the new tour info for you." + "\n"*2 + "Tour Name: " + extracted + "\n"*5 + "Thanks and Regards," + "\n" + user
                body = body.encode("utf-8")
                send_email(body, user, passw, receiv)

        time.sleep(1)
