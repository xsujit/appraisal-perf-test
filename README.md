# Locust performance test for appraisal application
Before the test starts, users are registered based on the data in the csv file and saved in `test_users`. 
During the TaskSet init, email is fetched from `test_users` and stored in `self.user_email`. 
The `on_start` method uses this email to login.
 
Tested on locust 1.1.1

Use following command to run the test

locust -f locust_file.py --headless -u 1 -r 1 --run-time 1m

locust -f src/test/locust_file.py --headless -u 1 -r 1 --run-time 1m --logfile locust.log --stop-timeout 30