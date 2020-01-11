# Generated using Jinja2
# site proupnetic
# site 5efcbe5e-b8b9-429d-bd1f-2e552b3f646a
# org Tarkenton Enteprises
# org 1a641984-ee63-44d0-9dfb-74fb5bfcabad

import os
import string
import random
import time
import pytest
import json
import selenium
from locust import HttpLocust, TaskSet, task, events
from locust.clients import HttpSession
from pyquery import PyQuery


class MyTaskSet(TaskSet):
    
    # Include PyTest Files

    # Custom Locust Steps
    # Top Visited Files
    
    @task(40)
    def path_homepage(self):
        self.client.get("/courses/new-york-state-sexual-harassment-prevention-training/")
    
    @task(30)
    def path_homepage(self):
        self.client.get("/my-courses/")
    
    @task(10)
    def path_homepage(self):
        self.client.get("/group-management/")
    
    @task(10)
    def path_homepage(self):
        self.client.get("/employee-registration/")
    
    @task(10)
    def path_homepage(self):
        self.client.get("/")
    

    # Anonymous pages
    
    def anon_index_page(self, path="/"):
        r = self.client.get("/")
        pq = PyQuery(r.content)
        link_elements = pq("a")
        self.urls_on_current_page = []
        for l in link_elements:
            if "href" in l.attrib:
                url = l.attrib["href"]
                if url != "/user/logout":
                    #ensure internal link
                    if url != "//dev-ps-loadtest-dummy.pantheonsite.io" and url is not None and "#" not in url and (url.startswith('https://dev-ps-loadtest-dummy.pantheonsite.io') or url.startswith('/')):
                        self.urls_on_current_page.append(l.attrib["href"])\

    @task(10)
    def load_anon_index_page(self):
        self.anon_index_page("/")
        count = 0
        while (count < 10):
            count = count + 1
            url = random.choice(self.urls_on_current_page)
            print("Calling ", url)
            self.client.get(url)
    

    
class MyLocust(HttpLocust):
    host = os.getenv('TARGET_URL', "https://dev-ps-loadtest-dummy.pantheonsite.io")
    task_set = MyTaskSet
    min_wait = 1000
    max_wait = 3000