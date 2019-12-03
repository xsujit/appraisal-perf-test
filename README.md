# Locust performance test for appraisal application
Use following command to run the test
locust -f src/test/locustfile.py --no-web -c 50 -r 2 --run-time 1m
