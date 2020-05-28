from locust import HttpLocust, TaskSet, task, between
import requests


class UserBehavior(TaskSet):

    def on_start(self):
        self.login()

    def on_stop(self):
        self.logout()

    def login(self):
        r = requests.get("http://localhost:8080/appraisal", allow_redirects=False)
        redirect_url = r.headers['Location']
        url = redirect_url[redirect_url.rfind("/"):]
        r = self.client.post(url, {"username": "jack.bauer@mastek.com", "password": "password"})
        print(r.content)

    def logout(self):
        self.client.post("/logout", {"username": "jack.bauer@mastek.com", "password": "password"})

    @task(1)
    def index(self):
        self.client.get("/")

    @task(2)
    def profile(self):
        r = self.client.get("/appraisal")
        assert r.status_code == 200 and "Project Title" in r.text

    @task(2)
    def team(self):
        r = self.client.get("/team", headers={"content-type": "application/json"})
        assert r.status_code == 200 and "Here you can view all your team members" in r.text


class WebsiteUser(HttpLocust):

    @staticmethod
    def setup():
        print("setup called")

    @staticmethod
    def teardown():
        print("teardown  called")

    host = "http://localhost:8080"
    task_set = UserBehavior
    wait_time = between(10, 10)
