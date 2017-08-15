FAIRShake
========

A web interface for the scoring of biomedical digital objects by user evaluation
according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability.

Prototype currently available at: http://amp.pharm.mssm.edu/fairshake

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
The Python `app.py` file uses Flask. It manages routes, connects to MySQL and executes database queries,
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
    | password       | text  |
    | first_name     | text  |
    | last_name      | text  |
    | role_evaluator | text  |   'role_evaluator'
    | role_starter   | text  | 'role_starter'


Current list of resource types
--------------
* Dataset
* Tool
* Repository

BioToolBay
-------
The FAIRShake FAIRness insignia with FAIRShake evaluation form connection on click (like the Chrome extension)
has been placed on the tool landing pages on BioToolBay. Any changes made to the Chrome extension `.js` file structure
should correspondingly be made for BioToolBay.

Chrome extension-related routes
---------
* `/api/chrome_extension/getQ`
    * Returns questions ordered 1-16 for this resource's type for insignia tooltip

* `/api/chrome_extension/getAvg`
    * Returns average scores ordered 1-16 for this resource for insignia color and score value

* `/redirectedFromExt`
    * For insignia click - redirects to FAIRShake evaluation form

* `/chromeextension`
    * For Chrome extension download from website

Adding webpages to Chrome extension
----------

* Until 'Start Project' or other appropriate automation implemented

* Create project (e.g. repositories listed on DataMed):
    * Enter project into MySQL database manually
        * `insert into project (project_name,project_description,user_id,project_img)
        values ('DataMed repositories','Repositories listed on DataMed', 'https://datamed.org/img/biocaddie_png2.png')`

* Enter questions into MySQL database (if the resource type is new)
    * `insert into question (res_type,num,content,F)
    values ('Repository',1,'The structure of the repository etc.','F')`
    * `insert into question (res_type,num,content,F,A)
    values ('Repository',2,'The repository is available online.','F', 'A')`

* Enter resources into MySQL database with Chrome extension click (or manually if not applicable)
    * Add resource pages to Chrome extension
        * In Chrome extension:
            * Create `.js` file in extension for this website
            * Insert `insigform` into desired spot for insignia
            * `insigform` hidden input values:
                * Resource name, URL, description (using jQuery)
                * Type of resource
                * Source webpage (e.g. DataMed) to be used for project identification in `app.py`

        * In `app.py`:
            * In `/redirectedFromExt`, add `elif` statement for new source webpage with new project number
                * `elif theSrc == 'DataMed':
                        cursor.execute(query2, (theName, theType, theURL, theDescrip, 4))
                        conx.commit()`

    * Click on insignia inserted on resource landing pages. This automatically inserts resource into database
    (on insignia click, not when insignia is placed on page through extension JavaScript
    with information from APIs).

    * or `insert into resource (resource_name,url,resource_type,description,project_id) values ('ArrayExpress,
    'https://www.ebi.ac.uk/arrayexpress/','Repository','ArrayExpress Archive of Functional Genomics Data etc.',4)`

Features in progress
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

    * `project_id` in MySQL database

        * Some tables in the MySQL database may include a `project_id` column that can be removed.

* User account

    * Connection to email (activation, password retrieval)
    * Sign in with Google or Facebook
    * Personalization features (avatar, about)

* Finding a resource in the database to pull for Chrome extension - issues here refer mainly to repositories

    * Since some resources may belong to multiple projects, the Chrome extension should recognize this.

    * Currently, the Chrome extension pulls resource averages and evaluations based on exact URL.
    It will not recognize the same resource if one project's webpage records the URL slightly differently
    from another project's webpage.
    * Examples:

        * '/' vs. no '/' at URL end
        * 'www' vs. no 'www' at URL beginning
        * 'http' vs. 'https'

    * Possible solutions:

        * Search by name in database
            * Similar issue by name e.g. 'UniProt:Swiss-Prot' from DataMed repositories and 'UniProt KnowledgeBase'
            in Model Organisms Database, as different webpages may have different names for the same resource
        * Use RegEx on URL search accounting for listed examples
        * For repository only, if certain parts of the URL are identical, ex. host or host and path,
        the resources should be considered identical

    * Current solution:

        * Using search both by name and URL in `/api/chrome_extension/getAvg` depending on source webpage.
        In Chrome extension JavaScript files, the call to the API passes in a `select` argument that can be `name`
        or `URL`. This specifies whether to search by name or URL in database for the average scores to display
        in insignia. However in `/redirectedFromExt`, to check if this resource from insignia click is already in the
        database, it searches by name... This is inconsistent and a better solution should be implemented.

    * Another issue: Some repositories listed on DataMed (and possibly future sites added to FAIRShake)
    are identified as distinct repositories even though they are hosted from the same site and can be considered
    one repository.

        * Repositories in question are: 'NeuroVault Atlases',' NeuroVault Cols', 'NeuroVault NIDM' all from NeuroVault

* Login issue from Chrome extension

    * Users must log in to submit evaluations. If a visitor is taken to the FAIRShake evaluation form through the
    Chrome extension, they may not be logged in.
    * Issue: The visitor should be able to log in and then be taken back to the original evaluation form.
    * Current solution: If visitor is logged in when clicking on insignia, they are taken to the evaluation form.
    If they are not logged in, they are taken to login page with evaluation form and resource information saved in
    `next` query. If they log in on this page, they will be taken back to the original evaluation form. If they move
    away from the login page, the form information is lost. If they log in later, they must click on the insignia
    in the Chrome extension again to return to the evaluation form.

* Error handling

    * There may be places where errors are not handled consistently.
    There is an error template (`errors.html`) set up. Example in `app.py`:
    `return render_template('error.html',errormsg='Invalid URL.')`

* Static files

    * Issue: Files saved in `static` folder (e.g. JavaScript, icons, pictures) are not recognized
    * Current solution: Pushed `static` files to amp.pharm.mssm.edu and hardcoded these addresses where needed
    in FAIRShake files

* Ensure consistency in results returned by APIs for questions and averages

* In Chrome extension for LINCS Dataset landing pages, if you come to the dataset landing page by entering in the URL,
the insignia appears normally. However, if you come to the dataset landing page by clicking on a
dataset link in `http://lincsportal.ccs.miami.edu/datasets/`, the insignia does not appear.
If you refresh the landing page, it will then appear. This is an issue specific to the LINCS Dataset landing pages.

    * Possible solutions: Automatically refresh these pages once

* Some LINCS Dataset landing pages do not show insignia at all, e.g.
`http://lincsportal.ccs.miami.edu/datasets/#/view/LDS-1195`

* Automate/standardize in some capacity the addition of webpages to Chrome extension

Future features to implement
------------

* Move website and database to Amazon server

* Sortable tables for resource lists in `/project/x/resources` and `/project/x/myevaluations`
    * May require different pagination using JavaScript on same page rather than URL change to different pages

* Improve pagination buttons on resource lists - possibly using `twbsPagination`

* Progress bar showing number of resources this user has evaluated out of this project

* Dropdown for comment in evaluation form allowing selection of common issues or 'other'

* 'Explore'/'Analytics'/'Ranking' feature for each project: Comparison of FAIRness scores of objects within this project
    * e.g. Ranked list with filters to select F/A/I/R scores

* Guide to show examples of 'yes' and 'no' for each question in evaluation form
    * e.g. Pullout sidebar

* Point/awards system

* Improvement to insignia color scale: All colors should have same shades of brightness
    * Issue: The only thing that should vary between the insignia colors is the red/blue shade in order to improve
    clarity. Currently, colors in between are often darker than the two ends of the scale. This should be corrected.
    * Possible solutions:
        * Could try other D3 color scales - currently using `d3.interpolateRgb`
        * Use gamma adjust

* Open comments on evaluation form no matter what option selected, not restricted to 'yes, but:'

* Insignia is currently dynamically created with JavaScript by the Chrome extension on a resource page, through
information received from APIs.
    * Issue: A more secure implementation should be considered.
    * Possible solutions:
        * Creating a static image of the insignia and sending a link to that image with the API.

* Legend explaining scoring/coloring of insignia