from django.test import TestCase, Client
from django.contrib.auth.models import User
from selenium import webdriver


# Create Currency Test Case
class TestCreateCurrencyTestCase(TestCase):
    def __init__(self, method_name: str = ...):
        super().__init__(method_name)
        # Super User
        self.super_user_name = 'superuser'
        self.super_user_password = 'h1hjk49n3v23098'
        self.super_user_email = 'superuser1@byourdomain.com'

    def setup_method(self, method):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("start-maximized")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.vars = {}

    def test_create_currency(self):
        self.setup_method("")

        # SuperUser
        super_user = User.objects.create_superuser(username=self.super_user_name, email=self.super_user_email)
        super_user.set_password(self.super_user_password)
        print("Super User Created")
        print(super_user)

        self.driver.get("http://localhost:8000/login")
        self.driver.set_window_size(1600, 900)
        self.driver.find_element_by_id("exampleInputEmail").clear()
        self.driver.find_element_by_id("exampleInputEmail").send_keys(self.super_user_name)
        self.driver.find_element_by_id("exampleInputPassword").clear()
        self.driver.find_element_by_id("exampleInputPassword").send_keys(self.super_user_password)
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        print("LOGGED IN")

        self.driver.get("http://localhost:8000/admin")
        self.driver.find_element_by_xpath("//div[@id='content-main']/div[3]/table/tbody/tr/td/a").click()
        self.driver.find_element_by_id("id_name").click()
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("Dolar")
        self.driver.find_element_by_id("id_code").click()
        self.driver.find_element_by_id("id_code").clear()
        self.driver.find_element_by_id("id_code").send_keys("USD")
        self.driver.find_element_by_id("id_sufix").click()
        self.driver.find_element_by_id("id_sufix").clear()
        self.driver.find_element_by_id("id_sufix").send_keys("USD")
        self.driver.find_element_by_name("_save").click()

        print("CURRENCY CREATED")
        self.teardown_method("")

    def teardown_method(self, method):
        self.driver.quit()
