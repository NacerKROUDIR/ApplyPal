from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import time


class Scraper:
    def __init__(self):
        self.date_posted = "Any time"
        self.experience_level = "Any"
        self.company = ""

        self.email_addr = os.getenv("LINKEDIN_EMAIL_TEST")
        self.password = os.getenv("LINKEDIN_PASSWORD")

        print("Starting...")

        self.driver = webdriver.Safari()
        self.wait = WebDriverWait(self.driver, 10)

        self.driver.get("https://www.linkedin.com/login/")
        self.sign_in()
        
    def sign_in(self):
        if not self.email_addr or not self.password:
            raise ValueError("Missing email or password environment variables")

        email_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_field.clear()
        email_field.send_keys(self.email_addr)

        password_field = self.driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(self.password)

        sign_in_button = self.driver.find_element(By.CSS_SELECTOR, '#organic-div > form > div.login__form_action_container > button')
        sign_in_button.click()
        time.sleep(3)
        self.driver.get("https://www.linkedin.com/jobs/")


    def search(self, job, region):
        job_field = self.driver.find_element(By.XPATH, '//input[@class="jobs-search-box__text-input jobs-search-box__keyboard-text-input jobs-search-global-typeahead__input"]')
        job_field.clear()
        job_field.send_keys(job)
        job_field.send_keys(Keys.RETURN)
        time.sleep(5)
        region_field = self.driver.find_element(By.XPATH, '//input[@autocomplete="address-level2"]')
        region_field.clear()
        region_field.send_keys(region)
        time.sleep(1)
        region_field.send_keys(Keys.RETURN)

    def apply_date_posted_filter(self):
        date_posted_field = self.driver.find_element(By.ID, "searchFilter_timePostedRange")
        date_posted_field.click()

        fieldset_element = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, '//fieldset[@class="reusable-search-filters-trigger-dropdown__container"]'))
            )
        options = fieldset_element.find_elements(By.TAG_NAME, 'p')
        
        if self.date_posted == "Any time":
            options[0].click()
        elif self.date_posted == "Past month":
            options[1].click()
        elif self.date_posted == "Past week":
            options[2].click()
        elif self.date_posted == "Past 24 hours":
            options[3].click()
        else:
            raise(ValueError("Unknown filter value for date_posted"))
        
        show_results_button = fieldset_element.find_elements(By.TAG_NAME, 'button')[-1]
        show_results_button.click()

        time.sleep(2)
            

    def apply_experience_level_filter(self):
        experience_level_field = self.driver.find_element(By.ID, "searchFilter_experience")
        experience_level_field.click()

        fieldset_element = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, '//fieldset[@class="reusable-search-filters-trigger-dropdown__container"]'))
            )
        options = fieldset_element.find_elements(By.TAG_NAME, 'p')
        print(options)
        if self.experience_level == "Internship":
            options[0].click()
        elif self.experience_level == "Entry level":
            options[1].click()
        elif self.experience_level == "Associate":
            options[2].click()
        elif self.experience_level == "Mid-senior level":
            options[3].click()
        elif self.experience_level == "Director":
            options[4].click()
        elif self.experience_level == "Executive":
            options[5].click()
        else:
            raise(ValueError("Unknown filter value for experiece_level"))
        
        show_results_button = fieldset_element.find_elements(By.TAG_NAME, 'button')[-1]
        show_results_button.click()

        time.sleep(2)

    def apply_company_filter(self):
        experience_level_field = self.driver.find_element(By.ID, "searchFilter_company")
        experience_level_field.click()

        fieldset_element = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, '//fieldset[@class="reusable-search-filters-trigger-dropdown__container"]'))
            )

        input_field = fieldset_element.find_element(By.XPATH, '//input[@placeholder="Ajouter une entreprise"]')
        input_field.clear()
        input_field.send_keys(self.company)

        show_results_button = fieldset_element.find_elements(By.TAG_NAME, 'button')[-1]
        show_results_button.click()

        time.sleep(1)
    
    
    def get_jobs_links(self):
        print("Getting jobs links...")
        jobs = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, '//ul[@class="scaffold-layout__list-container"]'))
            )
        jobs = jobs.find_elements(By.TAG_NAME, "a")
        self.jobs_links = [job.get_attribute('href') for job in jobs]
        self.n_jobs = len(self.jobs_links)
    

    def extract_info(self):
        jobs = []
        for i, job_link in enumerate(self.jobs_links):
            print(f"getting info for job {i+1}/{self.n_jobs}")
            self.driver.get(job_link)
            job_description = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, '//div[@class="mt4"]'))
                ).text.strip()
            company_info = self.driver.find_element(By.XPATH, '//div[@class="job-details-jobs-unified-top-card__company-name"]')
            company_name = company_info.text.strip()
            company_account = company_info.find_element(By.TAG_NAME, 'a').get_attribute('href')
            job_title = self.driver.find_element(By.XPATH, '//h1[@class="t-24 t-bold inline"]').text.strip()
            other_info_tag = self.driver.find_element(By.XPATH, '//div[@class="t-black--light mt2"]')
            other_info_spans = other_info_tag.find_elements(By.TAG_NAME, 'span')
            location = other_info_spans[0].text
            date_posted = other_info_spans[5].text
            n_applicants = other_info_spans[9].text
            skills = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, '//div[@id="how-you-match-card-container"]/section[2]/div/div/div/div/a'))
            ).text.strip()
            job = [company_name, company_account, location, date_posted, n_applicants, skills, job_title, job_description[:100]]
            for l in job:
                print(l)
                print("--------------------------------")
            print("*"*100)
            print("*"*100)
            jobs.append(job)
        return jobs


    def scrape(self, job:str, region:str, date_posted: str, experience_level: str, company: str) -> str:
        try:
            self.search(job, region)

            if date_posted != self.date_posted:
                self.date_posted = date_posted
                self.apply_date_posted_filter()
            if experience_level != self.experience_level:
                self.experience_level = experience_level
                self.apply_experience_level_filter()
            if company != self.company:
                self.company = company
                self.apply_company_filter()
            time.sleep(2)
            self.get_jobs_links()

            jobs = self.extract_info()
            # time.sleep(500)
            return jobs
        finally:
            pass
            self.driver.quit()


def extract_body(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.body
    if body:
        for script_or_style in body(['script', 'style']):
            script_or_style.extract()

        cleaned_body = body.get_text(separator='\n')
        cleaned_body = "\n".join(line.strip() for line in cleaned_body.splitlines() if line.strip())
        return cleaned_body
    return ""


def split_body(body, split_size=100):
    return [
        body[i: i+split_size] for i in range(0, len(body), split_size)
    ]
