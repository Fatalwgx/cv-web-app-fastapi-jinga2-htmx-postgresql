

import time
from selene.support.shared import browser


def test_health_check(setup_browser):
    # browser = setup_browser
    browser.open('http://localhost:80/')
    time.sleep(15)

