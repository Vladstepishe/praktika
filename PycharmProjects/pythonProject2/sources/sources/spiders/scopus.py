import scrapy
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScopusSpider(scrapy.Spider):
    name = "scopus"
    start_urls = ["https://scopus.com/sources"]

    def parse(self, response):
        # options = webdriver.ChromeOptions()                                                                               #Пытался различными способами заставить селениум работать в фоновом режиме
        # options.headless = True                                                                                           #Но так и не получилось(
        # browser = webdriver.Chrome(options=options)                                                                       #Поэтому оставил как есть
        browser = webdriver.Chrome()
        browser.get("https://www.scopus.com/sources")
        sources = []


        for pages in range(50):                                                                                              #Здесь осуществляется переход по страницам для сбора url источников, чтобы в дальнейшем гулять по ним
            sources_container = (browser.find_elements(By.XPATH, '//*[@class="lightGreyBorderBottom"]/td[2]/a'))            #Пришлось из одного списка в другой перебрасывать url, чтобы тут же использовать get_attribute('href)
            for el in sources_container:                                                                                    #Если сделать это после того как мы соберём все url и начнём ходить по ним, то он выдаёт, что не может достать href
                sources.append(el.get_attribute('href'))
            if pages!=49:
                browser.find_element(By.XPATH, '//*[@id="sourceResults-nextPage"]').click()                                     #Нажатие на кнопку перехода на след. страницу
        # while browser.find_element(By.XPATH, '//*[@id="sourceResults-nextPage"]'):
        #     sources_container = (browser.find_elements(By.XPATH,'//*[@class="lightGreyBorderBottom"]/td[2]/a'))
        #     for el in sources_container:
        #         sources.append(el.get_attribute('href'))
        #     browser.find_element(By.XPATH, '//*[@id="sourceResults-nextPage"]').click()
        # sources_container = (browser.find_elements(By.XPATH, '//*[@class="lightGreyBorderBottom"]/td[2]/a'))
        # for el in sources_container:
        #     sources.append(el.get_attribute('href'))

        for i in range(len(sources)):                                                                                       #Начало перехода по страницам с источниками
            print(f'-------------------{i}----------------------')                                                          #Сделал для себя для наглядности
            while True:
                try:
                    browser.get(str(sources[i]))
                    break
                except:
                    print("Сервер не отвечает")

                                                                                                                            #!Обработал явные ожидания. Если слипами пользоваться, то вылетают ошибки, потому что страницы грузятся с разной скоростью
            name = WebDriverWait(browser, 100).until(                                                                        #Достаём название источника
                EC.presence_of_element_located((By.XPATH, '//*[@id="jourlSection"]/div[2]/div/h2')))

            publisher = WebDriverWait(browser, 100).until(EC.presence_of_element_located(                                    #Достаём издателя
                (By.XPATH, '//*[@id="jourlSection"]/div[2]/div/ul/li[2]/span[2]'))).text

            branches = WebDriverWait(browser, 100).until(                                                                    #Достаём отрасли
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="csSubjContainer"]/span')))

            if not branches:
                branches = 'Отрасль не указана'
            else:
                for j in range(len(branches)):
                    branches[j] = branches[j].text

            type = WebDriverWait(browser, 100).until(                                                                        #Достаём тип источника
                EC.presence_of_element_located((By.XPATH, '//*[@id="jourlSection"]/div[2]/div/ul/li[5]/span[2]'))).text

            citescore = WebDriverWait(browser, 100).until(                                                                   #Достаём Citescore
                EC.presence_of_element_located((By.XPATH, '//*[@id="rpCard"]/h2/span'))).text

            snip = WebDriverWait(browser, 100).until(                                                                        #Достаём SNIP
                EC.presence_of_element_located((By.XPATH, '//*[@id="snipCard"]/h2/span'))).text

            sjr = WebDriverWait(browser, 100).until(                                                                         #Достаём SJR
                EC.presence_of_element_located((By.XPATH, '//*[@id="sjrCard"]/h2/span'))).text

            yield {                                                                                                         #Возвращаем найденное
                'url': str(sources[i]),
                'source name': name.text,
                'publisher': publisher,
                'knowledge branch': branches,
                'source type': type,
                'citescore': citescore,
                'snip': snip,
                'sjr': sjr
            }