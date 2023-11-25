# Udyog Portal
A website which connects employers and candidates. Built using Django Framework and MySQL.

## Features for employers
1) Post job openings.
2) Recieve applicantions on the job post with access to candidate's full profile and resume. And, select/reject them.
3) Shortlist candidates for further rounds.
4) Search for relevant candidates.
5) Search through entire resume database and have access to all resumes.

## Features for candidates
1) Build the profile with sills and attach resume.
2) Search for jobs with various filters.
3) Save a job post or apply for jobs.
4) See the status of applications.
5) Get relevant jobs.

## Development instructions

* Create a python virtual environment<br>
  ```python -m venv ~/.virtualenv/udyog-venv```
* Activate the environment<br>
  ```source ~/.virtualenv/udyog-venv/bin/activate```
* Clone this repository<br>
  ```git clone https://github.com/Prajna-Ramamurthy/Udyog-Portal.git```
* Install the required packages in the newly created venv as per requirements.txt<br>
  ```cd Udyog-Portal```<br>
  ```pip install -r requirements.txt```
* Go to the top level udyog project directory (where manage.py file is located)<br>
  ```cd udyog```
* Create static files<br>
  ```python manage.py collectstatic```
* Prepare migration files<br>
  ```python manage.py makemigrations```
* Create migration files<br>
  ```python manage.py migrate```
* Run the server<br>
  ```python manage.py runserver```
