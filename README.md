# course-tracker
The project fetches statuses of courses offered by NCSU

Script start:
- tracker.py

Setup:
- Pull the code
- Setup python environment
- Set email address and password as env variables to send emails
- Enter courses to track in student-courses.json for the script to track them

#### Script Working:
- Deployed to heroku
- Executes every 12 hours with status of every course subscribed

##### Phase 2 (complete):
- Fetch course statuses from NCSU every 2 hours
- If status change - notify subscribed users
- CRON job everyday at 10PM IST to send email with statuses

##### Phase 3:
- Subscribe to course status changes from NCSU site
- Update immediately on status change
- Ignore online courses
