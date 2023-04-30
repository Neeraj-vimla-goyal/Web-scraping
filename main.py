import smtplib
import ssl
import time
import requests
import selectorlib
import os
import sqlite3

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


class Event:
    def scrape(self, url):
        """
        Scrape the page from the URL
        """
        response = requests.get(url, headers=HEADERS)
        source = response.text
        return source

    def extract(self, source):
        """
        Extract the event from the response
        """
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value


class FileOps:
    def store(self, _str):
        """
        Write the event into file:
        """
        with open("data.txt", "a") as file:
            file.write(_str + "\n")

    def read(self):
        """
        read the events from the file
        """
        with open("data.txt", "r") as file:
            content = file.read()
        return content


class Config:
    def get_cred(self):
        cred_dic = {}
        for key in os.environ:
            if key == "PASSWORD_SCRAPING_APP":
                cred_dic["PASSWORD_SCRAPING_APP"] = os.environ["PASSWORD_SCRAPING_APP"]
            elif key == "SENDER":
                cred_dic["SENDER"] = os.environ["SENDER"]
            elif key == "RECEIVER":
                cred_dic["RECEIVER"] = os.environ["RECEIVER"]
        return cred_dic


class Email:
    def send(self, message, _username, _password, _receiver):
        host = "smtp.gmail.com"
        port = 465

        _loc_username = _username
        _loc_password = _password

        _loc_receiver = _receiver
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(_loc_username, _loc_password)
            server.sendmail(_loc_username, _loc_receiver, message)


class Database:
    def __init__(self, database_path):
        self.connection = sqlite3.connect(database_path)

    def read_db(self, _extracted):
        row = _extracted.split(",")
        row = [item.strip() for item in row]
        band, city, date = row
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM events where band=? AND city=? and date=?", (band, city, date))
        rows = cursor.fetchall()
        print(rows)
        return rows

    def write_db(self, _extracted):
        row = _extracted.split(",")
        row = [item.strip() for item in row]
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
        self.connection.commit()


if __name__ == "__main__":

    while True:
        event = Event()
        scraped = event.scrape(URL)
        extracted = event.extract(scraped)
        print(extracted)
        file_operation = FileOps()
        file_content = file_operation.read()

        if extracted != "No upcoming tours":
            dbops = Database(database_path="data.db")
            row = dbops.read_db(extracted)
            if not row:
                body = ""
                # Writing into the file
                file_operation.store(extracted)
                # Getting credentials for the emails
                config = Config()
                cred = config.get_cred()
                user = cred["SENDER"]
                passw = cred["PASSWORD_SCRAPING_APP"]
                receiv = cred["RECEIVER"]
                # Preparing the email body
                body = "Subject: New Tour Info-" + "\n" + "Hi " + receiv + ", " + "We have got the new tour info for you." + "\n" * 2 + "Tour Name: " + extracted + "\n" * 5 + "Thanks and Regards," + "\n" + user
                body = body.encode("utf-8")
                # Sending the email body
                email = Email()
                email.send(body, user, passw, receiv)
                # Writing into the database
                dbops.write_db(extracted)

                time.sleep(1)

