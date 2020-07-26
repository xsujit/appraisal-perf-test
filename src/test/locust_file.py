from locust import HttpUser, TaskSet, between, task, events
import logging
import requests
import csv


class AppraisalTask(TaskSet):

    user_num = 1
    test_users_index = 0

    def __init__(self, parent):
        super().__init__(parent)
        # Setup the instance variables
        self.user_num = AppraisalTask.user_num
        AppraisalTask.user_num += 1
        test_users_len = len(AppraisalUser.test_users)
        if AppraisalTask.test_users_index >= test_users_len:
            AppraisalTask.test_users_index = 0
        self.user_email = AppraisalUser.test_users[AppraisalTask.test_users_index][1]
        AppraisalTask.test_users_index += 1

    def on_start(self):
        # Login to the appraisal application
        logging.info("on_start called")
        r = self.client.post("/login", {"username": self.user_email, "password": "password"})
        assert r.status_code == 200, "Unexpected status code {}".format(r.status_code)

    def on_stop(self):
        r = self.client.get("/logout", allow_redirects=False)
        assert r.status_code == 302, "Unexpected status code {}".format(r.status_code)
        redirect_url = r.headers['Location']
        assert "logout-success" in redirect_url, "logout-success not found in logout url, found {}".format(redirect_url)
        requests.get(redirect_url)

    @task(1)
    def index(self):
        logging.info("User: {}".format(self.user_email))
        r = self.client.get("/")
        assert r.status_code == 200, "Unexpected status code {}".format(r.status_code)

    @task(2)
    def profile(self):
        r = self.client.get("/appraisal")
        assert r.status_code == 200 and "Project Title" in r.text

    @task(2)
    def team(self):
        r = self.client.get("/team")
        assert r.status_code == 200 and "Here you can view all your team members" in r.text


class AppraisalUser(HttpUser):

    host = "http://localhost:8080"
    tasks = [AppraisalTask]
    wait_time = between(1, 1)
    test_users = []

    @staticmethod
    @events.test_start.add_listener
    def setup(environment, **kwargs):
        logging.info("*** Test Starting ***")
        host_name = AppraisalUser.host
        target_users = environment.parsed_options.__dict__['num_users']
        logging.info("Target users: {}".format(target_users))
        users_registered = 0
        with open('test_users_v2.csv', newline='') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == target_users:
                    break
                user_email = '{}@gmail.com'.format(row[1])
                user_details = [row[0], user_email]
                AppraisalUser.test_users.append(user_details)
                users_registered += 1
                reg_payload = {'firstName': 'Test', 'lastName': 'Best', 'username': user_email, 'password': 'password',
                               'employeeId': '{}'.format(row[0]), 'projectId': '2', 'location': 'Bradford'}
                logging.info("Registering new user: {}".format(user_email))
                requests.post('{}/register'.format(host_name), params=reg_payload)
        login_payload = {'username': 'jack.bauer@mastek.com', 'password': 'password1'}
        s = requests.Session()
        s.post('{}/login'.format(host_name), params=login_payload)
        payload = {}
        for i in range(0, users_registered):
            f = {"employees[{}].id".format(i): "{}".format(i + 1),
                 "employees[{}].user.enabled".format(i): "true",
                 "_employees[{}].user.enabled".format(i): "on"}
            payload.update(f)
        s.post('{}/admin/user'.format(host_name), params=payload)
        r = s.get("{}/logout".format(host_name), allow_redirects=False)
        logging.info("Status code: {}".format(r.status_code))

    @staticmethod
    @events.test_stop.add_listener
    def teardown(**kwargs):
        logging.info("Test Stopping")

