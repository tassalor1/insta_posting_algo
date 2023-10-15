from selenium import webdriver
from selenium.webdriver.common.by import By
from credentials import insta_user, insta_password
from time import sleep

class Bot():

    def __init__(self):
        self.login(insta_user, insta_password)
        self.post()

    def login(self, insta_user, insta_password):

        self.driver = webdriver.Chrome()
        self.driver.get('https://instagram.com/')
        sleep(5)

        # click cookies pop up
        try:
            cookies = self.driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]')
            cookies.click()
        except Exception as e:
            print(f"Could not find the cookies button: {e}")

        sleep(3)

        # Enter username/password
        username = self.driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        username.clear()
        password.clear()

        username.send_keys(insta_user)
        password.send_keys(insta_password)

        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # self.driver.get("https://www.instagram.com/clave.xt/")
        sleep(5)

    def post(self):
        try:
            sav_info = self.driver.find_element(By.CSS_SELECTOR, "div[role='button'].btn-class")
            sav_info.click()
        except Exception as e:
            print(f"Could not find the save info button: {e}")

        try:
            create_button = self.driver.find_element(By.XPATH,'// *[ @ id = "mount_0_0_e0"] / div / div / div[2] '
                                                              '/ div / div / div / div[1] / div[1] / div[1] / div / div '
                                                              '/ div / div / div[2] / div[7] / div / span / div / a / div '
                                                              '/ div[2] / div / div / span / span')
            create_button.click()
        except Exception as e:
            print(f"Could not find the create button: {e}")

        try:
            sel_comp = self.driver.find_element(By.XPATH, '/ html / body / div[8] / div[1] / div / div[3] / div / div / div '
                                           '/ div / div / div / div / div[2] / div[1] / div / div / div[2] / div / button')
            sel_comp.click()
        except Exception as e:
            print(f"Could not find the select button: {e}")

def main():
    my_bot = Bot()


if __name__ == '__main__':
    main()

