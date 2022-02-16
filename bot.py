# Библиотеки
import os
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ex_cond
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementNotSelectableException, ElementClickInterceptedException, StaleElementReferenceException
from fake_useragent import UserAgent
from login_pass import login, password

# Необходимые переменные
main_url = "https://5kings.ru/"
directory = os.path.dirname(os.path.realpath(__file__))
env_path = directory + "\chromedriver"
service = Service(env_path + "\chromedriver.exe")
useragent = UserAgent()
os.environ['PATH'] += env_path  # Добавляет chromedriver в PATH


# Главный скрипт
def openChrome(url=main_url):
    options = webdriver.ChromeOptions()
    # options.headless = True
    options.add_argument('window-size=1600,900')
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument(f'--user-agent={useragent.random}')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url=url)
    try:
        # Вход
        WebDriverWait(driver, 10).until(ex_cond.presence_of_element_located(
            (By.XPATH, "(//div[@id='top_menu']//div)")))
        driver.find_element(By.NAME, "login").send_keys(login)
        driver.find_element(By.NAME, "pwd").send_keys(password)
        driver.find_element(By.ID, "input_button").click()
        WebDriverWait(driver, 10).until(ex_cond.presence_of_element_located(
            (By.ID, "exit_button")))
        driver.find_element(By.ID, "input_button").click()
        driver.switch_to.window(driver.window_handles[1])
        WebDriverWait(driver, 10).until(ex_cond.presence_of_element_located(
            (By.ID, "main_table")))
        sleep(0.5)

        while True:
            # Встаёт в очередь
            try:
                driver.find_element(By.ID, "pb_1").click()
                sleep(0.5)
                driver.switch_to.frame("d_act")
                driver.find_element(By.XPATH, "//input[@value='Встать в очередь на поле битвы']").click()
                sleep(10)
            except NoSuchElementException:
                print("no Labirint queue")

            # Ждёт, пока станет доступно подтверждение
            while True:
                try:
                    driver.switch_to.default_content()
                    driver.switch_to.frame("d_act")
                    if driver.find_element(By.XPATH, "//input[@value='Подтвердить']"):
                        driver.find_element(By.XPATH, "//input[@value='Подтвердить']").click()
                        break
                except NoSuchElementException:
                    try:
                        if driver.find_element(By.ID, "mapCanvas"):
                            break
                    except NoSuchElementException:
                        print("no skip because of no fight")
                    try:
                        driver.find_element(By.ID, "addblockway4")
                        print("skip - moved to door 4")
                        break
                    except NoSuchElementException:
                        try:
                            driver.find_element(By.ID, "addblockway3")
                            print("skip - moved to door 3")
                            break
                        except NoSuchElementException:
                            try:
                                driver.find_element(By.ID, "addblockway2")
                                print("skip - moved to door 2")
                                break
                            except NoSuchElementException:
                                try:
                                    driver.find_element(By.ID, "addblockway1")
                                    print("skip - moved to door 1")
                                    break
                                except NoSuchElementException:
                                    print("no skip because of no doors")
                    print("no confirm button")
                    driver.refresh()
                    sleep(10)
            sleep(2)

            # Ждёт других игроков
            while True:
                try:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.switch_to.default_content()
                    driver.switch_to.frame("d_act")
                    sleep(2)
                    if driver.find_element(By.ID, "estTime"):
                        sleep(10)
                        print('waiting for other players')
                        driver.refresh()
                except NoSuchElementException:
                    print("Session started")
                    driver.refresh()
                    break

            # Действия в самом лабиринте
            while True:  # Проверяет, можно ли атаковать другого игрока в этом зале
                try:
                    driver.switch_to.default_content()
                    driver.switch_to.frame("d_ulist")
                    sleep(10)
                    driver.find_element(By.XPATH, "//a[@title, 'Атаковать']").click()
                except NoSuchElementException:  # Если нет, то проходит в другой зал
                    driver.switch_to.default_content()
                    driver.switch_to.frame("d_act")
                    try:
                        driver.find_element(By.ID, "addblockway4").click()
                        print("moved to door 4")
                    except NoSuchElementException:
                        try:
                            driver.find_element(By.ID, "addblockway3").click()
                            print("moved to door 3")
                        except NoSuchElementException:
                            try:
                                driver.find_element(By.ID, "addblockway2").click()
                                print("moved to door 2")
                            except NoSuchElementException:
                                try:
                                    driver.find_element(By.ID, "addblockway1").click()
                                    print("moved to door 1")
                                except NoSuchElementException:
                                    print("no doors")
                try:  # Если обнаруживает поле битвы, начинает скрипт атаки
                    if driver.find_element(By.ID, "mapCanvas"):
                        print("Started fighting")

                        # Логика боя
                        while True:
                            try:
                                WebDriverWait(driver, 10).until(ex_cond.text_to_be_present_in_element(
                                    (By.ID, "TurnLabel"), "Ваш ход"))
                                driver.switch_to.default_content()
                                driver.switch_to.frame("d_pers")
                                driver.find_element(By.XPATH, "//a[@alt='Возможности']").click()
                                sleep(0.5)
                                driver.switch_to.default_content()
                                driver.switch_to.window(driver.window_handles[2])
                                try:
                                    driver.find_element(By.TAG_NAME, "input").click()
                                    WebDriverWait(driver, 2).until(ex_cond.presence_of_element_located(
                                        (By.XPATH, "//input[@type='button']")))
                                    driver.find_element(By.XPATH, "//input[@type='button']").click()
                                    print("used clone spell")
                                except TimeoutException:
                                    print("no clone spells left")
                                except NoSuchElementException:
                                    print("no clone spells left")
                                driver.close()
                                driver.switch_to.window(driver.window_handles[1])
                                driver.switch_to.frame("d_act")
                                sleep(1)

                                try:
                                    driver.find_element(By.XPATH, "//input[@value='Удар/Блок']").click()
                                    try:
                                        WebDriverWait(driver, 2).until(ex_cond.presence_of_element_located(
                                            (By.ID, "kk00")))
                                    except TimeoutException:
                                        pass

                                    try:
                                        driver.find_element(By.ID, "kk00").click()
                                        driver.find_element(By.ID, "kk10").click()
                                        try:
                                            driver.find_element(By.XPATH, "(//input[@type='button'])[2]").click()
                                            sleep(0.5)
                                            print("attacked by a weapon")
                                        except NoSuchElementException:
                                            print("er1")
                                        try:
                                            driver.find_element(By.XPATH, "(//input[@type='button'])[2]").click()
                                        except ElementNotInteractableException:
                                            print("no second attack/block confirm button")

                                    except ElementNotInteractableException:
                                        print("can't interact with attack")
                                    except ElementNotSelectableException:
                                        print("can't select attack")

                                    try:
                                        driver.find_element(By.ID, "bl00").click()
                                        driver.find_element(By.ID, "bl11").click()
                                        driver.find_element(By.ID, "bl02").click()
                                        driver.find_element(By.ID, "bl13").click()
                                        try:
                                            driver.find_element(By.XPATH, "(//input[@type='button'])[2]").click()
                                            sleep(0.5)
                                            print("blocked attacks")
                                        except NoSuchElementException:
                                            print("er2")
                                        try:
                                            driver.find_element(By.XPATH, "(//input[@type='button'])[2]").click()
                                        except ElementNotInteractableException:
                                            print("no second block/attack button")
                                    except ElementNotInteractableException:
                                        print("no block")
                                    except ElementClickInterceptedException:
                                        print("er4")

                                except ElementNotSelectableException:
                                    print("can't select Удар/Блок")
                                except ElementNotInteractableException:
                                    print("can't interact with Удар/Блок")

                                sleep(10)
                            except ElementNotInteractableException:
                                print("er5")
                            except TimeoutException:
                                try:  # Если обнаруживает конец боя, то выходит из скрипта атаки
                                    if driver.find_element(By.XPATH, "//input[@type='button']"):
                                        driver.find_element(By.XPATH, "//input[@type='button']").click()
                                        break
                                except NoSuchElementException:
                                    print("Fight isn't over")
                                except ElementNotInteractableException:
                                    print("er6")
                                print("not your turn")
                except NoSuchElementException:
                    print("no fight in this room")
                except StaleElementReferenceException:
                    print("stale error")

                # Если обнаруживает главный экран, то выходит из скрипта по Лабиринту
                try:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.switch_to.default_content()
                    driver.switch_to.frame("d_act")
                    if driver.find_element(By.ID, "arenax") or driver.find_element(By.XPATH, "//input[@value='Амулеты']"):
                        print("-------------\nLabirint is over!\n-------------")
                        driver.switch_to.default_content()
                        driver.find_element(By.ID, "pb_1").click()
                        break
                except NoSuchElementException:
                    pass
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


if __name__ == "__main__":
    openChrome()
    print("Done!", end='')
