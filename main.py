from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from threading import Thread
from datetime import date
from db import DB
import asyncio

# Class Name Path
NAME = ['sc-fdfabab6-6.jNQQeD']
REGULARPRICE = ['regularPrice', 'sc-5492faee-1.ibyzkU.oldPrice',
                'sc-5492faee-2.ipHrwP.finalPrice']
PRICE = ['sc-5492faee-2.ipHrwP.finalPrice']
PARCELS = ['cardParcels']


class Kabum(Thread):
    def __init__(self, init, limit):
        Thread.__init__(self)
        self.init = init
        self.limit = limit
        self.main_link = "https://www.kabum.com.br/produto/"
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.product = list()
        self.historic_product = list()

    def find_data(self, options: list):
        for xpath in options:
            try:
                return self.driver.find_element(By.CLASS_NAME, xpath).text
            except:
                pass

        return ""

    def run(self):
        for i in range(self.init, self.limit):
            link = f'{self.main_link}{i}'
            self.driver.get(link)

            pro = {
                "id": int(i),
                "Nome": self.find_data(NAME),
                "link": link,
            }

            if not pro["Nome"] == "":
                self.product.append(pro)

            his = {
                "dia": date.today().strftime("%d/%m/%Y"),
                "preco": self.find_data(REGULARPRICE),
                "avista": self.find_data(PRICE),
                "parcelado": self.find_data(PARCELS),
                "productId": int(i),
            }

            if not his['preco'] == "" and not his['avista'] == "":
                self.historic_product.append(his)

        self.driver.close()


def main():
    products = list()
    historic_products = list()
    last_value_db = asyncio.run(DB.get_last_value_product())
    threads_list = list()
    limit = last_value_db

    while True:
        for thread in range(20):
            init = limit
            limit += 10
            threads_list.append(Kabum(init, limit))

        for thread in threads_list:
            thread.start()

        for thread in threads_list:
            thread.join()

        for thread in threads_list:
            for i in thread.product:
                products.append(i)
            for i in thread.historic_product:
                historic_products.append(i)

        if len(products) > 10:
            asyncio.run(DB.create_product(products))
            asyncio.run(DB.create_historic_product(historic_products))
            products.clear()
            historic_products.clear()

        threads_list.clear()


if __name__ == "__main__":
    main()
