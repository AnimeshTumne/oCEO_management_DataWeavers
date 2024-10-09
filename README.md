# oCEO Management System
**Status:** Final Improvements and Deployment in Progress
This repository contains a simple yet elegant implementation of the on-Campus Employment Opportunities (oCEO) at IITGN. It facilitates easy creation and deletion of jobs by the faculty offering them, and an easy view of payment processing status for a student availing the opportunity.

## Front End:
Our frontend, developed using Flask, Flex and Bootstrap, facilitates easy user experience and takes into account the needs of each user separately. 


## Back End:
Our backend is based on flask in python. It uses flask inbuilt methods to redirect and route our pages on the webapp.

*How to use?* 

Import into mySQL, the final version of our database, ```oCEO_v6.sql```. Import this file into your database using server>import>import from self-contained file option.

Go into the ```main_project``` folder. After this, run ```main_app.py``` file, and create a new student/professor user using the ```New User``` button. After this, login using created credentials through the ```Student``` or ```Professor``` buttons. After login, you can view various operations that can be done for that particular usertype.

For logging-in using others, which contains Admin, oCEO coordinator, Dean SA and Student Affairs Junior Superintendant, you have four different email ids:

- dean@iitgn.ac.in
- sa_js@iitgn.ac.in
- joycee@iitgn.ac.in (as the oCEO coordinator)
- admin@iitgn.ac.in

password is same for all - 'admin'. Please select correct user type, or otherwise you would be redirected to a "bad credentials" page.
