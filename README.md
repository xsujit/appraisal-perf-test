# Locust performance test for appraisal application
Use following command to run the test
Tested on locust 1.1.1
locust -f src/test/locustfile.py --headless -u 1 -r 1 --run-time 1m --logfile locust.log