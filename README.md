FAIRShake
========

A web interface for the scoring of biomedical digital objects by user evaluation
according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability.

Currently available at: http://amp.pharm.mssm.edu/fairshake

Setup
---------

Requirements:
* Flask framework for Python
    * Extensions required: Flask-Login, Flask-MySQL
    * `pip install flask`
    * `pip install flask-login`
    * `pip install flask-mysql`
* MySQL for database management
    * Download at https://dev.mysql.com/downloads/mysql/

Components
--------

The MySQL database stores information on projects, resources, questions, evaluations, averages, and users.
The Python `app.py` file is structured with Flask. It manages routes, connects to MySQL and executes database queries,
manages account function (login, User objects), and passes variables into the HTML templates.
The HTML templates build the webpages.

MySQL Tables
---------

* average

    |    column     |  type |     description   |
    | ------------- | ----- | -------------     |
    | resource_id  | int    |
    | q_id         | int    |
    | avg          | float  |   Between -1 and 1
    |  project_id  | int    |


* evaluation
    |    column     |  type |     description   |
    | ------------- | ----- | -------------     |
    | user_id       | int   |
    | resource_id   | int   |
    | q_id          | int   |
    | answer        | text  |   'yes' or 'no' or 'yesbut'
    | comment       | text  |   Currently only if `answer` is 'yesbut'
    | project_id    | int   |

* project
    |    column           |  type |     description   |
    | -------------       | ----- | -------------     |
    | project_id          | int   |  int, primary key, auto-increment
    | project_name        | text  |
    | project_description | text  |
    | project_img         | text  |  URL for picture to display for project

* question
    |  column  |  type |     description   |
    | ---      | ----- | -------------     |
    | q_id     | int   |  int, primary key, auto-increment
    | num      | int   |  Number within set (e.g. 1-16)
    | version  | int   |  Default: 1
    | content  | text  |
    | F        | text  |  'F'
    | A        | text  |  'A'
    | I        | text  |  'I'
    | R        | text  |  'R'
    | res_type | text  |  Questions are associated with resource type


* resource
    |  column        |  type |     description   |
    | -----          | ----- | -------------     |
    | resource_id    | int   |  int, primary key, auto-increment
    | resource_name  | text  |
    | url            | text  |  URL of resource homepage to link to
    | resource_type  | text  |
    | description    | text  |
    | project_id     | int   |  Resources are associated with projects (currently one to many relationship represented)

* user
    |  column        |  type |     description   |
    | -----          | ----- | -------------     |
    | user_id        | int   |  int, primary key, auto-increment
    | username       | text  |
    | password       | text  |  URL of resource homepage to link to
    | first_name     | text  |
    | last_name      | text  |
    | role_evaluator | text  |   'role_evaluator'
    | role_starter   | text  | 'role_starter'


Chrome extension related FAIRShake routes
---------
* `/api/chrome_extension/getQ`
    * Returns questions ordered 1-16 for this resource's type for insignia tooltip
* `/api/chrome_extension/getAvg`
    * Returns average scores ordered 1-16 for this resource for insignia color and score value
* `/redirectedFromExt`
    * For insignia click - redirects to FAIRShake evaluation form
* `/chromeextension`
    * For Chrome extension download from website

Adding pages to Chrome extension
----------

* Create project (e.g. repositories listed on DataMed):
    * Enter project into MySQL database manually
        * `insert into project (project_name,project_description,user_id,project_img)
        values ('DataMed repositories','Repositories listed on DataMed', 'https://datamed.org/img/biocaddie_png2.png')`
    * Enter resources into MySQL database with Chrome extension click
        * Add resource pages to Chrome extension
        * Click on insignia inserted on resource landing pages. This automatically inserts resource into database
        (on insignia click, not when insignia appears on page).
    * Enter questions into MySQL database (if the resource type is new)
        * `insert into question (res_type,num,content,F)
        values ('Repository',1,'The structure of the repository etc.','F')`
        * `insert into question (res_type,num,content,F,A)
        values ('Repository',2,'The repository is available online.','F', 'A')`
* In Chrome extension:
    * Create `.js` file in extension for this website
    * Insert `insigform` into desired spot for insignia
    * `insigform` hidden input values:
        * Resource name, URL, description (using jQuery)
        * Type of resource
        * Source webpage (e.g. DataMed) to be used for project identification in `app.py`
* In `app.py`:
    * In `/redirectedFromExt`, add `elif` statement for new source webpage with new project number

Features in Progress
--------------

* Start a project
    * There is a page set up for users to start a project (`startproject.html`) at `/startproject`,
    but it is not fully implemented. If you try to submit a project, you will be stopped and receive a warning 'In progress.'
    * Although the page allows you to select a number of questions for a project other than 16,
    this is currently not implemented if you actually submit the project. (Some HTML templates or parts of `app.py` may
    use 16 as the number of questions.)
    * `role_starter`
        * Currently, there is no difference in `role_evaluator` and `role_starter` accounts. Both can technically
        start projects (by accessing `/startproject` and submitting a project).
* Organization of database
    * Categorizing questions as FAIR
        * The FAIR questions for each type are associated with one or more foundational F/A/I/R principles.
        There are 'F','A','I','R' columns in the `question` table of the MySQL database to indicate this.
        This could be used for analytics purposes later.
    * Project-resource relationship
        * Currently, the database represents the project-resource relationship as one to many.
        However, as more projects are added, there is a possibility that a resource may fit in multiple projects.
        This is a many to many relationship. Later, a `project2resource` table can be added to more
        accurately represent this relationship.
    * `Project_id` in MySQL database
        * Some tables in the MySQL database may include a `project_id` column that can be removed.
* User account
    * Connection to email (activation, password retrieval)
    * Sign in with Google or Facebook
    * Personalization features (avatar, about)
* Finding a resource in the database to pull for Chrome extension
    * Since some resources may belong to multiple projects, the Chrome extension should recognize this. Currently,
    the Chrome extension pulls resource averages and evaluations based on exact URL. So it will not recognize the
    same resource if one project's page records the URL slightly differently from another project's page.
    For example, one URL may have a '/' at the end, while another does not. Or one may have 'www' at the beginning.
    Or 'http' vs 'https'. Ways to address this: search by name, use RegEx on URL search.
* Login issue from Chrome extension
    * Users must log in to submit evaluations. If a visitor is taken to the FAIRShake evaluation form through the
    Chrome extension, they may not be logged in, especially if they are new to the site.
* Error handling
    * There may be places where errors are not handled consistently.
    There is an error template (`errors.html`) set up. Example in `app.py`:
    `return render_template('error.html',errormsg='Invalid URL.')`