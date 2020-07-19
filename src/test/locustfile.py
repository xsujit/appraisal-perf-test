from locust import HttpUser, TaskSet, between, task, events
import logging


class AppraisalTask(TaskSet):

    user_num = 0

    def __init__(self, parent):
        super().__init__(parent)
        AppraisalTask.user_num += 1
        self.user_num = AppraisalTask.user_num

    def on_start(self):
        logging.info("on_start for user: {}".format(self.user_num))
        r = self.client.post("/login", {"username": "jack.bauer@mastek.com", "password": "password1"})
        assert r.status_code == 200, "Unexpected status code {}".format(r.status_code)

    def on_stop(self):
        r = self.client.post("/logout", {"username": "jack.bauer@mastek.com", "password": "password1"})
        assert r.status_code == 200, "Unexpected status code {}".format(r.status_code)

    @task(1)
    def index(self):
        logging.info("User: {} | index".format(self.user_num))
        r = self.client.get("/")
        assert r.status_code == 200, "Unexpected status code {}".format(r.status_code)

    @task(2)
    def profile(self):
        logging.info("User: {} | profile".format(self.user_num))
        r = self.client.get("/appraisal")
        assert r.status_code == 200 and "Project Title" in r.text

    @task(2)
    def team(self):
        logging.info("User: {} | team".format(self.user_num))
        r = self.client.get("/team", headers={"content-type": "application/json"})
        assert r.status_code == 200 and "Here you can view all your team members" in r.text


class AppraisalUser(HttpUser):

    @staticmethod
    @events.test_start.add_listener
    def setup(**kwargs):
        print("*** Test Starting ***")
        logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')

    @staticmethod
    @events.test_stop.add_listener
    def teardown(**kwargs):
        print("*** Test Stopping ***")
        print("Total users: {}".format(AppraisalTask.user_num))

    host = "http://localhost:8080"
    tasks = [AppraisalTask]
    wait_time = between(1, 1)
