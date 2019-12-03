## TODO - convert to drupal8.j2 template
import os
import string
import random
import time
import pytest
import json
import selenium
from faker import Faker
from bs4 import BeautifulSoup
from locust import HttpLocust, TaskSet, task, events, between
from locust.clients import HttpSession
from pyquery import PyQuery
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

## TODO - transfer Helper Functions in a separate module (helper.py)
### HELPER FUNCTIONS Section
## Drupal 8 - Get form_build_id value via parsing
def get_form_build_id(self, request_path):
    # Get form build ID to pass back to Drupal on login.
    response = self.client.get(request_path)
    parsed_html = BeautifulSoup(response.content, 'lxml')
    form_build_id = parsed_html.body.find('input', {'name': 'form_build_id'})['value']
    return form_build_id

## Drupal 8 - Get form_token for creating content
def get_form_token(self, request_path):
    # Get form build ID to pass back to Drupal on login.
    response = self.client.get(request_path)
    parsed_html = BeautifulSoup(response.content, 'lxml')
    form_token = parsed_html.body.find('input', {'name': 'form_token'})['value']
    return form_token

## Drupal 8 - Get random article from page
def get_random_article(self, source_path, search_class, comment_form_id):
    resp = self.client.get(source_path)

    parsed_html = BeautifulSoup(resp.content, 'lxml')
    article_links = [link['href'] for link in parsed_html.body.findAll("a", {"class": search_class})]
    random_article_path = random.choice(article_links)

    # Parse returned article for comment form ID and post path
    random_article_html = BeautifulSoup(self.client.get(random_article_path).content, "lxml")
    comment_post_path = random_article_html.body.find('form', {'id': comment_form_id})['action']
    return { "random_article_path": random_article_path, "comment_post_path": comment_post_path }

## PyTest Code Steps
class TestKedbloginsearch():
  def setup_method(self, method):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    self.driver = webdriver.Chrome(chrome_options=options)
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_kedbloginsearch(self):
    # Test name: kedb-login-search
    # Step # | name | target | value | comment
    # 1 | open | / |  | 
    self.driver.get("http://dev-ps-loadtest-dummy.pantheonsite.io/")
    # 2 | click | id=edit-name |  | 
    self.driver.find_element(By.ID, "edit-name").click()
    # 3 | type | id=edit-name | eladio@getpantheon.com | 
    self.driver.find_element(By.ID, "edit-name").send_keys("eladio@getpantheon.com")
    # 4 | type | id=edit-pass | [Pantheon]1234 | 
    self.driver.find_element(By.ID, "edit-pass").send_keys("[Pantheon]1234")
    # 5 | click | id=edit-submit |  | 
    self.driver.find_element(By.ID, "edit-submit").click()
    # 6 | click | id=facetapi-link--556 |  | 
    self.driver.find_element(By.ID, "facetapi-link--556").click()
    # 7 | click | css=#block-facetapi-qjejqftyhn5j90hmbhoy3t0dllnssrjt > .block-title |  | 
    self.driver.find_element(By.CSS_SELECTOR, "#block-facetapi-qjejqftyhn5j90hmbhoy3t0dllnssrjt > .block-title").click()
    # 8 | click | linkText=Log out |  | 
    self.driver.find_element(By.LINK_TEXT, "Log out").click()
    # 9 | setWindowSize | 960x1008 |  | 
    self.driver.set_window_size(960, 1008)

### Anon.T Anonymous TaskSet
class AnonymousTaskSet(TaskSet):

    ## Anon.1.0 Random URLs from Homepage
    def anon_index_page(self, path="/"):
        # Using PyQuery, we look for anchor elements from the homepage (or any path) 
        r = self.client.get("/")
        pq = PyQuery(r.content)
        link_elements = pq("a")

        self.urls_on_current_page = [] # Pass the results into an array.

        # A loop reads the array and randomly picks a path 
        for l in link_elements:
            if "href" in l.attrib:
                url = l.attrib["href"]
                if url != "/user/logout":
                    # Ensure we only run links of the target site, excluding specific domains too
                    if url != "//dev-ps-loadtest-dummy.pantheonsite.io" and url is not None and "#" not in url and (url.startswith('http://dev-ps-loadtest-dummy.pantheonsite.io') or url.startswith('/')):
                        self.urls_on_current_page.append(l.attrib["href"])\
                        
    @task(1) 
    def load_anon_index_page(self):
        self.anon_index_page("/")
        count = 0
        while (count < 10):
            count = count + 1
            url = random.choice(self.urls_on_current_page)
            print("Calling ", url)
            self.client.get(url)
    ## Anon.1.0 End
    

    ## Anon.2.0 XML Sitemap Random pick
    def extract_sitemap(self, path="/sitemap.xml"):
        r = self.client.get("/sitemap.xml")
        locs = BeautifulSoup(r.text, 'lxml') # Pre-req is to use 'from bs4 import BeautifulSoup'
        self.urls_on_sitemap = [] # Pass the results into an array.
        for loc in locs.select('url > loc'):
            self.urls_on_sitemap.append(loc.text)
            
    @task(1) 
    def anon_random_sitemap(self):
        self.extract_sitemap("/")
        count = 0
        while (count < 10):
            count = count + 1
            url = random.choice(self.urls_on_sitemap)
            print("Calling ", url)
            self.client.get(url)
    ## Anon.2.0 End


    ## Anon.3.0 Core Search Form Submission
    @task(1)
    def search(self):
        f = open('./search/umami.txt', 'r')
        searchWords = {}
        i = 0
        for X in f:
            searchWords[i] = X.rstrip()
            i = i+1
        print(len(searchWords))
        # Search Paths
        #url = "/search/node/"+random.choice(searchWords) # Search path with Clean URL search
        url = "/en/search/node?keys="+random.choice(searchWords) # Search path with Clean URL search
        print("Calling ", url)
        r = self.client.get(url)
    ## Anon.3.0 End


    ## Anon.4.0 User Login Page for Drupal 8
    @task(1)
    def login(self):
        #login function using http session handler. Modify for the actual login path
        request_path = "/user/login"
        self.client.post(request_path, {
            "name": "umami",
            "pass": "umami",
            "form_id": "user_login_form",
            "form_build_id": get_form_build_id(self, request_path),
            "op": "Log in"
        })
    ## Anon.4.0 End

    
    ## Anon.5.0 User Registration Form
    #  Assuming that Public Registration is enabled for the site
    @task(1)
    def user_register(self):
        request_path = "/user/register"
    
        # Generate random email, or pick random email from list
        random_email = "test-" + "".join(random.choice(string.ascii_lowercase) for i in range(7)) + "@ps-pantheontest.com"
        random_name = "".join(random.choice(string.ascii_lowercase) for i in range(12)) 

        # Submit Registration Information
        self.client.post(request_path, {
            "mail": random_email,
            "name": random_name, # Add more required fields if needed
            "form_id": "user_register_form",
            "form_build_id": get_form_build_id(self,request_path),
            "op": "Create new account"
        })
    ## Anon.5.0 End


    ## Anon.6.0 WebForm Submissions
    @task(1)
    def webform_submit(self):
        request_path = "/chef-application"
        self.client.post(request_path, {
            "contact[name]": "My Name",
            "contact[company]": "My Company",
            "contact[email]": "example@email.com",
            "contact[phone]": "09088772988",
            "contact[address]": "Address 1 Entry",
            "contact[address_2]": "Address 2 Entry",
            "contact[city]": "San Francisco",
            "contact[state_province]": "California",
            "contact[postal_code]": "90210",
            "contact[country]": "Philippines",
            "form_id": "webform_submission_demo_application_node_130_add_form",
            "form_build_id": get_form_build_id(self,request_path),
            "op": "Submit"
        })
    ## Anon.6.0 End
      

    ## Anon.7.0 API Endpoints (REST/JSON:API)
    ## TODO - actual endpoints functions and helpers
    def retrieve_all_endpoints(self):
        self.client.get("/json/api/endpoints/list")

    @task(1)
    def retrieve_endpoint(self):
        self.client.get("/json/api/specific/path")
    ## Anon.7.0 End 

## Anon.U Anonymous User
class AnonymousUser(HttpLocust):
    host = os.getenv('TARGET_URL', "http://dev-ps-loadtest-dummy.pantheonsite.io")
    task_set = AnonymousTaskSet
    wait_time = between(1, 3)


## Auth.T Authenticated TaskSet
class AuthenticatedTaskSet(TaskSet):
    ## Auth.1.0 User Login Form (Drupal 7 and WordPress)
    # @task(1)
    # def login_user(self):
    #     #login function using http session handler. modify as needed.
    #     self.client.get("/user/login") 
    #     self.client.post("/user/login", {"name":"umami", "pass":"umami", "form_id": "user_login", "op": "Log in"})

    ## Auth.1.1 User Login Function and Form (Drupal 8)
    def on_start(self):
        self.login() # on_start is called when a Locust start before, any task is scheduled

    def login(self):
        #login function using http session handler. Modify for the actual login path
        request_path = "/user/login"
        self.client.post(request_path, {
            "name": "umami",
            "pass": "umami",
            "form_id": "user_login_form",
            "form_build_id": get_form_build_id(self, request_path),
            "op": "Log in"
        })
    
    def on_stop(self):
        self.client.get("/user/logout")

    ## Auth.1.1 User Login then Navigate Site. Add some pages to load.
    @task(1)
    def navigate_site_steps(self):
        self.client.get("/")
        self.client.get("/en/user/4/edit")
        # Add more paths or pages here    
    ## Auth.1.0 End

    ## 2.0 Create an Article
    @task(1)
    def create_node_article(self):
        ## TODO
        # Add "files[field_image_0]": get_lorem_picsum(),
        
        # Create new Faker instance and text
        fake = Faker() 
        article_title = fake.format('sentence')
        article_body = fake.format('text')
        article_tags = fake.format('word')
        print(article_title)
        print(article_body)
        print(article_tags)

        request_path = "/node/add/article"
        self.client.post(request_path, {
            "title[0][value]": article_title,
            "body[0][value]": article_body,
            "field_tags[target_id]": article_tags,
            "langcode[0][value]": "en",
            "moderation_state[0][state]": "published", ## Depending on the roles and permissions, this might not work
            "form_id": "node_article_form",
            "form_token": get_form_token(self, request_path),
            "form_build_id": get_form_build_id(self, request_path),
            "op": "Save"
        })
        
    ## 2.0 End

    ## 3.0 Adding Comments to Articles
    # Scenario: Configured to only post as Authenticated
    # Make sure that BigPipe is turned-off in Drupal 8 
    # The response content is not complete and unable to be parsed by lxml
    @task(100)
    def create_node_article_comment(self):
        fake = Faker() # Create new Faker instance
        
        # Find a random article from a page
        # self, Articles or News page, the "class" for Article Links, and the Comment Form ID for all comments
        random_comment = get_random_article(self, "/articles", "read-more__link", "comment-form")
        comment_post_path = random_comment["random_article_path"]
        random_article_path = random_comment["comment_post_path"]

        # Post the Comment to the selected 
        self.client.post(comment_post_path, {
            "subject[0][value]": fake.sentence(),
            "comment_body[0][value]": fake.text(),
            "langcode[0][value]": "en",
            "form_id": "comment_article_comment_form", ## Change depending on the Content type machine name
            "form_token": get_form_token(self, random_article_path),
            "form_build_id": get_form_build_id(self, random_article_path),
            "op": "Save"
        })
    ## 3.0 End

    ## 4.0 Create an article via JSON:API
    ## 4.0 End

    ## 5.0 Commerce Shopping Cart Steps
    ## 5.0 End

# Auth.U Authenticated User
class AuthenticatedUser(HttpLocust):
    host = os.getenv('TARGET_URL', "http://dev-ps-loadtest-dummy.pantheonsite.io")
    task_set = AuthenticatedTaskSet
    wait_time = between(6, 20)

## Adv.T Custom Scripts, CasperJS, Selenium, PyTest etc
class AdvancedTaskSet(TaskSet):

    ## Adv.6.0 Recorded Selenium Steps
    @task(1)
    def pytest(self):
         start_time = time.time()
         os.system("pytest locustfile.py")
         total_time = int((time.time() - start_time) * 1000)
         events.request_success.fire(
             request_type="pytest",
             name="login-search",
             response_time=total_time,
             response_length=0
         )

    #@task(1)
    #def selenium(self):
    #    start_time = time.time()
    #     os.system('selenium-side-runner -c "goog:chromeOptions.args=[--headless,--nogpu] browserName=chrome" KEDB-test.side')
    #     total_time = int((time.time() - start_time) * 1000)
    #     events.request_success.fire(
    #         request_type="selenium",
    #         name="login-search",
    #         response_time=total_time,
    #         response_length=0
    #     )

## Adv.U Advanced User Setting
# class AdvancedUser(HttpLocust):
#     host = os.getenv('TARGET_URL', "http://dev-ps-loadtest-dummy.pantheonsite.io")
#     task_set = AdvancedTaskSet
#     wait_time = between(1, 3)