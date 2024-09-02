import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Scraper():
    #Inicializando
    def __init__(self) -> None:
        self.options = webdriver.ChromeOptions()

        self.options.add_argument('--log-level=3')

        self.options.add_argument('--disable-logging')

        #self.options.add_argument("--headless")        

        self.main_loop(1)
    
    def main_loop(self, start_page, reviews_arg=[], rates_arg=[]):
        driver = self.get_driver()

        self.login(driver)

        self.run_Scraper(driver,start_page,reviews_arg,rates_arg)               

    #Driver para manipulação do website
    def get_driver(self):
        driver = webdriver.Chrome('./chromedriver', chrome_options = self.options)  # Optional argument, if not specified will search path.

        driver.get('https://www.glassdoor.com.br/index.htm')

        driver.maximize_window()

        print('Starting Browser. OK!\n')

        return driver

    #Logar na plataforma    
    def login(self, driver):
        print('Log In.\n')

        #Verificando se a página carregou     
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "section")))

        #Deslocando até o input do email (bloqueio de direcionamento via elemento html, saida TAB)  
        n = 16
        for i in range(n):
            ActionChains(driver).send_keys(Keys.TAB).perform()
            time.sleep(0.5)

        time.sleep(2)

        ActionChains(driver).send_keys(Keys.ENTER).perform()

        time.sleep(2)

        #Inserir dados do login

        ActionChains(driver).send_keys('seuemail').perform()

        ActionChains(driver).send_keys(Keys.ENTER).perform()

        time.sleep(2)

        #Inserir senha
        password_field = driver.find_element(By.NAME,'password')

        password_field.send_keys('suasenha')

        time.sleep(2)

        password_field.send_keys(Keys.ENTER)

        time.sleep(10)

        # email_field.send_keys('laossyt@gmail.com')
        # ActionChains(driver).move_to_element(email_field).perform()
        print('Log In. OK!\n')

    #Scraping das reviews
    def run_Scraper(self, driver, start_page, reviews_arg, rates_arg):
        print('Starting scrapper.\n')

        reviews = reviews_arg
        rates = rates_arg

        page = start_page
        tries = 0

        #Entrar no link da empresa
        #============================================================================================
        print('Loading enterprise page. OK!')

        url = f'https://www.glassdoor.com.br/Avalia%C3%A7%C3%B5es/DXC-Technology-Avalia%C3%A7%C3%B5es-E1603125_P{page}.htm?filter.iso3Language=por'

        driver.get(url)

        #============================================================================================

        #Scrap das paginas
        while(True):
            print(f'Scrapping the page: {page}')            
            
            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "ReviewsFeed")))

                time.sleep(3)
                
                reviews_div = driver.find_element(By.ID,"ReviewsFeed")    

            except:
                print(f'Reviews not found. Refreshing!\nTry:{tries}')

                driver.refresh()

                if tries == 3:
                    print('Scrapping error! Restarting Service.')
                    page -= 1
                    break        

                tries += 1

                continue

            soup = BeautifulSoup(reviews_div.get_attribute('outerHTML'),'html.parser')

            reviews_elements = soup.find_all('p', class_='pb')
            reviews_rates = soup.find_all('span', 'ratingNumber')


            if tries == 0:
                for review in reviews_elements:
                    if 'px-std' not in review['class']:
                        reviews.append(review.text)
                        #print(review)

                for rate in reviews_rates:
                    rates.append(rate.text)    

            print(f'Reviews got: {len(reviews)}')
            print(f'Rates got: {len(rates)}\n')            

            try:
                next_btn = driver.find_element(By.CLASS_NAME,'nextButton')

                if not next_btn.is_enabled():
                    print("Scrapping done!")
                    print('Scrapping Phase. OK!\n')
                    
                    self.save_data(reviews,rates, page) 
                    return                   

                next_btn.click()        

                if tries != 0:
                    tries = 0

                page += 1
            
            except:
                print(f'Button not found. Refreshing!\nTry:{tries}')

                driver.refresh()

                if tries == 3:
                    print('Scrapping error! Restarting Service.')
                    break        

                tries += 1

        driver.quit()

        self.main_loop(page+1, reviews_arg = reviews, rates_arg = rates)        

    #Salvando Dados obtidos
    def save_data(self,reviews,rates,page):
        print('Saving Data Base.\n')

        f_reviews = {'pros': [], 'contras': [], 'rates': rates}

        for i in range(len(reviews)):
            if i%2 == 0:
                f_reviews['pros'].append(reviews[i])
            else:
                f_reviews['contras'].append(reviews[i])

        print(f"# Pros Comments: {len(f_reviews['pros'])}")
        print(f"# Bad Comments: {len(f_reviews['contras'])}")
        print(f"# Rates: {len(f_reviews['rates'])}\n")

        df = pd.DataFrame(f_reviews)
        df.to_csv(f"reviews-page{page}.csv")


if __name__ == '__main__':
    Scraper()