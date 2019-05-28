# course-tracker
The project fetches statuses of courses offered by NCSU

Setup:
- Pull the code
- Setup python environment
- Set email address and password as env variables to send emails
- Enter courses to track in student-courses.json for the script to track them

Script Working:
- Deployed to heroku
- Executes every 12 hours with status of every course subscribed

Next phase:
- Fetch course statuses from NCSU every 2 hours
- If status change - notify subscribed users
- CRON job everyday at 10PM IST to send email with statuses
