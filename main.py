import requests
import selectorlib
import time


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


def send_email():
    print("Email Sent !")


def store(_str):
    with open("data.txt", "a") as file:
        file.write(_str + "\n")


def read():
    with open("data.txt", "r") as file:
        content = file.read()
    return content


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        file_content = read()

        if extracted not in file_content:
            if extracted != "No upcoming tours":
                store(extracted)

        time.sleep(1)
