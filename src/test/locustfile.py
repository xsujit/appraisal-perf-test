from locust import HttpLocust, TaskSet, task, between
import certifi
import urllib3
import ssl

def cert_exists():
    with open(certifi.where()) as cr_file:
        if ssl.get_server_certificate(('localhost', 8443)) in cr_file.read():
            print("Cert exists in file")
            return True
        else:
            return False
            

if(cert_exists() != True):
    cert_file = open(certifi.where(), "a")        
    cert_file.write(ssl.get_server_certificate(('localhost', 8443)))
    cert_file.close()
        

class UserBehavior(TaskSet):

    def on_start(self):
        self.login()


    def on_stop(self):
        self.logout()

        
    def login(self):
        self.client.post("/login", {"username":"jack.bauer@mastek.com", "password":"password"}, verify=certifi.where())


    def logout(self):
        self.client.post("/logout", {"username":"jack.bauer@mastek.com", "password":"password"}, verify=certifi.where())


    @task(1)
    def index(self):
        self.client.get("/", verify=certifi.where())


    @task(2)
    def profile(self):
        r = self.client.get("/appraisal", verify=certifi.where())
        assert r.status_code == 200 and "Project Title" in r.text

        
    @task(2)
    def team(self):
        r = self.client.get("/team", verify=certifi.where(), headers={"content-type":"application/json"})        
        assert r.status_code == 200 and "Here you can view all your team members" in r.text


class WebsiteUser(HttpLocust):

    def setup(self):
        print("setup called")
    
    def teardown(self):
        print("teardown  called")
    
    host = "https://localhost:8443"
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)