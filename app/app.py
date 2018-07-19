from flask import Flask, request, redirect, render_template, flash, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin, login_url
from flask_cors import CORS
from flaskext.mysql import MySQL
import math
from urlparse import urlparse
import validators
from flask.json import jsonify
import json

mysql = MySQL()

app = Flask(__name__)
CORS(app)

app.config.from_pyfile('config.py')
mysql.init_app(app)
ENTRY_POINT = app.config['ENTRY_POINT']

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = ENTRY_POINT + "/login"
app.secret_key = app.config['SECRET_KEY']

# Required for Flask login: Given user ID, returns user object
@login_manager.user_loader
def load_user(user_id):
    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select username,first_name,last_name,password from user where user_id=%s"
    cursor.execute(query1,(user_id))
    count = cursor.rowcount
    data = cursor.fetchall()

    if count == 0:
        return None
    elif count>1:
        return None
    else:
        username = data[0][0]
        first_name = data[0][1]
        last_name = data[0][2]
        password = data[0][3]

    # Return user object with these fields #
    return User(username, first_name, last_name, user_id, password)


# Home page #
@app.route(ENTRY_POINT + '/', methods=['GET'])
# @app.route(ENTRY_POINT, methods=['GET'])
def doe():
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Pass in list of projects to choose featured projects from #
    cursor.execute("select project_id,project_name,project_description,project_img from project order by project_id")
    data=cursor.fetchall()
    if not data:
        return render_template("error.html",errormsg="No projects")
    else:
        projectlist = []
        for row in data:
            projectlist.append(row)

        return render_template('doehome.html',projectlist=projectlist)


# Login page #
@app.route(ENTRY_POINT + "/login", methods=['GET', 'POST'])
def login():
    # User has tried to log in
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # If redirected from page with login_required view, that page is saved in "next" parameter by Flask Login
        prevPage = request.args.get('next')

        conx = mysql.get_db()
        cursor = conx.cursor()
        query1 = "select user_id from user where username=%s and password=%s"
        cursor.execute(query1,(username,password))
        data = cursor.fetchall()
        # User with this username and password not found in database #
        if not data:
            flash("Username or password is wrong.","danger")
            return redirect(ENTRY_POINT + '/login')
        # Correct username and password, log user in #
        else:
            user_id = data[0][0]
            user = load_user(user_id)
            login_user(user)

            # If there is a page saved in "next", go back to it. If not, go to homepage #
            return redirect((prevPage) or (ENTRY_POINT + '/'))
    else:
        return render_template('login.html')


# This user's evaluated projects page #
@app.route(ENTRY_POINT + "/evaluatedprojects", methods=["GET"])
@login_required
def evaluatedprojects():
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Get projects this user has begun evaluating #
    query1 = "select project_id,project_name,project_description,project_img from project " \
             "where project_id in (select project_id from resource_in_project " \
             "where resource_id in(select distinct(resource_id) from evaluation where user_id=%s)) order by project_id"
    cursor.execute(query1,(current_user.user_id))
    evprojd = cursor.fetchall()
    evproj = []
    for row in evprojd:
        evproj.append(row)
    return render_template('evaluatedproj.html',evproj=evproj)


# Logout #
@app.route(ENTRY_POINT + "/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.","success")
    return redirect(ENTRY_POINT + '/login')


# Signup page #
@app.route(ENTRY_POINT + "/register", methods=['GET', 'POST'])
def register():

    # Go to signup page #
    if request.method == 'GET':
        return render_template('register.html')

    # Signup information submitted #
    else:
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        projrole = request.form['projrole']
        conx_register = mysql.get_db()
        cursor = conx_register.cursor()

        # Check if this username (email) already exists in database #
        query1 = "select username from user where username=%s"
        cursor.execute(query1, (username))
        data = cursor.fetchall()

        # Username is new #
        # Username already exists in database #
        if data:
            flash("Account with this username already exists.","danger")
            return redirect(ENTRY_POINT + '/register')
        else:
            # Passwords don't match #
            if not (password1 == password2):
                flash("Passwords do not match.", "danger")
                return redirect(ENTRY_POINT + '/register')

            # Passwords match #
            else:
                if projrole == 'role_evaluator':
                    conx_add = mysql.get_db()
                    cursor = conx_add.cursor()
                    query1 = "insert into user(username,password,first_name,last_name,role_evaluator) values(%s,%s,%s,%s,'role_evaluator')"
                    cursor.execute(query1,(username,password1,first_name,last_name))
                    conx_add.commit()
                    flash("Account successfully created.", "success")
                    return redirect(ENTRY_POINT + '/login')
                elif projrole == 'role_starter':
                    conx_add = mysql.get_db()
                    cursor = conx_add.cursor()
                    query2 = "insert into user(username,password,first_name,last_name,role_starter) values(%s,%s,%s,%s,'role_starter')"
                    cursor.execute(query2,(username,password1,first_name,last_name))
                    conx_add.commit()
                    flash("Account successfully created.", "success")
                    return redirect(ENTRY_POINT + '/login')
                else:
                    return render_template('error.html',errormsg='Select valid role.')


# Project resources list page #
@app.route(ENTRY_POINT + '/project/<int:proj>/resources/', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route(ENTRY_POINT + '/project/<int:proj>/resources', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route(ENTRY_POINT + '/project/<int:proj>/resources/page/<int:page>', methods=['GET'])
def resourcelist(proj,page):
    if page<1:
        return render_template("error.html",errormsg="Not valid page number.")

    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select project_id,project_name,project_description,project_img from project where project_id=%s"
    cursor.execute(query1,(proj))
    data = cursor.fetchall()
    if not data:
        return render_template("error.html", errormsg="Not valid project.")
    else:
        projinfo=data[0]

    resources = []  # For resources' information #
    per_page = 10  # Number of resources per page #
    pagecount = per_page * page

    # Add this project's resources to list #
    # query3 = "select resource_id,resource_name,url,resource_type,description,project_id from resource " \
    #          "where project_id=%s order by resource_id"
    query3 = "select resource_id,resource_name,url,resource_type,description from resource " \
            "where resource_id in(select resource_id from resource_in_project where project_id=%s) order by resource_id"
    cursor.execute(query3,(proj))  # get resource info to display
    data = cursor.fetchall()
    for row in data:
        resources.append(row)
    total = len(resources)

    lastpage=1
    if total<per_page:
        lastpage=1
    elif total%per_page==0:
        lastpage=total/per_page
    else:
        lastpage=math.trunc(total/per_page)+1

    if page>lastpage:
        return render_template("error.html",errormsg="Not valid page number.")

    # For pagination: showlast is position of last resource #
    if pagecount > total:
        showlast = total
    else:
        showlast = pagecount

    avginfo = []  # Average scores for insignia #
    qdat = []  # Questions for insignia #
    userres = []  # For resources this user has evaluated - for check marks #
    listeval = []  # Number of evaluations resources have #

    # Go through all resources #
    for i in range(total):
        templist = [] # Contains resource id and averages
        xlist = [] # Contains resource id and questions

        templist.append(str(resources[i][0])) # Add resource id
        xlist.append(str(resources[i][0])) #Add resource id

        # Get number of evaluations for this resource #
        query4 = "select count(distinct(user_id)) from evaluation where resource_id=%s"
        cursor.execute(query4, (resources[i][0]))
        eval1 = cursor.fetchall()
        listeval.append(eval1[0][0]) # Add number of evaluations for resource

        query9 = "select q_id,content from question where res_type=%s and version=(select max(version) from question where res_type=%s) order by num"
        cursor.execute(query9,(resources[i][3],resources[i][3]))
        sqnum = cursor.rowcount
        data = cursor.fetchall()
        resources[i] = resources[i] + (sqnum,) # Add number of questions to tuple of resource information
        for row in data: # For all questions of this resource
            q_id=row[0]

            query6 = "select avg from average where resource_id=%s and q_id=%s"
            cursor.execute(query6,(resources[i][0],q_id))
            adata = cursor.fetchall()

            # No average for this resource for this question #
            if not adata:
                templist.append('None')

            # Add averages to list #
            else:
                templist.append(adata[0][0])

            # Add questions to list #
            query7 = "select content from question where q_id=%s"
            cursor.execute(query7,(q_id))
            xlist.append(cursor.fetchall()[0][0])

        avginfo.append(templist)  # Append list of averages for this resource
        qdat.append(xlist) # Append list of questions for this resource (a project may have multiple resource types)

    if current_user.is_authenticated:  # Add check marks for evaluated resources for logged in users
        query8 = "select resource_id,resource_name,url,resource_type,description from resource where " \
                 "resource_id in (select distinct(resource_id) from evaluation where user_id=%s)"
        cursor.execute(query8,(current_user.user_id))
        data = cursor.fetchall()
        for row in data:
            userres.append(row[0])  # list containing resource ids of resources this user evaluated


    return render_template('projhome.html',
                           resources=resources, listeval=listeval, total=total, projinfo=projinfo, proj=proj,
                           userres=userres, avginfo=avginfo, qdat=qdat,
                           pagecount=pagecount, page=page, per_page=per_page, showlast=showlast, lastpage=lastpage)


# Project my evaluations page #
@app.route(ENTRY_POINT + "/project/<int:proj>/myevaluations", defaults={'page': 1}, methods=['GET'])
@app.route(ENTRY_POINT + "/project/<int:proj>/myevaluations/", defaults={'page': 1}, methods=['GET'])
@app.route(ENTRY_POINT + "/project/<int:proj>/myevaluations/page/<int:page>", methods=['GET'])
@login_required
def myevals(proj, page):
    if page<1:
        return render_template("error.html",errormsg="Not valid page number.")

    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select project_id,project_name,project_description,project_img from project where project_id=%s"
    cursor.execute(query1,(proj))
    data = cursor.fetchall()
    if not data:
        return render_template("error.html", errormsg="Not valid project.")
    else:
        projinfo=data[0]

    per_page = 10
    pagecount = per_page * page

    query2 = "select count(resource_id) from resource_in_project where project_id=%s and resource_id in " \
             "(select distinct(resource_id) from evaluation where user_id=%s)"
    cursor.execute(query2,(proj,current_user.user_id))
    totalres = cursor.fetchall()[0][0]

    lastpage = 1
    if totalres < per_page:
        lastpage = 1
    elif totalres % per_page == 0:
        lastpage = totalres / per_page
    else:
        lastpage = math.trunc(totalres / per_page) + 1

    if page>lastpage:
        return render_template("error.html",errormsg="Not valid page number.")

    showlast = 0
    if pagecount > totalres:
        showlast = totalres
    else:
        showlast = pagecount

    resources = []
    listeval = []
    avginfo = []  # average insignia
    myans = []  # my answers insignia
    qdat = []

    query3 = "select resource_id,resource_name,url,resource_type,description from resource where " \
             "resource_id in (select t1.resource_id from evaluation t1 inner join resource_in_project t2 " \
             "on t1.resource_id=t2.resource_id where user_id=%s and t2.project_id=%s) order by resource_id"
             # "resource_id in (select resource_id from evaluation where user_id=%s and project_id=%s) order by resource_id" \

    cursor.execute(query3,(current_user.user_id,proj))
    data = cursor.fetchall()
    for row in data:
        resources.append(row)

    for i in range(totalres):  # Go through all resources evaluated by this user
        nlist = []
        templist = []
        xlist = []

        templist.append(str(resources[i][0]))
        xlist.append(str(resources[i][0]))

        query4 = "select count(distinct(user_id)) from evaluation where resource_id=%s"
        cursor.execute(query4,(resources[i][0]))
        listeval.append(cursor.fetchall()[0][0])

        query9 = "select q_id,content from question where res_type=%s and version=(select max(version) from question where res_type=%s) order by num"
        cursor.execute(query9, (resources[i][3], resources[i][3]))
        sqnum = cursor.rowcount
        data = cursor.fetchall()
        resources[i] = resources[i] + (sqnum,)
        for row in data:
            q_id = row[0]

            query6 = "select avg from average where resource_id=%s and q_id=%s"
            cursor.execute(query6,(resources[i][0],q_id))
            adata = cursor.fetchall()
            if not adata:  # Did not find an average for this resource for this question
                templist.append('None')
            else:
                templist.append(adata[0])  # Add this resource's average

            query7 = "select content from question where q_id=%s"
            cursor.execute(query7,(q_id))
            xlist.append(cursor.fetchall()[0][0])

        avginfo.append(templist) # List of resource averages
        qdat.append(xlist) # List of resource questions

        nlist.append(resources[i][0])
        query8 = "select answer from evaluation where resource_id=%s and user_id=%s order by q_id"
        cursor.execute(query8,(resources[i][0],current_user.user_id))  # my insignia answers
        nd = cursor.fetchall()
        for row in nd:
            if row[0] == 'yes':
                nlist.append(1)
            elif row[0] == 'no':
                nlist.append(-1)
            elif row[0] == 'yesbut' or row[0] == 'nobut':
                nlist.append(0)
        myans.append(nlist)

    return render_template('myevaluations.html', resources=resources, totalres=totalres, listeval=listeval, avginfo=avginfo,
                           ans=myans, qdat=qdat, proj=proj, projinfo=projinfo,
                           per_page=per_page, pagecount=pagecount, showlast=showlast, page=page, lastpage=lastpage)


# Evaluation form - Modify, old answers automatically filled in #
@app.route(ENTRY_POINT + "/modifyevaluation", methods=['GET'])
@login_required
def modifyevaluation():

    # First check that this user has submitted an evaluation for this resource.
    # If not, return an error message.
    resource_id = request.args.get('resourceid')
    if not resource_id:
        return render_template('error.html',errormsg="Please select a resource to evaluate.")

    conx = mysql.get_db()
    cursor = conx.cursor()

    query00 = "select max(resource_id) from resource"
    cursor.execute(query00)
    data=cursor.fetchall()[0][0]
    if data<int(resource_id) or int(resource_id)<0:
        return render_template('error.html',errormsg='Please select a valid resource to evaluate.')

    query6 = "select max(num) from question where res_type=(select resource_type from resource where resource_id=%s)"
    cursor.execute(query6,(resource_id))
    qnum = cursor.fetchall()[0][0]
    query0 = "select count(*) from evaluation where resource_id=%s and user_id=%s"
    cursor.execute(query0, (resource_id, current_user.user_id))
    count = cursor.fetchall()[0][0]
    if count == 0:
        return render_template('error.html', errormsg= "You have not yet submitted an evaluation for this resource.")
    elif count > qnum: # There is more than one evaluation recorded for this user and resource
        return render_template('error.html')
    else:
        setInfo = []
        setq = []
        query1 = "select answer,url_comment,comment from evaluation where resource_id=%s and user_id=%s order by q_id"
        cursor.execute(query1,(resource_id,current_user.user_id))
        data = cursor.fetchall()
        for row in data:
            setInfo.append(row)

        query3 = "select resource_name,url,resource_type,description from resource where resource_id=%s"
        cursor.execute(query3,(resource_id))
        row1 = cursor.fetchall()[0]
        resource_name = row1[0]
        url = row1[1]
        resource_type = row1[2]
        description = row1[3]

        query5 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query5,(resource_type,resource_type))
        sqnum = cursor.fetchall()[0][0]

        for i in range(1, sqnum+1):
            query4 = "select num,version,content from question where res_type=%s and num=%s and version=(select max(version) from question where res_type=%s)"
            cursor.execute(query4,(resource_type,i,resource_type))
            qd = cursor.fetchall()
            for row in qd:
                setq.append(row)

        exampleArr = []
        if resource_type=="Tool":
            exampleArr = [[["http://amp.pharm.mssm.edu/Harmonizome/about"], "Name: Harmonizome. Description from website: \
                            Search for genes or proteins and their functional terms extracted and organized from over a hundred publicly available resources. \
                            To facilitate access to and learning from biomedical Big Data, we created the Harmonizome: \
                            a collection of information about genes and proteins from 114 datasets provided by 66 online resources."],
                          [["http://amp.pharm.mssm.edu/Harmonizome"], "Available online."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/about",
                            "http://amp.pharm.mssm.edu/Harmonizome/resource/Gene+Ontology",
                            "http://amp.pharm.mssm.edu/Harmonizome/resource/Mammalian+Phenotype+Ontology",
                            "http://amp.pharm.mssm.edu/Harmonizome/resource/Human+Phenotype+Ontology"], "Gene and protein identifiers were mapped to NCBI \
                              Entrez Gene Symbols and attributes were mapped to appropriate ontologies. \
                              Harmonizome uses ontologies like Gene Ontology, Mammalian Phenotype Ontology, Human Phenotype Ontology."],
                          [["https://www.youtube.com/playlist?list=PL0Bwuj8819U8KXTPDSRe59ZPOYizZIpCS"],
                           "Video tutorials available on Youtube by Avi Ma'ayan."],
                          [["https://github.com/MaayanLab/harmonizome",
                            "http://amp.pharm.mssm.edu/Harmonizome/documentation"],
                           "Source code on GitHub (User: MaayanLab. Repository: harmonizome.) README.md available through GitHub.\
                          APIs documented on Harmonizome website."],
                          [["https://github.com/MaayanLab/harmonizome/releases"],
                           "There are no previous versions of the tool on Github."],
                          [["http://icahn.mssm.edu/research/labs/maayan-laboratory"],
                           "Link to Ma'ayan laboratory at Mount Sinai."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/documentation"],
                           "This document describes the REST APIs provided by the Harmonizome."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/terms"], "Free for academic, non-profit use, but for commercial uses please \
                            contact Mount Sinai Innovation Partners for a license."]]
        elif resource_type == "Dataset":
            exampleArr = [[[""], "LINCS ID: LDG-1348: LDS-1409"],
                          [[""], "Cell line (name, LINCS ID, organ) and small molecules used (name, LINCS ID, center sample ID, \
                                provider, provider catalog ID) are described."],
                          [[""], ""],
                          [["http://lincsportal.ccs.miami.edu/datasets"],
                                "Hosted in LINCS Data Portal datasets."],
                          [[""],
                                "Download available through Downloads tab in .tar.gz format."],
                          [[""], "Version information provided in Downloads tab: 1.0."],
                          [[""], "Dataset creator information provided in Descriptions tab. Center: HMS LINCS (Harvard Medical School).\
                                Principal investigator: Peter. K. Sorger. Data source: http://lincs.hms.harvard.edu/db/datasets/20310/"],
                          [[""],
                           "Citation information provided in Description and Downloads tab, available in text, .bib, .ris, .enw format. \
                                Peter K. Sorger: LINCS MCF 10A Common Project: \
                                Rolling-time-point sensitivity measures of the MCF 10A breast cell line to 8 small molecule perturbagens. \
                                Dataset 2 of 15: End-point cell counts and normalized growth rate inhibition values for all technical replicates of biological replicate 2.,\
                                 2017, LINCS (dataset), http://identifiers.org/lincs.data/LDS-1409, 1.0; retrieved: Feb 11, 2018."],
                          [["http://lincsportal.ccs.miami.edu/datasets/#/terms"],
                                "The use of these data is conditional on the terms of use from the respective data producing centers and the LINCS Consortium. \
                                This site may be used under the Creative Commons Attribution License Version 4."]]
        elif resource_type == "Repository":
            exampleArr = [[[""], "Browse tab and link on homepage takes user to list of datasets with links to dataset landing pages. \
                                Individual dataset landing pages list metadata."],
                          [[""], ""],
                          [["https://www.ebi.ac.uk/arrayexpress/",
                            "https://www.ebi.ac.uk/arrayexpress/help/contact_us.html"],
                           "Has option to submit feedback at homepage. Has page for other contact methods and information, like email and Twitter."],
                          [[""], ""],
                          [[""], ""],
                          [[""], "Metadata criteria consistent with repository intent: Includes organism, sample information, \
                                array information, protocol information, experiment type, and information reported about the experiment."],
                          [[""], "Individual dataset landing pages show date dataset submitted/updated/released, \
                                dataset name, contact information for dataset generator. Citation may be provided."],
                          [[""],
                           "Sections for information available in individual dataset landing pages: sample information, \
                                protocol information, experiment description, experiment type."],
                          [[""], ""]]

        return render_template('modifyevaluation.html',
                               resource_name=resource_name, resource_id=resource_id, resource_type=resource_type, url=url,
                               description=description, setInfo=setInfo, setq=setq, sqnum=sqnum, exampleArr=exampleArr)


# Evaluation form - New evaluation #
@app.route(ENTRY_POINT + "/newevaluation", methods=['GET'])
@login_required
def newevaluation():

    # First check that this user has not yet submitted an evaluation for this.
    # If not, return an error message.

    setq = []

    resource_id = request.args.get('resourceid')
    if not resource_id:
        return render_template('error.html',errormsg='Please select a resource to evaluate.')
    conx = mysql.get_db()
    cursor = conx.cursor()

    query00 = "select max(resource_id) from resource"
    cursor.execute(query00)
    if cursor.fetchall()[0][0]<int(resource_id) or int(resource_id)<0:
        return render_template('error.html',errormsg='Please select a valid resource to evaluate.')

    query0 = "select * from evaluation where resource_id=%s and user_id=%s"
    cursor.execute(query0,(resource_id, current_user.user_id))
    if cursor.rowcount!=0:
        return render_template('error.html',errormsg="You have already submitted an evaluation for this resource.")
    else:
        query1 = "select resource_name,url,resource_type,description from resource where resource_id=%s"
        cursor.execute(query1,(resource_id))
        row1 = cursor.fetchall()[0]
        resource_name = row1[0]
        resource_type = row1[2]
        url = row1[1]
        description = row1[3]

        query5 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query5, (resource_type, resource_type))
        sqnum = cursor.fetchall()[0][0]

        for i in range(1, sqnum + 1):
            query2 = "select num,version,content from question where res_type=%s and num=%s and version=(select max(version) from question where res_type=%s) order by num"
            cursor.execute(query2,(resource_type,i,resource_type))
            qd = cursor.fetchall()
            for row in qd:
                setq.append(row)

        exampleArr=[]
        if resource_type=="Tool":
            exampleArr = [[["http://amp.pharm.mssm.edu/Harmonizome/about"], "Name: Harmonizome. Description from website: \
                            Search for genes or proteins and their functional terms extracted and organized from over a hundred publicly available resources. \
                            To facilitate access to and learning from biomedical Big Data, we created the Harmonizome: \
                            a collection of information about genes and proteins from 114 datasets provided by 66 online resources."],
                          [["http://amp.pharm.mssm.edu/Harmonizome"], "Available online."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/about",
                            "http://amp.pharm.mssm.edu/Harmonizome/resource/Gene+Ontology",
                            "http://amp.pharm.mssm.edu/Harmonizome/resource/Mammalian+Phenotype+Ontology",
                            "http://amp.pharm.mssm.edu/Harmonizome/resource/Human+Phenotype+Ontology"], "Gene and protein identifiers were mapped to NCBI \
                              Entrez Gene Symbols and attributes were mapped to appropriate ontologies. \
                              Harmonizome uses ontologies like Gene Ontology, Mammalian Phenotype Ontology, Human Phenotype Ontology."],
                          [["https://www.youtube.com/playlist?list=PL0Bwuj8819U8KXTPDSRe59ZPOYizZIpCS"],
                           "Video tutorials available on Youtube by Avi Ma'ayan."],
                          [["https://github.com/MaayanLab/harmonizome",
                            "http://amp.pharm.mssm.edu/Harmonizome/documentation"],
                           "Source code on GitHub (User: MaayanLab. Repository: harmonizome.) README.md available through GitHub.\
                          APIs documented on Harmonizome website."],
                          [["https://github.com/MaayanLab/harmonizome/releases"],
                           "There are no previous versions of the tool on Github."],
                          [["http://icahn.mssm.edu/research/labs/maayan-laboratory"],
                           "Link to Ma'ayan laboratory at Mount Sinai."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/documentation"],
                           "This document describes the REST APIs provided by the Harmonizome."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/terms"], "Free for academic, non-profit use, but for commercial uses please \
                            contact Mount Sinai Innovation Partners for a license."]]
        elif resource_type == "Dataset":
            exampleArr = [[[""], "LINCS ID: LDG-1348: LDS-1409"],
                          [[""], "Cell line (name, LINCS ID, organ) and small molecules used (name, LINCS ID, center sample ID, \
                                provider, provider catalog ID) are described."],
                          [[""], ""],
                          [["http://lincsportal.ccs.miami.edu/datasets"],
                                "Hosted in LINCS Data Portal datasets."],
                          [[""],
                                "Download available through Downloads tab in .tar.gz format."],
                          [[""], "Version information provided in Downloads tab: 1.0."],
                          [[""], "Dataset creator information provided in Descriptions tab. Center: HMS LINCS (Harvard Medical School).\
                                Principal investigator: Peter. K. Sorger. Data source: http://lincs.hms.harvard.edu/db/datasets/20310/"],
                          [[""],
                           "Citation information provided in Description and Downloads tab, available in text, .bib, .ris, .enw format. \
                                Peter K. Sorger: LINCS MCF 10A Common Project: \
                                Rolling-time-point sensitivity measures of the MCF 10A breast cell line to 8 small molecule perturbagens. \
                                Dataset 2 of 15: End-point cell counts and normalized growth rate inhibition values for all technical replicates of biological replicate 2.,\
                                 2017, LINCS (dataset), http://identifiers.org/lincs.data/LDS-1409, 1.0; retrieved: Feb 11, 2018."],
                          [["http://lincsportal.ccs.miami.edu/datasets/#/terms"],
                                "The use of these data is conditional on the terms of use from the respective data producing centers and the LINCS Consortium. \
                                This site may be used under the Creative Commons Attribution License Version 4."]]
        elif resource_type == "Repository":
            exampleArr = [[[""], "Browse tab and link on homepage takes user to list of datasets with links to dataset landing pages. \
                                Individual dataset landing pages list metadata."],
                          [[""], ""],
                          [["https://www.ebi.ac.uk/arrayexpress/",
                            "https://www.ebi.ac.uk/arrayexpress/help/contact_us.html"],
                           "Has option to submit feedback at homepage. Has page for other contact methods and information, like email and Twitter."],
                          [[""], ""],
                          [[""], ""],
                          [[""], "Metadata criteria consistent with repository intent: Includes organism, sample information, \
                                array information, protocol information, experiment type, and information reported about the experiment."],
                          [[""], "Individual dataset landing pages show date dataset submitted/updated/released, \
                                dataset name, contact information for dataset generator. Citation may be provided."],
                          [[""],
                           "Sections for information available in individual dataset landing pages: sample information, \
                                protocol information, experiment description, experiment type."],
                          [[""], ""]]

        return render_template('newevaluation.html',
                                   resource_name=resource_name, resource_id=resource_id, resource_type=resource_type, url=url,
                                   description=description, setq=setq,sqnum=sqnum, exampleArr=exampleArr)


# Enter modify submission into database #
@app.route(ENTRY_POINT + '/modifysubmitted', methods=['POST'])
@login_required
def modifysubmitted():
    resource_id = request.form['resource_id']

    conx = mysql.get_db()
    cursor = conx.cursor()

    if request.form['formType'] == 'cancelForm':
        if current_user.is_authenticated:
            return redirect(ENTRY_POINT + '/evaluatedprojects')
        else:
            return redirect(ENTRY_POINT)
        # query0 = "select project_id from resource where resource_id=%s"
        # cursor.execute(query0,(resource_id))
        # if cursor.rowcount==0:
        #     return render_template('error.html')
        # project_id=cursor.fetchall()[0][0]
        # return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/myevaluations')

    elif request.form['formType'] == 'deleteEval':
        query1 = "select resource_type from resource where resource_id=%s"
        cursor.execute(query1, (resource_id))  # get resource type
        tt = cursor.fetchall()
        res_type = tt[0][0]

        query0 = "delete from evaluation where resource_id=%s and user_id=%s"
        cursor.execute(query0,(resource_id,current_user.user_id))
        conx.commit()

        query2 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query2,(res_type,res_type))
        qtotal = cursor.fetchall()[0][0]

        for i in range(qtotal):  # for each question, update average
            query3 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
            cursor.execute(query3,(i+1,res_type,res_type))  # get q_id of most recent q
            q_id = cursor.fetchall()[0][0]  # use most recent q_id for this question

            total = 0

            query6 = "select answer from evaluation where resource_id=%s and q_id=%s"
            cursor.execute(query6, (resource_id, q_id))  # start to update average in average table
            count = cursor.rowcount
            data = cursor.fetchall()
            if count == 0:
                query7 = "delete from average where resource_id=%s and q_id=%s"
                cursor.execute(query7, (resource_id,q_id))
                conx.commit()
            else:
                for row in data:
                    if row[0] == 'yes':
                        total = total + 1
                    elif row[0] == 'no':
                        total = total - 1
                average = float(total) / count
                query8 = "update average set avg=%s where resource_id=%s and q_id=%s"
                cursor.execute(query8, (average, resource_id, q_id))
                conx.commit()
        flash("Evaluation deleted.", "success")
        if current_user.is_authenticated:
            return redirect(ENTRY_POINT + '/evaluatedprojects')
        else:
            return redirect(ENTRY_POINT)

    elif request.form['formType'] == 'evalForm':
        query1 = "select resource_type from resource where resource_id=%s"
        cursor.execute(query1, (resource_id))  # get resource type
        tt = cursor.fetchall()
        res_type = tt[0][0]

        query2 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query2,(res_type,res_type))
        qtotal = cursor.fetchall()[0][0]

        for i in range(qtotal):  # for each question
            thisAnswer = request.form['q' + str((i + 1))]  # get answer for this question
            thisComment = request.form['q' + str((i + 1)) + 'comment']  # get comment for this question
            thisURLComment = request.form['q' + str(i + 1) + 'urlcomment']  # get urlcomment for this question

            query3 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
            cursor.execute(query3,(i+1,res_type,res_type))  # get q_id of most recent q
            q_id = cursor.fetchall()[0][0]  # use most recent q_id for this question

            # # update evaluation entry, first clearing any existing comments #
            # query4 = "update evaluation set url_comment=null,comment=null where resource_id=%s and q_id=%s and user_id=%s"
            # cursor.execute(query4, (resource_id,q_id,current_user.user_id))
            # conx.commit()
            query5 = "update evaluation set answer=%s,url_comment=%s,comment=%s where resource_id=%s and q_id=%s and user_id=%s"
            if not thisComment and not thisURLComment:
                cursor.execute(query5, (thisAnswer, None, None, resource_id, q_id, current_user.user_id))
                conx.commit()
            else:
                if thisComment:
                    if thisURLComment:
                        cursor.execute(query5,
                                       (thisAnswer, thisURLComment, thisComment, resource_id, q_id, current_user.user_id))
                        conx.commit()
                    else:
                        cursor.execute(query5, (thisAnswer, None, thisComment, resource_id, q_id, current_user.user_id))
                        conx.commit()
                else:
                    if thisURLComment:
                        cursor.execute(query5, (thisAnswer, thisURLComment, None, resource_id, q_id, current_user.user_id))
                        conx.commit()

            total = 0

            query6 = "select answer from evaluation where resource_id=%s and q_id=%s"
            cursor.execute(query6, (resource_id, q_id))  # start to update average in average table
            count = cursor.rowcount
            data = cursor.fetchall()
            for row in data:
                if row[0] == 'yes':
                    total = total + 1
                elif row[0] == 'no':
                    total = total - 1

            # update  average #
            average = float(total) / count
            query8 = "update average set avg=%s where resource_id=%s and q_id=%s"
            cursor.execute(query8, (average, resource_id, q_id))
            conx.commit()
        flash("Evaluation modified.", "success")
        if current_user.is_authenticated:
            return redirect(ENTRY_POINT + '/evaluatedprojects')
        else:
            return redirect(ENTRY_POINT)

    else:
        return render_template('error.html')


# Enter new evaluation submission into database #
@app.route(ENTRY_POINT + '/evaluationsubmitted', methods=['POST'])
@login_required
def evaluationsubmitted():

    resource_id = request.form['resource_id']

    conx = mysql.get_db()
    cursor = conx.cursor()

    if request.form['formType'] == 'cancelForm':
        if current_user.is_authenticated:
            return redirect(ENTRY_POINT + '/evaluatedprojects')
        else:
            return redirect(ENTRY_POINT)

    elif request.form['formType'] == 'evalForm':
        query1 = "select resource_type from resource where resource_id=%s"
        cursor.execute(query1,(resource_id))  # get resource type
        tt = cursor.fetchall()
        res_type = tt[0][0]

        query10 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query10,(res_type,res_type))
        qtotal = cursor.fetchall()[0][0]

        for i in range(qtotal):  # for each question
            thisAnswer = request.form['q' + str(i+1)]  # get answer for this question
            thisComment = request.form['q' + str(i+1) + 'comment']  # get comment for this question
            thisURLComment = request.form['q' + str(i+1) + 'urlcomment'] # get urlcomment for this question

            query2 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
            cursor.execute(query2,(i+1,res_type,res_type))  # get q_id
            q_id = cursor.fetchall()[0][0]

            # since this is a new evaluation, there should not be an evaluation existing but clear just in case
            query3 = "delete from evaluation where q_id=%s and resource_id=%s and user_id=%s"
            cursor.execute(query3,(q_id,resource_id,current_user.user_id))
            conx.commit()

            query4 = "insert into evaluation(user_id,q_id,answer,url_comment,comment,resource_id) values(%s,%s,%s,%s,%s,%s)"
            if thisComment:
                if thisURLComment:
                    # query5 = "insert into evaluation(user_id,q_id,answer,url_comment,comment,resource_id) values(%s,%s,%s,%s,%s,%s)"
                    cursor.execute(query4, (current_user.user_id, q_id, thisAnswer, thisURLComment, thisComment, resource_id))
                    conx.commit()
                else:
                    # query4 = "insert into evaluation(user_id,q_id,answer,comment,resource_id) values(%s,%s,%s,%s,%s)"
                    cursor.execute(query4, (current_user.user_id, q_id, thisAnswer, None, thisComment, resource_id))
                    conx.commit()
            else:
                if thisURLComment:
                    # query4 = "insert into evaluation(user_id,q_id,answer,url_comment,resource_id) values(%s,%s,%s,%s,%s)"
                    cursor.execute(query4, (current_user.user_id, q_id, thisAnswer, thisURLComment, None, resource_id))
                    conx.commit()
                else:
                    # query4 = "insert into evaluation(user_id,q_id,answer,resource_id) values(%s,%s,%s,%s)"
                    cursor.execute(query4, (current_user.user_id, q_id, thisAnswer, None, None, resource_id))
                    conx.commit()

            total = 0

            query6 = "select answer from evaluation where resource_id=%s and q_id=%s"
            cursor.execute(query6,(resource_id,q_id))  # start to update average in average table
            count = cursor.rowcount
            data = cursor.fetchall()
            for row in data:
                if row[0] == 'yes':
                    total = total + 1
                elif row[0] == 'no':
                    total = total - 1

            average = float(total) / count
            query8 = "delete from average where resource_id=%s and q_id=%s"
            cursor.execute(query8,(resource_id,q_id))
            conx.commit()  # clear this entry in average
            query9 = "insert into average(resource_id,q_id,avg) values(%s,%s,%s)"
            cursor.execute(query9,(resource_id,q_id,average))
            conx.commit()

        flash("Evaluation submitted.", "success")
        if current_user.is_authenticated:
            return redirect(ENTRY_POINT + '/evaluatedprojects')
        else:
            return redirect(ENTRY_POINT)
    else:
        return render_template('error.html')


@app.route(ENTRY_POINT + "/forgotpassword")
def forgotpass():
    return render_template('forgotpass.html')


@app.route(ENTRY_POINT + '/sentpassword', methods=['POST'])
def sentpass():
    username = request.form['username']

    conx = mysql.get_db()
    cursor = conx.cursor()
    query1 = "select password from user where username=%s"
    cursor.execute(query1,(username))
    data = cursor.fetchone()

    if not data:
        return "No account under this username"
    else:
        return "Email placeholder" # To be implemented later #


@app.route(ENTRY_POINT + "/settings",methods=["GET"])
@login_required
def settings():
    return render_template('settings.html')


@app.route(ENTRY_POINT + "/resetpassword", methods=["GET","POST"])
@login_required
def resetPassword():

    # Go to reset pass page #
    if request.method=='GET':
        return render_template('resetpass.html')

    # Reset pass submitted #
    else:
        username = current_user.username
        passwordold = request.form['passwordold']
        password1 = request.form['password1']
        password2 = request.form['password2']

        conx = mysql.get_db()
        cursor = conx.cursor()
        query1 = "select username from user where username=%s and password=%s"
        cursor.execute(query1,(username,passwordold))
        data = cursor.fetchone()

        if not data:
            flash("Wrong password.","danger")
            return redirect(ENTRY_POINT + '/resetpassword')
        else:  # old pass + this username match
            if not (password1 == password2):  # passwords don't match
                flash("Passwords do not match.", "danger")
                return redirect(ENTRY_POINT + '/resetpassword')
            else:  # passwords match
                query2 = "update user set password=%s where username=%s"
                cursor.execute(query2,(password1,username))
                conx.commit()
                flash("Password successfully changed.","success")
                return redirect(ENTRY_POINT + '/settings')


@app.route(ENTRY_POINT + '/projects', methods=['GET'])
def projects():
    projectlist = []

    conx = mysql.get_db()
    cursor = conx.cursor()
    cursor.execute("select project_id,project_name,project_description,project_img from project order by project_id")
    data = cursor.fetchall()
    for row in data:
        projectlist.append(row)
    return render_template('projects.html', projectlist=projectlist)


@app.route(ENTRY_POINT+'/startproject',methods=['GET','POST'])
@login_required
def startProject():

    # Go to start project page #
    if request.method=='GET':

        return render_template('startproject.html')

    # Start project submitted #
    else:
        # To finish later #

        conx = mysql.get_db()
        cursor = conx.cursor()

        projectname=request.form['projectname']
        projectdesc=request.form['projectdesc']
        projectimg=request.form['projectimg']

        query1 = "insert into project(project_name,project_description,project_img) values(%s,%s,%s)"
        cursor.execute(query1,(projectname,projectdesc,projectimg))
        conx.commit()

        savertotal=request.form['savertotal']

        for i in range(int(savertotal)):
            resourcename=request.form['savername' + str(i + 1)]
            resourcetype = request.form['savertype' + str(i + 1)]
            resourceurl = request.form['saverurl' + str(i + 1)]
            resourcedesc = request.form['saverdesc' + str(i + 1)]

            query2 = "insert into resource(resource_name,resource_type,url,description) values(%s,%s,%s,%s)"
            cursor.execute(query2,(resourcename,resourcetype,resourceurl,resourcedesc,projectname))
            conx.commit()

            query4 = "insert into resource_in_project(resource_id,project_id) " \
                     "values(select resource_id from resource where url=%s),(select project_id from project where project_name=%s))"
            cursor.execute(query4,(resourceurl,projectname))

        saveqtotal=request.form['saveqtotal']

        for r in range(int(saveqtotal)):  # get the first x questions + ignore the rest
            qucontent=request.form['saveq'+str(r+1)]
            query3 = "insert into question(num,version,res_type,content) values(%s,'1','example_type',%s)"
            cursor.execute(query3,(r+1,qucontent))
            conx.commit()

        flash("Project successfully created.", "success")
        return redirect(ENTRY_POINT + '/projects')


# find the resource that matches this url
# returns None if none or multiple matches found
# returns list [resource_id, resource_name, resource_type] if one match found
def findResource(url,cursor):
    if not validators.url(url):
        return None
    else:
        # check whole url match first with and without trailing / - exact match to end
        index = url.find('://')
        a = url[(index + 3):]
        if a[:4] == "www.":
            a = a[4:]
        input = '%' + a
        query = "select resource_id,resource_name,resource_type from resource where url like %s"
        cursor.execute(query, (input))
        if cursor.rowcount>1:
            return None
        elif cursor.rowcount == 0:
            if a[(len(a) - 1):] == "/":
                a = a[:len(a) - 1]
                input = '%' + a
                query = "select resource_id,resource_name,resource_type from resource where url like %s"
                cursor.execute(query, (input))
                if cursor.rowcount!=1:
                    return None
                else:
                    result = cursor.fetchall()
                    return result[0]
        else:
            result = cursor.fetchall()
            return result[0]


# API to get this resource's questions for insignia #
# returns ['None'] if invalid URL, 0 or more than 1 matches for URL, or no questions for this resource's type
# otherwise returns list of questions, resource name, resource ID, # of questions
@app.route(ENTRY_POINT + '/api/getQ')
def getQAPI():

    resArr = []
    conx = mysql.get_db()
    cursor = conx.cursor()
    url = request.args.get('url')
    result = findResource(url,cursor)
    if result is None:
        return jsonify(['None'])
    else:
        theID = result[0]
        theName = result[1]
        theType = result[2]

        # Get questions for this resource's type #
        query1 = "select content from question where version=(select max(version) from question where res_type=%s) and res_type=%s order by num"
        cursor.execute(query1, (theType,theType))
        sqnum = cursor.rowcount
        data=cursor.fetchall()

        # No questions for this resource type yet
        if sqnum == 0:
            return jsonify(['None'])
        else:
            for row in data:
                resArr.append(row[0]) # text type returned from database is unicode
            resArr.append(theName)
            # resArr.append(str(theID).encode("utf-8").decode("utf-8"))
            # resArr.append(str(sqnum).encode("utf-8").decode("utf-8"))
            resArr.append(theID)
            resArr.append(sqnum)
            return jsonify(resArr)


# API to get this resource's average scores for insignia #
# returns ['None'] if invalid URL, or 0 or more than 1 matches to URL, or no score yet
# otherwise returns list of scores
@app.route(ENTRY_POINT + '/api/getAvg')
def getAvgAPI():
    avgArr=[]
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Get this resource's average scores to make insignia, search by URL #
    url = request.args.get('url')
    result = findResource(url,cursor)
    if result is None:
        return jsonify(['None'])
    else:
        resource_id = result[0]
        query0 = "select avg from average t1 inner join question t2 on t1.q_id=t2.q_id where resource_id=%s order by num"
        cursor.execute(query0,(resource_id))
        result1=cursor.fetchall()

        # No averages yet for this resource - has not yet been evaluated #
        if cursor.rowcount==0:
            return jsonify(['None'])
        # Average scores exist - Return in comma separated string #
        else:
            for row in result1:
                avgArr.append(row[0])
            return jsonify(avgArr)

# API to enter evaluations into database and update average #
# parameters: url, q1a (answer to q1), q1u (urlcomment to 1q), q1c (comment to q1), q2a, q2u, q2c,..., qna, qnu, qnc
# answers may only be: 'yes', 'no', 'yesbut', 'nobut'
# comments are not necessary
# urlcomments must be valid URLs
# returns: '0' if unsuccessful, '1' if successful
# if evaluating a resource with n number of questions, must enter answers for each question (i.e. q1a,...,qna)
# if no comment or urlcomment submitted, null in database
# evaluations from this API entered in database with user_id=-1 for the purpose of vetting
@app.route(ENTRY_POINT + '/api/evaluate',methods=['POST'])
def evaluateAPI():
    conx = mysql.get_db()
    cursor = conx.cursor()

    url = request.form.get('url')
    if not url:
        return '0'
    arrayQA = request.form.get('arrayQA')
    if arrayQA:
        arrayQA1 = json.loads(arrayQA)
    else:
        return '0'

    result = findResource(url,cursor)
    if result is None:
        return '0'
    else:
        resource_id=result[0]
        res_type=result[2]

        query1 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query1,(res_type,res_type))
        qtotal = cursor.fetchall()[0][0]
        # before beginning to enter anything in database:
        # check that each answer has a question number field and answer field
        # check that each answer is yes, no, yesbut, or nobut
        # check that all urlcomments are valid URLs
        # check that each question is only answered once
        # check that the number of questions answered matches the number of questions for the resource
        for x in arrayQA1:
            if 'question' not in x or 'answer' not in x: # For each QuestionAnswer object, question and answer fields are required
                return '0'
            if x['answer'] not in ['yes','no','yesbut','nobut']: # Only valid answers accepted
                return '0'
            if 'urlcomment' in x and not validators.url(x['urlcomment']): # Only valid URLs accepted as URLcomment
                return '0'
        for y in range(1,qtotal+1): # check that each question is only answered once, and number of questions answered matches resource's number of questions
            qcount=0
            for x in arrayQA1:
                if x['question'] == y:
                    qcount=qcount+1
            if qcount!=1:
                return '0'

        # # begin to enter information into database
        # for i in range(3,qtotal+1):  # for each question
        #     # find object that represents this question, then get the fields
        #     for h in range(0,qtotal): # go through all QuestionAnswers
        #         if arrayQA1[h]['question']==i:
        #             return str(arrayQA1[h]['question'])

        for i in range(1, qtotal + 1):  # for each question. i from 1-9
            # find object that represents this question, then get the fields
            for h in range(0, qtotal):  # go through all QuestionAnswers to find this question. for each index 0-8
                if arrayQA1[h]['question'] == i:
                    thisQA = arrayQA1[h]
                    thisAnswer = thisQA['answer']
                    thisComment = ''
                    thisURLComment = ''
                    if 'textComment' in thisQA:
                        thisComment = thisQA['textComment']
                    if 'urlComment' in thisQA:
                        thisURLComment = thisQA['urlComment']

                    query2 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
                    cursor.execute(query2, (i, res_type, res_type))  # get q_id
                    q_id = cursor.fetchall()[0][0]

                    query3 = "insert into evaluation(user_id,q_id,answer,url_comment,comment,resource_id) values(%s,%s,%s,%s,%s,%s)"

                    if thisComment:
                        if thisURLComment:
                            cursor.execute(query3, (-1, q_id, thisAnswer, thisURLComment, thisComment, resource_id))
                            conx.commit()
                        else:
                            cursor.execute(query3, (-1, q_id, thisAnswer, None, thisComment, resource_id))
                            conx.commit()
                    else:
                        if thisURLComment:
                            cursor.execute(query3, (-1, q_id, thisAnswer, thisURLComment, None, resource_id))
                            conx.commit()
                        else:
                            cursor.execute(query3, (-1, q_id, thisAnswer, None, None, resource_id))
                            conx.commit()
                    # else:
                    #     query4 = "insert into evaluation(user_id,q_id,answer,resource_id) values(%s,%s,%s,%s)"
                    #     cursor.execute(query4, (-1, q_id, thisAnswer, resource_id))
                    #     conx.commit()

                    total = 0

                    query6 = "select answer from evaluation where resource_id=%s and q_id=%s"
                    cursor.execute(query6, (resource_id, q_id))  # start to update average in average table
                    count = cursor.rowcount
                    data = cursor.fetchall()

                    for row in data:
                        if row[0] == 'yes':
                            total = total + 1
                        elif row[0] == 'no':
                            total = total - 1

                    average = float(total) / count
                    # query8 = "update average set avg=%s where resource_id=%s and q_id=%s"
                    # cursor.execute(query8,(average,resource_id,q_id))
                    # conx.commit()

                    query8 = "delete from average where resource_id=%s and q_id=%s"
                    cursor.execute(query8, (resource_id, q_id))
                    conx.commit()  # clear this entry in average
                    query9 = "insert into average(resource_id,q_id,avg) values(%s,%s,%s)"
                    cursor.execute(query9, (resource_id, q_id, average))
                    conx.commit()
    return '1'

# API to get questions based on resource type #
# returns ['None'] if invalid type, or no questions for this type
# otherwise returns list of questions
@app.route(ENTRY_POINT + '/api/getQByType')
def getQByTypeAPI():

    resArr = []
    conx = mysql.get_db()
    cursor = conx.cursor()
    theType = request.args.get('type')
    if theType=='Dataset' or theType=='Tool' or theType=='Repository':

        # Get questions for this resource's type #
        query1 = "select content from question where version=(select max(version) from question where res_type=%s) and res_type=%s order by num"
        cursor.execute(query1, (theType,theType))
        data=cursor.fetchall()

        # No questions for this resource type yet
        if cursor.rowcount == 0:
            return jsonify(['None'])
        else:
            for row in data:
                resArr.append(row[0])  # text type returned from database is unicode
            return jsonify(resArr)
    else:
        return jsonify(['None'])

# Download Chrome extension page #
@app.route(ENTRY_POINT + '/chromeextension')
def chromeextension():
    return render_template('chromext.html')

# Download Bookmarklet page #
@app.route(ENTRY_POINT + '/bookmarklet')
def bookmarklet():
    return render_template('bookmarklet.html')

# Logged in user. Flask-login also provides class for anonymous users. #
class User(UserMixin):

    def __init__(self, username, first_name, last_name, user_id, password):

        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
        self.password = password

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)


if __name__ == "__main__":
    app.run(debug=True)
