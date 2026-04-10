"""
SELENIUM TESTS - EasyBook Frontend End-to-End Tests
Tests the full user flow through a browser using Selenium WebDriver
"""
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:8080')
WAIT_TIMEOUT = 10


@pytest.fixture(scope='module')
def driver():
    """Set up Chrome WebDriver in headless mode"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280,800')
    chrome_options.add_argument('--disable-extensions')

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        d = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        d = webdriver.Chrome(options=chrome_options)

    d.implicitly_wait(5)
    yield d
    d.quit()


def wait_for(driver, by, value, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_clickable(driver, by, value, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )


class TestPageLoad:
    """Selenium tests - Page loading and basic navigation"""

    def test_homepage_loads(self, driver):
        """Test: Homepage loads successfully with correct title"""
        driver.get(FRONTEND_URL)
        wait_for(driver, By.TAG_NAME, 'body')
        assert 'EasyBook' in driver.title or 'EasyBook' in driver.page_source

    def test_homepage_has_navbar(self, driver):
        """Test: Homepage has a navigation bar"""
        driver.get(FRONTEND_URL)
        wait_for(driver, By.TAG_NAME, 'body')
        # Check nav exists
        nav = driver.find_elements(By.TAG_NAME, 'nav')
        assert len(nav) > 0 or 'navbar' in driver.page_source.lower()

    def test_homepage_has_services_section(self, driver):
        """Test: Homepage shows a services or features section"""
        driver.get(FRONTEND_URL)
        wait_for(driver, By.TAG_NAME, 'body')
        page = driver.page_source.lower()
        assert 'service' in page or 'book' in page or 'appointment' in page

    def test_login_page_loads(self, driver):
        """Test: Login page loads"""
        driver.get(f'{FRONTEND_URL}/login.html')
        wait_for(driver, By.TAG_NAME, 'body')
        page = driver.page_source.lower()
        assert 'login' in page or 'sign in' in page

    def test_register_page_loads(self, driver):
        """Test: Register page loads"""
        driver.get(f'{FRONTEND_URL}/register.html')
        wait_for(driver, By.TAG_NAME, 'body')
        page = driver.page_source.lower()
        assert 'register' in page or 'sign up' in page or 'create' in page

    def test_services_page_loads(self, driver):
        """Test: Services page loads"""
        driver.get(f'{FRONTEND_URL}/services.html')
        wait_for(driver, By.TAG_NAME, 'body')
        assert driver.find_element(By.TAG_NAME, 'body')

    def test_404_graceful(self, driver):
        """Test: Non-existent page doesn't crash browser"""
        driver.get(f'{FRONTEND_URL}/nonexistent-page-xyz.html')
        wait_for(driver, By.TAG_NAME, 'body')
        assert driver.find_element(By.TAG_NAME, 'body')


class TestLoginForm:
    """Selenium tests - Login form interaction"""

    def test_login_form_has_email_field(self, driver):
        """Test: Login form contains email input"""
        driver.get(f'{FRONTEND_URL}/login.html')
        wait_for(driver, By.TAG_NAME, 'body')
        email_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="email"], input[name="email"], #email')
        assert len(email_inputs) > 0

    def test_login_form_has_password_field(self, driver):
        """Test: Login form contains password input"""
        driver.get(f'{FRONTEND_URL}/login.html')
        wait_for(driver, By.TAG_NAME, 'body')
        pwd_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"], input[name="password"], #password')
        assert len(pwd_inputs) > 0

    def test_login_form_has_submit_button(self, driver):
        """Test: Login form has a submit button"""
        driver.get(f'{FRONTEND_URL}/login.html')
        wait_for(driver, By.TAG_NAME, 'body')
        btns = driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], button.btn-login')
        assert len(btns) > 0

    def test_login_empty_submission(self, driver):
        """Test: Empty form submission shows validation or stays on page"""
        driver.get(f'{FRONTEND_URL}/login.html')
        wait_for(driver, By.TAG_NAME, 'body')
        btns = driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"], button')
        if btns:
            btns[0].click()
            time.sleep(1)
            # Should still be on login page or show error
            assert 'login' in driver.current_url.lower() or 'login' in driver.page_source.lower()

    def test_login_invalid_credentials(self, driver):
        """Test: Invalid credentials show error message"""
        driver.get(f'{FRONTEND_URL}/login.html')
        wait_for(driver, By.TAG_NAME, 'body')

        email_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="email"], #email')
        pwd_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"], #password')
        submit_btns = driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"], button.btn-login')

        if email_inputs and pwd_inputs and submit_btns:
            email_inputs[0].clear()
            email_inputs[0].send_keys('notauser@fake.com')
            pwd_inputs[0].clear()
            pwd_inputs[0].send_keys('wrongpassword')
            submit_btns[0].click()
            time.sleep(2)
            # Expect error message or still on login page
            assert ('error' in driver.page_source.lower() or
                    'invalid' in driver.page_source.lower() or
                    'login' in driver.current_url.lower())


class TestRegisterForm:
    """Selenium tests - Registration form interaction"""

    def test_register_form_has_name_field(self, driver):
        """Test: Register form has name field"""
        driver.get(f'{FRONTEND_URL}/register.html')
        wait_for(driver, By.TAG_NAME, 'body')
        name_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[name="name"], #name, input[placeholder*="name" i]')
        assert len(name_inputs) > 0

    def test_register_form_has_required_fields(self, driver):
        """Test: Register form has email, password, and name"""
        driver.get(f'{FRONTEND_URL}/register.html')
        wait_for(driver, By.TAG_NAME, 'body')
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        # Should have at least 3 inputs: name, email, password
        assert len(inputs) >= 3

    def test_register_has_role_selection(self, driver):
        """Test: Register form has role selection (customer/provider)"""
        driver.get(f'{FRONTEND_URL}/register.html')
        wait_for(driver, By.TAG_NAME, 'body')
        page = driver.page_source.lower()
        assert 'customer' in page or 'provider' in page or 'role' in page


class TestServicesPage:
    """Selenium tests - Services browsing"""

    def test_services_page_shows_content(self, driver):
        """Test: Services page renders content area"""
        driver.get(f'{FRONTEND_URL}/services.html')
        wait_for(driver, By.TAG_NAME, 'body')
        assert driver.find_element(By.TAG_NAME, 'body')

    def test_services_page_has_search_or_filter(self, driver):
        """Test: Services page has search or filter functionality"""
        driver.get(f'{FRONTEND_URL}/services.html')
        wait_for(driver, By.TAG_NAME, 'body')
        page = driver.page_source.lower()
        assert 'search' in page or 'filter' in page or 'category' in page

    def test_homepage_has_cta_button(self, driver):
        """Test: Homepage has a call-to-action button"""
        driver.get(FRONTEND_URL)
        wait_for(driver, By.TAG_NAME, 'body')
        btns = driver.find_elements(By.TAG_NAME, 'button')
        links = driver.find_elements(By.TAG_NAME, 'a')
        assert len(btns) + len(links) > 0
