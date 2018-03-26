from flask import Flask, request, redirect, render_template, flash, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin, login_url
from flask_cors import CORS
from flaskext.mysql import MySQL
import math
from urlparse import urlparse
import validators
from flask.json import jsonify

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
@app.route(ENTRY_POINT, methods=['GET'])
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
    # # Go to login page - accessed through FAIRShake Chrome extension
    # if request.method == 'GET':
    #     redirects = request.args.get('next')
    #     if redirects is None:
    #         return render_template('login.html')
    #     else:
    #         matchObj = re.match(r'[/]fairshake[/]redirectedFromExt.*', redirects)
    #         if matchObj is None:
    #             return render_template('login.html')
    #         else:
    #             theName = request.args.get('theName')
    #             theURL = request.args.get('theURL')
    #             theType = request.args.get('theType')
    #             theDescrip = request.args.get('theDescrip')
    #             if theName is None or theURL is None or theType is None or theDescrip is None:
    #                 return render_template('login.html')
    #             else:
    #                 return render_template('login.html',redirectFromExt="yes",theName=theName,theURL=theURL,theType=theType,theDescrip=theDescrip)
    # # Login information submitted through POST #
    # else:

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
        # redirects = request.args.get('next')
        # if redirects is None:
        #     return render_template('login.html')
        # else:
        #     matchObj = re.match(r'[/]fairshake[/]redirectedFromExt.*', redirects)
        #     if matchObj is None:
        #         return render_template('login.html')
        #     else:
        #         theName = request.args.get('theName')
        #         theURL = request.args.get('theURL')
        #         theType = request.args.get('theType')
        #         theDescrip = request.args.get('theDescrip')
        #         if theName is None or theURL is None or theType is None or theDescrip is None:
        #             return render_template('login.html')
        #         else:
        #             return render_template('login.html',redirectFromExt="yes",theName=theName,theURL=theURL,theType=theType,theDescrip=theDescrip)



# This user's evaluated projects page #
@app.route(ENTRY_POINT + "/evaluatedprojects", methods=["GET"])
@login_required
def evaluatedprojects():
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Get projects this user has begun evaluating #
    query1 = "select project_id,project_name,project_description,project_img from project " \
             "where project_id in (select distinct(project_id) from evaluation where user_id=%s order by project_id)"
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
    query3 = "select resource_id,resource_name,url,resource_type,description,project_id from resource " \
             "where project_id=%s order by resource_id"
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
        query8 = "select resource_id,resource_name,url,resource_type,description,project_id from resource where " \
                 "resource_id in (select resource_id from evaluation where user_id=%s)"
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

    query2 = "select count(distinct(resource_id)) from evaluation where user_id=%s and project_id=%s"
    cursor.execute(query2,(current_user.user_id,proj))
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

    query3 = "select resource_id,resource_name,url,resource_type,description,project_id from resource where " \
             "resource_id in (select resource_id from evaluation where user_id=%s and project_id=%s) order by resource_id"
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
            elif row[0] == 'yesbut':
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

    conx = mysql.get_db()
    cursor = conx.cursor()

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
        row1 = cursor.fetchone()
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
            exampleArr=[[["http://amp.pharm.mssm.edu/Harmonizome/about"], "Name: Harmonizome. Description from website: \
                        Search for genes or proteins and their functional terms extracted and organized from over a hundred publicly available resources. \
                        To facilitate access to and learning from biomedical Big Data, we created the Harmonizome: \
                        a collection of information about genes and proteins from 114 datasets provided by 66 online resources."],
                          [["http://amp.pharm.mssm.edu/Harmonizome"],"Available online."],
                          [["http://database.oxfordjournals.org/content/2016/baw100.short"], "Paper published in Oxford about tool: \
                                The harmonizome: a collection of processed datasets gathered to serve and mine knowledge about genes and proteins"],
                          [["https://www.youtube.com/playlist?list=PL0Bwuj8819U8KXTPDSRe59ZPOYizZIpCS"],
                           "Video tutorials available on Youtube by Avi Ma'ayan."],
                          [["https://github.com/MaayanLab/harmonizome","http://amp.pharm.mssm.edu/Harmonizome/documentation"],
                                "Source code on GitHub (User: MaayanLab. Repository: harmonizome.) README.md available through GitHub.\
                                 APIs documented on Harmonizome website."],
                          [[""],""],
                          [["http://icahn.mssm.edu/research/labs/maayan-laboratory"],
                           "Link to Ma'ayan laboratory at Mount Sinai."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/terms"], "Rouillard AD, Gundersen GW, Fernandez NF, Wang Z, \
                                        Monteiro CD, McDermott MG, Ma'ayan A. The harmonizome: a collection of processed datasets gathered to serve and mine \
                                        knowledge about genes and proteins. Database (Oxford). 2016 Jul 3;2016. pii: baw100."],
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

    conx = mysql.get_db()
    cursor = conx.cursor()

    query0 = "select * from evaluation where resource_id=%s and user_id=%s"
    cursor.execute(query0,(resource_id, current_user.user_id))
    if cursor.rowcount!=0:
        return render_template('error.html',errormsg="You have already submitted an evaluation for this resource.")
    else:
        query1 = "select resource_id,resource_name,url,resource_type,description,project_id from resource where " \
                 "resource_id=%s"
        cursor.execute(query1,(resource_id))
        row1 = cursor.fetchone()
        resource_name = row1[1]
        resource_type = row1[3]
        url = row1[2]
        description = row1[4]

        query5 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query5, (resource_type, resource_type))
        sqnum = cursor.fetchall()[0][0]

        for i in range(1, sqnum + 1):
            query2 = "select num,version,content from question where res_type=%s and num=%s and version=(select max(version) from question) order by num"
            cursor.execute(query2,(resource_type,i))
            qd = cursor.fetchall()
            for row in qd:
                setq.append(row)

        exampleArr=[]
        if resource_type=="Tool":
            exampleArr=[[["http://amp.pharm.mssm.edu/Harmonizome/about"], "Name: Harmonizome. Description from website: \
                        Search for genes or proteins and their functional terms extracted and organized from over a hundred publicly available resources. \
                        To facilitate access to and learning from biomedical Big Data, we created the Harmonizome: \
                        a collection of information about genes and proteins from 114 datasets provided by 66 online resources."],
                          [["http://amp.pharm.mssm.edu/Harmonizome"],"Available online."],
                          [["http://database.oxfordjournals.org/content/2016/baw100.short"], "Paper published in Oxford about tool: \
                                The harmonizome: a collection of processed datasets gathered to serve and mine knowledge about genes and proteins"],
                          [["https://www.youtube.com/playlist?list=PL0Bwuj8819U8KXTPDSRe59ZPOYizZIpCS"],
                           "Video tutorials available on Youtube by Avi Ma'ayan."],
                          [["https://github.com/MaayanLab/harmonizome","http://amp.pharm.mssm.edu/Harmonizome/documentation"],
                                "Source code on GitHub (User: MaayanLab. Repository: harmonizome.) README.md available through GitHub.\
                                 APIs documented on Harmonizome website."],
                          [[""],""],
                          [["http://icahn.mssm.edu/research/labs/maayan-laboratory"],
                           "Link to Ma'ayan laboratory at Mount Sinai."],
                          [["http://amp.pharm.mssm.edu/Harmonizome/terms"], "Rouillard AD, Gundersen GW, Fernandez NF, Wang Z, \
                                        Monteiro CD, McDermott MG, Ma'ayan A. The harmonizome: a collection of processed datasets gathered to serve and mine \
                                        knowledge about genes and proteins. Database (Oxford). 2016 Jul 3;2016. pii: baw100."],
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
        query0 = "select project_id from resource where resource_id=%s"
        cursor.execute(query0,(resource_id))
        if cursor.rowcount==0:
            return render_template('error.html')
        project_id=cursor.fetchall()[0][0]
        return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/myevaluations')

    elif request.form['formType'] == 'deleteEval':
        query1 = "select resource_type,project_id from resource where resource_id=%s"
        cursor.execute(query1, (resource_id))  # get resource type
        tt = cursor.fetchall()
        res_type = tt[0][0]
        project_id = tt[0][1]

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
        return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/myevaluations')

    elif request.form['formType'] == 'evalForm':
        query1 = "select resource_type,project_id from resource where resource_id=%s"
        cursor.execute(query1, (resource_id))  # get resource type
        tt = cursor.fetchall()
        res_type = tt[0][0]
        project_id = tt[0][1]

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

            if (thisAnswer == 'no') or (not thisComment and not thisURLComment): # enter evaluation in database, with comments if this answer is yes or yesbut
                query5 = "update evaluation set answer=%s,url_comment=%s,comment=%s where resource_id=%s and q_id=%s and user_id=%s"
                cursor.execute(query5, (thisAnswer, None, None, resource_id, q_id, current_user.user_id))
                conx.commit()
            else:
                if thisComment:
                    if thisURLComment:
                        query5 = "update evaluation set answer=%s,url_comment=%s,comment=%s where resource_id=%s and q_id=%s and user_id=%s"
                        cursor.execute(query5,
                                       (thisAnswer, thisURLComment, thisComment, resource_id, q_id, current_user.user_id))
                        conx.commit()
                    else:
                        query5 = "update evaluation set answer=%s,url_comment=%s,comment=%s where resource_id=%s and q_id=%s and user_id=%s"
                        cursor.execute(query5, (thisAnswer, None, thisComment, resource_id, q_id, current_user.user_id))
                        conx.commit()
                else:
                    if thisURLComment:
                        query5 = "update evaluation set answer=%s,url_comment=%s,comment=%s where resource_id=%s and q_id=%s and user_id=%s"
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

        return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/myevaluations')

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
        query0 = "select project_id from resource where resource_id=%s"
        cursor.execute(query0,(resource_id))
        if cursor.rowcount==0:
            return render_template('error.html')
        project_id=cursor.fetchall()[0][0]
        return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/resources')

    elif request.form['formType'] == 'evalForm':
        query1 = "select resource_type, project_id from resource where resource_id=%s"
        cursor.execute(query1,(resource_id))  # get resource type
        tt = cursor.fetchall()
        res_type = tt[0][0]
        project_id = tt[0][1]

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

            if thisAnswer != 'no': # enter evaluation in database, with comments if this answer is yes or yesbut
                if thisComment:
                    if thisURLComment:
                        query5 = "insert into evaluation(user_id,q_id,answer,url_comment,comment,resource_id,project_id) values(%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(query5, (current_user.user_id, q_id, thisAnswer, thisURLComment, thisComment, resource_id, project_id))
                        conx.commit()
                    else:
                        query4 = "insert into evaluation(user_id,q_id,answer,comment,resource_id,project_id) values(%s,%s,%s,%s,%s,%s)"
                        cursor.execute(query4, (current_user.user_id, q_id, thisAnswer, thisComment, resource_id, project_id))
                        conx.commit()
                else:
                    if thisURLComment:
                        query4 = "insert into evaluation(user_id,q_id,answer,url_comment,resource_id,project_id) values(%s,%s,%s,%s,%s,%s)"
                        cursor.execute(query4, (current_user.user_id, q_id, thisAnswer, thisURLComment, resource_id, project_id))
                        conx.commit()
                    else:
                        query4 = "insert into evaluation(user_id,q_id,answer,resource_id,project_id) values(%s,%s,%s,%s,%s)"
                        cursor.execute(query4, (current_user.user_id, q_id, thisAnswer, resource_id, project_id))
                        conx.commit()
            else:
                query4 = "insert into evaluation(user_id,q_id,answer,resource_id,project_id) values(%s,%s,%s,%s,%s)"
                cursor.execute(query4, (current_user.user_id,q_id,thisAnswer,resource_id,project_id))
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
            query9 = "insert into average(resource_id,q_id,avg,project_id) values(%s,%s,%s,%s)"
            cursor.execute(query9,(resource_id,q_id,average,project_id))
            conx.commit()

        flash("Evaluation submitted.", "success")
        return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/resources')
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

            query2 = "insert into resource(resource_name,resource_type,url,description,project_id) values(%s,%s,%s,%s,(select project_id from project where project_name=%s))"
            cursor.execute(query2,(resourcename,resourcetype,resourceurl,resourcedesc,projectname))
            conx.commit()

        saveqtotal=request.form['saveqtotal']

        for r in range(int(saveqtotal)):  # get the first x questions + ignore the rest
            qucontent=request.form['saveq'+str(r+1)]
            query3 = "insert into question(num,version,res_type,content) values(%s,'1','example_type',%s)"
            cursor.execute(query3,(r+1,qucontent))
            conx.commit()

        flash("Project successfully created.", "success")
        return redirect(ENTRY_POINT + '/projects')

# recursive method to eliminate segments of URL after last occurrence of "/" starting from end and return exact matches
# returns None if no match found
# returns 2d list: [[resource_id, resource_name, resource_type]]
def cutSegment(url, cursor, pattern):
    index = url.rfind('/')
    checkIndex = url.rfind('#')
    if (pattern == 'hostpath' and index == -1) or (pattern == 'fragment' and (index < checkIndex or checkIndex == -1)):
        return None
    else:
        cutURL = url[:(index + 1)] # look for exact match to this path with '/' at end
        input = '%' + cutURL
        query = "select resource_id,resource_name,resource_type,project_id from resource where url like %s"
        cursor.execute(query, (input))
        if cursor.rowcount==0: # no exact match found
            cutURL = url[:index] # look for exact match to this path without '/' at end
            input = '%' + cutURL
            query = "select resource_id,resource_name,resource_type,project_id from resource where url like %s"
            cursor.execute(query, (input))
            if cursor.rowcount==0: # no match found, keep eliminating segments
                return cutSegment(cutURL, cursor, 'hostpath')
            elif cursor.rowcount>1:
                return None
            else:
                result = cursor.fetchall()
                return result
        elif cursor.rowcount>1: # returned multiple exact matches... something is wrong
            return None
        else:
            result = cursor.fetchall()
            return result


# parameter is whole url
def findResourceByFrag(url,cursor):
    index = url.find('://') # remove scheme
    a = url[(index + 3):]
    if a[:4] == "www.":
        a = a[4:]
    if a[(len(a) - 1):] == "/":
        a = a[:len(a) - 1]
    result = cutSegment(a, cursor, 'fragment')
    if not result:
        return None
    else:
        return result[0]


# parameter is whole url
def findResourceByHostPath(url,cursor):
    o = urlparse(url)
    a = o.netloc + o.path
    if a[:4] == "www.":
        a = a[4:]

    input = '%' + a
    query = "select resource_id,resource_name,resource_type,project_id from resource where url like %s"
    cursor.execute(query, (input))
    if cursor.rowcount > 1:
        return None
    elif cursor.rowcount == 0:
        if a[(len(a) - 1):] == "/":
            a = a[:len(a) - 1]
            input = '%' + a
            query = "select resource_id,resource_name,resource_type,project_id from resource where url like %s"
            cursor.execute(query, (input))
            if cursor.rowcount > 1:
                return None
            elif cursor.rowcount == 0:
                result = cutSegment(a, cursor, 'hostpath')
                if result is None:
                    return None
                else:
                    return result[0]
            else:
                result = cursor.fetchall()
                return result[0]
        else:
            result = cutSegment(a, cursor, 'hostpath')
            if result is None:
                return None
            else:
                return result[0]
    else:
        result = cursor.fetchall()
        return result[0]


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
        query = "select resource_id,resource_name,resource_type,project_id from resource where url like %s"
        cursor.execute(query, (input))
        if cursor.rowcount>1:
            return None
        elif cursor.rowcount == 0:
            if a[(len(a) - 1):] == "/":
                a = a[:len(a) - 1]
                input = '%' + a
                query = "select resource_id,resource_name,resource_type,project_id from resource where url like %s"
                cursor.execute(query, (input))
                if cursor.rowcount>1:
                    return None
                elif cursor.rowcount == 0:
                    if url.find('lincsportal.ccs.miami.edu/datasets/#/view/') != -1:
                        result = findResourceByFrag(url, cursor)
                        return result
                    else:
                        result = findResourceByHostPath(url, cursor)
                        return result
                else:
                    result = cursor.fetchall()
                    return result[0]
            else:
                if url.find('lincsportal.ccs.miami.edu/datasets/#/view/') != -1:
                    result = findResourceByFrag(url, cursor)
                    return result
                else:
                    result = findResourceByHostPath(url, cursor)
                    return result
        else:
            result = cursor.fetchall()
            return result[0]


# API to get this resource's questions for insignia #
# returns 'None' if invalid URL, 0 or more than 1 matches for URL, or no questions for this resource's type
# otherwise returns list of questions, resource name, resource ID, # of questions
@app.route(ENTRY_POINT + '/api/getQ')
def getQAPI():

    resArr = []
    conx = mysql.get_db()
    cursor = conx.cursor()
    url = request.args.get('url')
    result = findResource(url,cursor)
    if result is None:
        return jsonify('None')
    else:
        theID = result[0]
        theType = result[2]
        theName = result[1]

        # Get questions for this resource's type #
        query1 = "select content from question where version=(select max(version) from question) and res_type=%s order by num"
        cursor.execute(query1, (theType))
        sqnum = cursor.rowcount

        # No questions for this resource type yet
        if sqnum == 0:
            return jsonify('None')
        else:
            data=cursor.fetchall()
            for row in data:
                resArr.append(row[0]) # text type returned from database is unicode
            resArr.append(theName)
            resArr.append(str(theID).encode("utf-8").decode("utf-8"))
            resArr.append(str(sqnum).encode("utf-8").decode("utf-8"))
            return jsonify(resArr)


# API to get this resource's average scores for insignia #
# returns 'None' if invalid URL, or 0 or more than 1 matches to URL, or no score yet
# otherwise returns comma separated string of scores
@app.route(ENTRY_POINT + '/api/getAvg')
def getAvgAPI():
    avgArr=[]
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Get this resource's average scores to make insignia, search by URL #
    url = request.args.get('url')
    result = findResource(url,cursor)
    if result is None:
        return jsonify('None')
    else:
        resource_id = result[0]
        query0 = "select avg from average t1 inner join question t2 on t1.q_id=t2.q_id where resource_id=%s order by num"
        cursor.execute(query0,(resource_id))

        # No averages yet for this resource - has not yet been evaluated #
        if cursor.rowcount==0:
            return jsonify('None')
        # Average scores exist - Return in comma separated string #
        else:
            result1=cursor.fetchall()
            for row in result1:
                avgArr.append(row[0])
            return jsonify(avgArr)

# API to enter evaluations into database and update average #
# parameters: url, q1a (answer to q1), q1u (urlcomment to 1q), q1c (comment to q1), q2a, q2u, q2c,..., qna, qnu, qnc
# answers may only be: 'yes', 'no', 'yesbut'
# comments are not necessary
# returns: '0' if unsuccessful, '1' if successful
# if evaluating a resource with 16 questions, must enter answers for each question (i.e. q1a,...,q16a)
# if no comment or urlcomment submitted, null in database
# evaluation entered in database with user_id=-1
@app.route(ENTRY_POINT + '/api/evaluate')
def evaluateAPI():
    conx = mysql.get_db()
    cursor = conx.cursor()

    url = request.args.get('url')
    result = findResource(url,cursor)
    if result is None:
        return '0'
    else:
        resource_id=result[0]
        res_type=result[2]
        project_id=result[3]

        query1 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query1,(res_type,res_type))
        qtotal = cursor.fetchall()[0][0]

        # before beginning to enter anything in database, check that each question has an answer
        for a in range(qtotal):
            thisAnswer = request.args.get('q'+str(a+1)+'a')
            thisURLComment = request.args.get('q'+str(a+1)+'u')
            if not (thisAnswer=='yes' or thisAnswer=='no' or thisAnswer=='yesbut'):
                return '0'
            if thisURLComment and not validators.url(thisURLComment):
                return '0'

        for i in range(qtotal):  # for each question
            thisComment = request.args.get('q'+str(i+1)+'c') # get the comment
            thisURLComment = request.args.get('q'+str(i+1)+'u') # get the url comment
            thisAnswer = request.args.get('q'+str(i+1)+'a')  # get the answer

            query2 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
            cursor.execute(query2, (i + 1, res_type, res_type))  # get q_id
            q_id = cursor.fetchall()[0][0]

            # user_id
            # project_id
            # not reversible - you cannot go back and find this evaluation

            if thisAnswer != 'no':  # enter evaluation in database, with comments if this answer is yes or yesbut
                if thisComment:
                    if thisURLComment:
                        query5 = "insert into evaluation(user_id,q_id,answer,url_comment,comment,resource_id,project_id) values(%s,%s,%s,%s,%s,%s,%s)"
                        cursor.execute(query5, (-1, q_id, thisAnswer, thisURLComment, thisComment, resource_id, project_id))
                        conx.commit()
                    else:
                        query4 = "insert into evaluation(user_id,q_id,answer,comment,resource_id,project_id) values(%s,%s,%s,%s,%s,%s)"
                        cursor.execute(query4, (-1, q_id, thisAnswer, thisComment, resource_id, project_id))
                        conx.commit()
                else:
                    if thisURLComment:
                        query4 = "insert into evaluation(user_id,q_id,answer,url_comment,resource_id,project_id) values(%s,%s,%s,%s,%s,%s)"
                        cursor.execute(query4, (-1, q_id, thisAnswer, thisURLComment, resource_id, project_id))
                        conx.commit()
                    else:
                        query4 = "insert into evaluation(user_id,q_id,answer,resource_id,project_id) values(%s,%s,%s,%s,%s)"
                        cursor.execute(query4, (-1, q_id, thisAnswer, resource_id, project_id))
                        conx.commit()
            else:
                query4 = "insert into evaluation(user_id,q_id,answer,resource_id,project_id) values(%s,%s,%s,%s,%s)"
                cursor.execute(query4, (-1, q_id, thisAnswer, resource_id, project_id))
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

            average = float(total) / count
            query8 = "delete from average where resource_id=%s and q_id=%s"
            cursor.execute(query8, (resource_id, q_id))
            conx.commit()  # clear this entry in average
            query9 = "insert into average(resource_id,q_id,avg,project_id) values(%s,%s,%s,%s)"
            cursor.execute(query9, (resource_id, q_id, average, project_id))
            conx.commit()
        return '1'

# API to get questions based on resource type #
# returns 'None' if invalid URL, 0 or more than 1 matches for URL, or no questions for this resource's type
# otherwise returns list of questions
@app.route(ENTRY_POINT + '/api/getQByType')
def getQByTypeAPI():

    resArr = []
    conx = mysql.get_db()
    cursor = conx.cursor()
    theType = request.args.get('type')
    if theType=='Dataset' or theType=='Tool' or theType=='Repository':

        # Get questions for this resource's type #
        query1 = "select content from question where version=(select max(version) from question) and res_type=%s order by num"
        cursor.execute(query1, (theType))

        # No questions for this resource type yet
        if cursor.rowcount == 0:
            return jsonify('None')
        else:
            data = cursor.fetchall()
            for row in data:
                resArr.append(row[0])  # text type returned from database is unicode
            return jsonify(resArr)
    else:
        return 'None'

# Download Chrome extension page #
@app.route(ENTRY_POINT + '/chromeextension')
def chromeextension():
    return render_template('chromext.html')

# Download Bookmarklet page #
@app.route(ENTRY_POINT + '/bookmarklet')
def bookmarklet():
    return render_template('bookmarklet.html')

# Searches exact URL match
@app.route(ENTRY_POINT + '/redirectedFromExt', methods=['POST', 'GET'])
def redirectedFromExt():

    # URL reached through POST only through browser extension click #
    # if request.method == 'POST':
    theName = request.args.get('theName').strip()
    theURL = request.args.get('theURL')
    theType = request.args.get('theType')
    theSrc = request.args.get('theSrc')
    theDescrip = request.args.get('theDescrip')
    if theDescrip:
        theDescrip = theDescrip.strip()
    else:
    # if theSrc == 'LINCS Data Portal':
        dsDescrip1 = request.args.get('dsDescrip1').strip()
        dsDescrip2 = request.args.get('dsDescrip2').strip()
        theDescrip = dsDescrip1 + " " + dsDescrip2

    # Check if this resource exists in database - if not, insert into database #
    conx = mysql.get_db()
    cursor = conx.cursor()
    query1 = "select resource_id from resource where url=%s"
    cursor.execute(query1, (theURL))
    result = cursor.fetchall()

    # This resource is not in database yet --> insert #
    if not result:
        query2 = "insert into resource(resource_name,resource_type,url,description,project_id) values(%s,%s,%s,%s,%s)"

        if theSrc == 'LINCS Data Portal' or theSrc == 'LINCS Tools':
            cursor.execute(query2, (theName, theType, theURL, theDescrip, 1))
            conx.commit()
        elif theSrc == 'MOD':
            cursor.execute(query2, (theName, theType, theURL, theDescrip, 2))
            conx.commit()
        elif theSrc == 'BioToolBay':
            cursor.execute(query2, (theName, theType, theURL, theDescrip, 3))
            conx.commit()
        elif theSrc == 'DataMed':
            cursor.execute(query2, (theName, theType, theURL, theDescrip, 4))
            conx.commit()
        elif theSrc == 'Fairsharing':
            cursor.execute(query2, (theName, theType, theURL, theDescrip, 5))
            conx.commit()
        else:
            cursor.execute(query2, (theName, theType, theURL, theDescrip, 0))
            conx.commit()
        query3 = "select resource_id from resource where url=%s"
        cursor.execute(query3,(theURL))
        resource_id=cursor.fetchall()[0][0]
    else:
        resource_id = result[0][0]

    # If logged in, go to evaluation form for this resource  - new evaluation or modified #
    if current_user.is_authenticated:
        query3 = "select * from evaluation where user_id=%s and resource_id=%s"
        cursor.execute(query3,(current_user.user_id,resource_id))
        result = cursor.fetchall()
        if not result:
            return redirect(url_for('newevaluation',resourceid=resource_id))
        else:
            return redirect(url_for('modifyevaluation',resourceid=resource_id))

    # If not logged in, go to login page with evaluation form URL #
    # with resource information saved in query string (passed through GET) #
    else:
        # redirectFromExt='yes'
        flash("Please log in to view this page.", "danger")
        return redirect(login_url(ENTRY_POINT + '/login', next_url=url_for('redirectedFromExt', theName=theName,
                                                                           theURL=theURL, theType=theType,
                                                                           theDescrip=theDescrip, theSrc=theSrc)))



            # return redirect(url_for('login',redirectFromExt=redirectFromExt,theName=theName,theURL=theURL,theType=theType,theDescrip=theDescrip,
            #                         next=url_for('redirectedFromExt',theName=theName,theURL=theURL, theType=theType,theDescrip=theDescrip)))


    # # URL reached through GET if redirected from login or manually entered #
    # # If redirected from login, resource should be in database. If manually entered, resource may not be in database #
    # # Check if resource in database in extensionEvaluation #
    # else:
    #     # Got here from login or manually entered while logged in #
    #     if current_user.is_authenticated:
    #         theName = request.args.get('theName').strip()
    #         theURL = request.args.get('theURL')
    #         theType = request.args.get('theType')
    #         theDescrip = request.args.get('theDescrip').strip()
    #         return extensionEvaluation(theName=theName, theURL=theURL, theType=theType, theDescrip=theDescrip)
    #     # Got here by manual entering because still not logged in #
    #     else:
    #         return render_template('error.html', errormsg='Invalid URL.')

# def extensionEvaluation(theName, theURL, theType, theDescrip):
#     conx = mysql.get_db()
#     cursor = conx.cursor()
#
#     # Check if resource with these fields exists in database first #
#     query1 = "select * from resource where resource_name=%s and url=%s and resource_type=%s and description=%s"
#     cursor.execute(query1, (theName, theURL, theType, theDescrip))
#     resd = cursor.fetchall()
#
#     # This resource does not exist - wrong URL #
#     if not resd:
#         return render_template('error.html', errormsg='No such digital object.')
#
#     # Resource does exist --> pull up correct form #
#     else:
#         setq = []
#
#         query3 = "select resource_id from resource where resource_name=%s"
#         cursor.execute(query3, (theName))
#         rtt = cursor.fetchall()
#         resource_id = rtt[0][0]
#
#         query8 = "select count(*) from question where res_type=%s and version=(select max(version) from question where res_type=%s)"
#         cursor.execute(query8, (theType, theType))
#         sqnum = cursor.fetchall()[0][0]
#
#         for i in range(1, sqnum + 1):
#             query4 = "select num,version,content from question where res_type=%s and num=%s and version=(select max(version) from question where res_type=%s) order by num"
#             cursor.execute(query4, (theType, i, theType))
#             cursor.execute("select num,version,content from question where res_type='" + theType
#                            + "' and num=" + str(
#                 i) + " and version=(select max(version) from question) order by num")
#             qd = cursor.fetchall()
#             for row in qd:
#                 setq.append(row)
#
#         # Decide whether to show modify evaluation or new evaluation #
#         query5 = "select * from evaluation where resource_id=%s and user_id=%s"
#         cursor.execute(query5, (resource_id, current_user.user_id))
#         chr = cursor.fetchall()
#
#         # User has not evaluated this resource yet --> show new evaluation #
#         if not chr:
#             return render_template('newevaluation.html', resource_name=theName, resource_id=resource_id,
#                                    resource_type=theType, url=theURL,
#                                    description=theDescrip, setq=setq, redirectedFromExt='yes',sqnum=sqnum)
#
#         # User has evaluated resource --> show modify evaluation #
#         else:
#             setanswers = []
#             setcomments = []
#
#             query6 = "select q_id, answer from evaluation where resource_id=%s and user_id=%s order by q_id"
#             cursor.execute(query6, (resource_id, current_user.user_id))
#             data = cursor.fetchall()
#             for row in data:
#                 setanswers.append(row)
#
#             query7 = "select comment from evaluation where resource_id=%s and user_id=%s order by q_id"
#             cursor.execute(query7, (resource_id, current_user.user_id))
#             data = cursor.fetchall()
#             for row in data:
#                 setcomments.append(str(row[0]))
#
#             return render_template('modifyevaluation.html',
#                                    resource_name=theName, resource_id=resource_id, resource_type=theType,
#                                    url=theURL,
#                                    description=theDescrip, setanswers=setanswers, setcomments=setcomments,
#                                    setq=setq, redirectedFromExt='yes',sqnum=sqnum)
#




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


# class AnonymousUserMixin(object):
#     '''
#     This is the default object for representing an anonymous user.
#     '''
#     @property
#     def is_authenticated(self):
#         return False
#
#     @property
#     def is_active(self):
#         return False
#
#     @property
#     def is_anonymous(self):
#         return True
#
#     def get_id(self):
#         return str(1234567890)


if __name__ == "__main__":
    app.run(debug=True)