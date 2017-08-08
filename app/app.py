from flask import Flask, request, redirect, render_template, flash, jsonify,url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin, login_url
from flask_cors import CORS
from flaskext.mysql import MySQL
import re

mysql = MySQL()

app = Flask(__name__)
CORS(app)
app.secret_key = 'thisstring'


# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'temp123'
# app.config['MYSQL_DATABASE_DB'] = 'proj1'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# app.config['MYSQL_DATABASE_USER'] = 'fairshake'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'systemsbiology'
# app.config['MYSQL_DATABASE_DB'] = 'fairshake'
# app.config['MYSQL_DATABASE_HOST'] = '146.203.54.78'
app.config.from_pyfile('config.py')
mysql.init_app(app)
ENTRY_POINT = app.config['ENTRY_POINT']

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = ENTRY_POINT + "/login"


# Required method for Flask login: Given user ID, returns user object #
@login_manager.user_loader
def load_user(user_id):
    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select username,first_name,last_name,password from user where user_id=%s"
    cursor.execute(query1,(user_id))
    ud = cursor.fetchall()

    if not ud:
        return None
    else:
        username = ud[0][0]
        first_name = ud[0][1]
        last_name = ud[0][2]
        password = ud[0][3]

    # Return user object with these fields #
    return User(username, first_name, last_name, user_id, password)


# Home page #
@app.route(ENTRY_POINT + '/', methods=['GET'])
@app.route(ENTRY_POINT, methods=['GET'])
def doe():
    projectlist=[]
    conx = mysql.get_db()
    cursor = conx.cursor()

    cursor.execute("select * from project order by project_id")
    data=cursor.fetchall()
    for row in data:
        projectlist.append(row)

    return render_template('doehome.html',projectlist=projectlist)


# API to get this resource's average scores for insignia #
@app.route(ENTRY_POINT + '/api/chrome_extension/getAvg')
def chrome_extension_getAvg():
    avgStr=""
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Get this resource's average scores to make insignia, search by URL #
    if request.args.get('select') == 'URL':
        theURL = request.args.get('theURL')
        query1 = "select avg from average t1 inner join resource t2 on t1.resource_id=t2.resource_id where url=%s"
        cursor.execute(query1,(theURL))
        result1 = cursor.fetchall()

    # Get this resource's average scores to make insignia, search by name #
    elif request.args.get('select') == 'name':
        theName = request.args.get('theName')
        query2 = "select avg from average t1 inner join resource t2 on t1.resource_id=t2.resource_id where resource_name=%s"
        cursor.execute(query2,(theName))
        result1 = cursor.fetchall()

    # No averages yet for this resource - has not yet been evaluated #
    if not result1:
        return 'None'

    # Average scores exist - Return in comma separated string #
    else:
        for i in range(16):
            avgStr = avgStr + str(result1[i][0]) + ","
        return avgStr


# API to get this resource's questions for insignia #
@app.route(ENTRY_POINT + '/api/chrome_extension/getQ')
def chrome_extension_getQ():
    resArr=[]
    theType = request.args.get('theType')
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Get questions for this resource's type #
    query1 = "select content from question where version=(select max(version) from question) and res_type=%s order by num"
    cursor.execute(query1,(theType))
    result1 = cursor.fetchall()

    # No questions for this resource type - invalid #
    if not result1:
        return 'None'

    # Return questions #
    else:
        for row in result1:
            resArr.append(row[0])
        return str(resArr)


# Download Chrome extension page #
@app.route(ENTRY_POINT + '/chromeextension')
def chromeextension():
    return render_template('chromext.html')


# Login page #
@app.route(ENTRY_POINT + "/login", methods=['GET', 'POST'])
def login():
    # # Go to login page - accessed #
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

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # If redirected from page with login_required view, that page is saved in "next" parameter by Flask Login #
        prevPage = request.args.get('next')

        conx = mysql.get_db()
        cursor = conx.cursor()
        query1 = "select username, password, user_id from user where username=%s and password=%s"
        cursor.execute(query1,(username,password))
        data = cursor.fetchall()

        # User with this username and password not found in database #
        if not data:
            flash("Username or password is wrong.","danger")
            return redirect(ENTRY_POINT + '/login')
        # Correct username and password, log user in #
        else:
            user_id = data[0][2]
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
    evproj=[]
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Get projects this user has begun evaluating #
    query1 = "select * from project where project_id in (select distinct(project_id) from evaluation where user_id=%s)"
    cursor.execute(query1,(current_user.user_id))
    evprojd = cursor.fetchall()
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
        data = cursor.fetchone()

        # Username is new #
        if data is None:
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
                    return "error"

        # Username already exists in database #
        else:
            flash("Account with this username already exists.","danger")
            return redirect(ENTRY_POINT + '/register')


# Project resources list page #
@app.route(ENTRY_POINT + '/project/<int:proj>/resources/', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route(ENTRY_POINT + '/project/<int:proj>/resources', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route(ENTRY_POINT + '/project/<int:proj>/resources/page/<int:page>', methods=['GET'])
def resourcelist(proj,page):
    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select * from project where project_id=%s"
    cursor.execute(query1,(proj))
    projinfo = cursor.fetchall()
    if not projinfo:
        return "error"

    resourceslist = []  # For resources' information #
    userres = []  # For resources this user has evaluated - for check marks #
    listeval = []  # Number of evaluations resources have #
    per_page = 10  # Number of resources per page #
    pagecount = per_page * page

    avginfo = []  # Average scores for insignia #
    qdat = []  # Questions for insignia #

    # Add this project's resources to list #
    query3 = "select * from resource where project_id=%s"
    cursor.execute(query3,(proj))  # get resource info to display
    data = cursor.fetchall()
    for row in data:
        resourceslist.append(row)
    total = len(resourceslist)

    # Go through all resources #
    for i in range(total):
        templist = []
        xlist = []

        templist.append(str(resourceslist[i][0]))
        xlist.append(str(resourceslist[i][0]))

        # Get number of evaluations for this resource #
        query4 = "select count(distinct(user_id)) from evaluation where resource_id=%s"
        cursor.execute(query4, (resourceslist[i][0]))
        eval1 = cursor.fetchall()
        listeval.append(eval1[0][0])

        # Go through all 16 questions #
        for t in range(16):
            query5 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
            cursor.execute(query5,(t+1,resourceslist[i][3],resourceslist[i][3]))  # can later add in project_id if res_type will have same names
            q_id = cursor.fetchall()[0][0]

            query6 = "select avg from average where resource_id=%s and q_id=%s"
            cursor.execute(query6,(resourceslist[i][0],q_id))
            adata = cursor.fetchall()

            # No average for this resource for this question #
            if not adata:
                templist.append('None')
                # break  # Removed break - messes up if there are errors in database

            # Add averages to list #
            else:
                templist.append(adata[0][0])

            # Add questions to list #
            query7 = "select content from question where q_id=%s"
            cursor.execute(query7,(q_id))
            tst = cursor.fetchall()
            xlist.append(tst[0][0])

        avginfo.append(templist)  # Append list of averages for this resource #
        qdat.append(xlist) # Append list of questions for this resource (a project may have multiple resource types)

    if current_user.is_authenticated:  # this person is logged in (resourceslist is a public page) for check marks
        conx_getres = mysql.get_db()
        cursor = conx_getres.cursor()
        query8 = "select * from resource where resource_id in (select resource_id from evaluation where user_id=%s)"
        cursor.execute(query8,(current_user.user_id))  # should maybe change this in subquery #check off ones that this user has evaluated
        data = cursor.fetchall()
        for row in data:
            userres.append(row[0])  # list containing resource ids of resources this user evaluated

    # For pagination: showlast is position of last resource #
    if pagecount > total:
        showlast = total
    else:
        showlast = pagecount


    return render_template('projhome.html',
                           resourceslist=resourceslist, listeval=listeval, total=total, pagecount=pagecount, page=page,
                           per_page=per_page, showlast=showlast, userres=userres, avginfo=avginfo, qdat=qdat, proj=proj,projinfo=projinfo)


# Project my evaluations page #
@app.route(ENTRY_POINT + "/project/<int:proj>/myevaluations", defaults={'page': 1}, methods=['GET'])
@app.route(ENTRY_POINT + "/project/<int:proj>/myevaluations/", defaults={'page': 1}, methods=['GET'])
@app.route(ENTRY_POINT + "/project/<int:proj>/myevaluations/page/<int:page>", methods=['GET'])
@login_required
def myevals(proj, page):
    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select * from project where project_id=%s"
    cursor.execute(query1,(proj))
    projinfo = cursor.fetchall()
    if cursor.rowcount == 0:
        return "error"

    resources = []
    listeval = []
    per_page = 10
    pagecount = per_page * page
    showlast = 0

    avginfo = []  # average insignia
    ans = []  # my answers insignia
    qdat = []

    conx_getres = mysql.get_db()
    cursor = conx_getres.cursor()
    query2 = "select count(distinct(resource_id)) from evaluation where user_id=%s and project_id=%s"
    cursor.execute(query2,(current_user.user_id,proj))  # display only those resources this user has evaluated
    data1 = cursor.fetchall()
    totalres = data1[0][0]

    conx_getres1 = mysql.get_db()
    cursor = conx_getres1.cursor()
    query3 = "select * from resource where resource_id in (select resource_id from evaluation where user_id=%s and project_id=%s)"
    cursor.execute(query3,(current_user.user_id,proj))  # get res info
    data = cursor.fetchall()
    for row in data:
        resources.append(row)

    for i in range(totalres):  # go through all my evaluations
        nlist = []
        templist = []  # average insignia
        xlist = []

        conx_getnumeval1 = mysql.get_db()
        cursor = conx_getnumeval1.cursor()
        query4 = "select count(distinct(user_id)) from evaluation where resource_id=%s"
        cursor.execute(query4,(resources[i][0]))
        eval1 = cursor.fetchall()
        listeval.append(eval1[0][0])

        templist.append(str(resources[i][0]))
        xlist.append(str(resources[i][0]))

        for t in range(16):  # about question
            query5 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
            cursor.execute(query5,(t+1,resources[i][3],resources[i][3]))
            q_id = cursor.fetchall()[0][0]
            query6 = "select avg from average where resource_id=%s and q_id=%s"
            cursor.execute(query6,(resources[i][0],q_id))
            adata = cursor.fetchone()
            if adata is None:  # did not find an average for this resource for this question
                templist.append('None')
                break  # this resource has not yet been evaluated - newly added, break out of this resource
            else:
                templist.append(adata[0])  # else add this resources averages to templist --> avginfo
            odata = cursor.fetchall()  # clean up this cursor call

            query7 = "select content from question where q_id=%s"
            cursor.execute(query7,(q_id))
            tst = cursor.fetchall()
            xlist.append(tst[0][0])

        avginfo.append(templist)
        qdat.append(xlist)

        nlist.append(resources[i][0])  # first index 0 is resource_id
        query8 = "select resource_id,answer from evaluation where resource_id=%s and user_id=%s order by q_id"
        cursor.execute(query8,(resources[i][0],current_user.user_id))  # my insignia answers
        nd = cursor.fetchall()  # iterating through
        for row in nd:
            if row[1] == 'yes':
                nlist.append(1)
            elif row[1] == 'no':
                nlist.append(-1)
            elif row[1] == 'yesbut':
                nlist.append(0)
        ans.append(nlist)

    if pagecount > totalres:
        showlast = totalres
    else:
        showlast = pagecount

    return render_template('myevaluations.html',
                           page=page, resources=resources, per_page=per_page, pagecount=pagecount, showlast=showlast,
                           totalres=totalres, listeval=listeval, avginfo=avginfo, ans=ans, qdat=qdat, proj=proj, projinfo=projinfo)


# Evaluation form - Modify, old answers automatically filled in #
@app.route(ENTRY_POINT + "/modifyevaluation", methods=['POST'])
@login_required
def modifyevaluation():
    setanswers = []
    setcomments = []
    setq = []

    resourceid = request.form['resourceid']

    conx_getres = mysql.get_db()
    cursor = conx_getres.cursor()
    query1 = "select q_id, answer from evaluation where resource_id=%s and user_id=%s order by q_id"
    cursor.execute(query1,(resourceid,current_user.user_id))
    data = cursor.fetchall()
    for row in data:
        setanswers.append(row)

    query2 = "select comment from evaluation where resource_id=%s and user_id=%s order by q_id"
    cursor.execute(query2,(resourceid,current_user.user_id))
    data = cursor.fetchall()
    for row in data:
        setcomments.append(str(row[0]))

    query3 = "select * from resource where resource_id=%s"
    cursor.execute(query3,(resourceid))
    row1 = cursor.fetchone()
    resource_name = row1[1]
    resource_id = row1[0]
    resource_type = row1[3]
    url = row1[2]
    description = row1[4]

    for i in range(1, 17):
        query4 = "select num,version,content from question where res_type=%s and num=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query4,(resource_type,i,resource_type))
        qd = cursor.fetchall()
        for row in qd:
            setq.append(row)

    return render_template('modifyevaluation.html',
                           resource_name=resource_name, resource_id=resource_id, resource_type=resource_type, url=url,
                           description=description, setanswers=setanswers, setcomments=setcomments, setq=setq)


# Evaluation form - New evaluation #
@app.route(ENTRY_POINT + "/newevaluation", methods=['POST'])
@login_required
def newevaluation():

    if request.method == 'POST':
        setq = []

        resourceid = request.form['resourceid']

        conx_getres = mysql.get_db()
        cursor = conx_getres.cursor()
        query1 = "select * from resource where resource_id=%s"
        cursor.execute(query1,(resourceid))
        row1 = cursor.fetchone()
        resource_name = row1[1]
        resource_id = row1[0]
        resource_type = row1[3]
        url = row1[2]
        description = row1[4]

        for i in range(1, 17):
            query2 = "select num,version,content from question where res_type=%s and num=%s and version=(select max(version) from question) order by num"
            cursor.execute(query2,(resource_type,i))
            qd = cursor.fetchall()
            for row in qd:
                setq.append(row)

        return render_template('newevaluation.html',
                               resource_name=resource_name, resource_id=resource_id, resource_type=resource_type, url=url,
                               description=description, setq=setq)


# Enter modify submission into database #
@app.route(ENTRY_POINT + '/modifysubmitted', methods=['POST'])
@login_required
def modifysubmitted():
    answerlist = []
    commentlist = []

    resource_id = request.form['hiddenfield']

    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select resource_type,project_id from resource where resource_id=%s"
    cursor.execute(query1,(resource_id))  # get resource type
    tt = cursor.fetchall()
    res_type = tt[0][0]
    project_id = tt[0][1]

    for i in range(16):  # for each question 1-16
        thisanswer = request.form['q' + str((i + 1))]  # get answer for this question 1-16
        thiscomment = request.form['q' + str((i + 1)) + 'yesbutcomment']  # get comment for this question 1-16

        query2 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query2,(i+1,res_type,res_type))  # get q_id of most recent q 1-16
        q_id = cursor.fetchall()[0][0]  # use most recent q_id for this question 1-16

        query3 = "delete from evaluation where q_id=%s and resource_id=%s and user_id=%s"
        cursor.execute(query3,(q_id,resource_id,current_user.user_id))  # clear from evaluation my evaluation for this resource (of most updated q version)
        conx.commit()

        query4 = "insert into evaluation(q_id,answer,user_id,resource_id,project_id) values(%s,%s,%s,%s,%s)"
        cursor.execute(query4,(q_id,thisanswer,current_user.user_id,resource_id,project_id))
        conx.commit()
        if thisanswer == 'yesbut':
            query5 = "update evaluation set comment=%s where q_id=%s and user_id=%s and resource_id=%s"
            cursor.execute(query5,(thiscomment,q_id,current_user.user_id,resource_id))
            conx.commit()

        templist = []
        total = 0
        num = 0

        query6 = "select answer from evaluation where resource_id=%s and q_id=%s"
        cursor.execute(query6,(resource_id,q_id))  # start to update average in average table
        data = cursor.fetchall()
        for row in data:
            templist.append(row[0])
            if row[0] == 'yes':
                total = total + 1
            elif row[0] == 'no':
                total = total - 1

        query7 = "select count(answer) from evaluation where resource_id=%s and q_id=%s"
        cursor.execute(query7,(resource_id,q_id))
        dd = cursor.fetchall()
        count = dd[0][0]

        average = float(total) / count
        query8 = "delete from average where resource_id=%s and q_id=%s"
        cursor.execute(query8,(resource_id,q_id))
        conx.commit()  # clear this entry in average
        query9 = "insert into average(resource_id,q_id,avg,project_id) values(%s,%s,%s,%s)"
        cursor.execute(query9,(resource_id,q_id,average,project_id))
        conx.commit()

    flash("Evaluation submitted.", "success")
    return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/myevaluations')


# Enter new evaluation submission into database #
@app.route(ENTRY_POINT + '/evaluationsubmitted', methods=['POST'])
@login_required
def evaluationsubmitted():

    resource_id = request.form['hiddenfield']

    conx = mysql.get_db()
    cursor = conx.cursor()

    query1 = "select resource_type, project_id from resource where resource_id=%s"
    cursor.execute(query1,(resource_id))  # get resource type
    tt = cursor.fetchall()
    res_type = tt[0][0]
    project_id = tt[0][1]

    for i in range(16):  # for each question 1-16
        thisanswer = request.form['q' + str((i + 1))]  # get answer for this question 1-16
        thiscomment = request.form['q' + str((i + 1)) + 'yesbutcomment']  # get comment for this question 1-16

        query2 = "select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s)"
        cursor.execute(query2,(i+1,res_type,res_type))  # get q_id of most recent q 1-16
        q_id = cursor.fetchall()[0][0]  # use most recent q_id for this question 1-16

        query3 = "delete from evaluation where q_id=%s and resource_id=%s and user_id=%s"
        cursor.execute(query3,(q_id,resource_id,current_user.user_id)) # clear from evaluation my evaluation for this resource (of most updated q version)
        conx.commit()

        query4 = "insert into evaluation(q_id,answer,user_id,resource_id,project_id) values(%s,%s,%s,%s,%s)"
        cursor.execute(query4,(q_id,thisanswer,current_user.user_id,resource_id,project_id))
        conx.commit()

        if thisanswer == 'yesbut':
            query5 = "update evaluation set comment=%s where q_id=%s and user_id=%s and resource_id=%s"
            cursor.execute(query5,(thiscomment,q_id,current_user.user_id,resource_id))
            conx.commit()

        templist = []
        total = 0
        num = 0

        query6 = "select answer from evaluation where resource_id=%s and q_id=%s"
        cursor.execute(query6,(resource_id,q_id))  # start to update average in average table
        data = cursor.fetchall()
        for row in data:
            templist.append(row[0])
            if row[0] == 'yes':
                total = total + 1
            elif row[0] == 'no':
                total = total - 1

        query7 = "select count(answer) from evaluation where resource_id=%s and q_id=%s"
        cursor.execute(query7,(resource_id,q_id))
        dd = cursor.fetchall()
        count = dd[0][0]

        average = float(total) / count
        query8 = "delete from average where resource_id=%s and q_id=%s"
        cursor.execute(query8,(resource_id,q_id))
        conx.commit()  # clear this entry in average
        query9 = "insert into average(resource_id,q_id,avg,project_id) values(%s,%s,%s,%s)"
        cursor.execute(query9,(resource_id,q_id,average,project_id))
        conx.commit()

    flash("Evaluation submitted.", "success")
    return redirect(ENTRY_POINT + '/project/' + str(project_id) + '/resources')

# Manually refresh averages in database #

# @app.route(ENTRY_POINT + '/refreshavg', methods=['GET'])
# def refreshavg():
#     conx = mysql.get_db()
#     cursor = conx.cursor()
#
#     cursor.execute("select count(distinct(resource_id)) from resource")
#     eqq = cursor.fetchall()
#     tres = eqq[0][0]
#
#     for j in range(1, tres + 1):  # for each resource
#         query1 = "select resource_type from resource where resource_id=%s"
#         cursor.execute(query1,(j))
#         res_type = cursor.fetchall()[0][0]
#
#         for i in range(16):  # for each question
#
#             templist = []
#             total = 0
#             num = 0
#
#             query2 = "select answer from evaluation where resource_id=%s and q_id=(select q_id from question where num=%s and res_type=%s and version=(select max(version) from question where res_type=%s))"
#             cursor.execute(query2,(j,i+1,res_type,res_type))
#             data = cursor.fetchall()
#             for row in data:
#                 templist.append(row[0])  # for each question 1-16
#                 if row[0] == 'yes':
#                     total = total + 1
#                 elif row[0] == 'no':
#                     total = total - 1
#
#             cursor.execute("select count(answer) from evaluation where resource_id=" + str(
#                 j) + " and q_id=(select q_id from question where num=" + str(
#                 (i + 1)) + " and res_type='" + res_type + "' and version=(select max(version) from question))")
#             dd = cursor.fetchall()
#             count = dd[0][0]
#
#             average = float(total) / count
#             cursor.execute("insert into average(avg,q_id,resource_id) values(" + str(
#                 average) + ",(select q_id from question where num=" + str(
#                 (i + 1)) + " and res_type='" + res_type + "' and version=(select max(version) from question))," + str(
#                 j) + ")")
#             conx.commit()
#
#     return "ok"


@app.route(ENTRY_POINT + "/forgotpassword")
def forgotpass():
    return render_template('forgotpass.html')


@app.route(ENTRY_POINT + '/sentpassword', methods=['POST'])
def sentpass():
    username = request.form['username']

    conx_forgotp = mysql.get_db()
    cursor = conx_forgotp.cursor()
    query1 = "select password from user where username=%s"
    cursor.execute(query1,(username))
    data = cursor.fetchone()

    if data is None:
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

        if data is None:
            flash("Wrong password.","danger")
            return redirect(ENTRY_POINT + '/resetpassword')
        else:  # old pass + this username match
            if not (password1 == password2):  # passwords don't match
                flash("Passwords do not match.", "danger")
                return redirect(ENTRY_POINT + '/resetpassword')
            else:  # passwords match
                conx_resetp = mysql.get_db()
                cursor = conx_resetp.cursor()
                query2 = "update user set password=%s where username=%s"
                cursor.execute(query2,(password1,username))
                conx_resetp.commit()
                flash("Password successfully changed.","success")
                return redirect(ENTRY_POINT + '/settings')


@app.route(ENTRY_POINT + '/projects', methods=['GET'])
def projects():
    projectlist = []

    conx = mysql.get_db()
    cursor = conx.cursor()
    cursor.execute("select * from project order by project_id")
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
        flash("In progress.","warning")
        return redirect(ENTRY_POINT + "/startproject")

        conx = mysql.get_db()
        cursor = conx.cursor()

        projectname=request.form['projectname']
        projectdesc=request.form['projectdesc']
        projectimg=request.form['projectimg']

        query1 = "insert into project(project_name,project_description,project_img,user_id) values(%s,%s,%s,%s)"
        cursor.execute(query1,(projectname,projectdesc,projectimg,current_user.user_id))
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
            query3 = "insert into question(num,version,res_type,content,project_id) values(%s,'1','example_type',%s,(select project_id from project where project_name=%s))"
            cursor.execute(query3,(r+1,qucontent,projectname))
            conx.commit()

        flash("Project successfully created.", "success")
        return redirect(ENTRY_POINT + '/projects')


@app.route(ENTRY_POINT + '/redirectedFromExt', methods=['POST','GET'])
def redirectedFromExt():

    # URL reached through POST only through browser extension click #
    if request.method == 'POST':
        theName = request.form['theName'].strip()
        theURL = request.form['theURL']
        theType = request.form['theType']
        theSrc = request.form['theSrc']
        if theSrc == 'LINCS Data Portal':
            dsDescrip1 = request.form['dsDescrip1'].strip()
            dsDescrip2 = request.form['dsDescrip2'].strip()
            theDescrip = dsDescrip1 + " " + dsDescrip2
        else:
            theDescrip = request.form['theDescrip'].strip()

        # Check if this resource exists in database - if not, insert into database #
        conx = mysql.get_db()
        cursor = conx.cursor()
        query1 = "select * from resource where resource_name=%s"
        cursor.execute(query1,(theName))
        td = cursor.fetchall()

        # This resource is not in database yet --> insert #
        if not td:
            query2 = "insert into resource(resource_name,resource_type,url,description,project_id) values(%s,%s,%s,%s,%s)"

            if theSrc == 'LINCS Data Portal' or theSrc == 'LINCS Tools':
                cursor.execute(query2,(theName,theType,theURL,theDescrip,1))
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

        # If logged in, go to evaluation form for this resource #
        if current_user.is_authenticated:
            return extensionEvaluation(theName=theName,theURL=theURL,theType=theType,theDescrip=theDescrip)

        # If not logged in, go to login page with evaluation form URL #
        # with resource information saved in query string (passed through GET) #
        else:
            # redirectFromExt='yes'
            flash("Please log in to view this page.","warning")
            return redirect(login_url(ENTRY_POINT + '/login', next_url=url_for('redirectedFromExt',theName=theName,
            theURL=theURL, theType=theType,theDescrip=theDescrip)))
            # return redirect(url_for('login',redirectFromExt=redirectFromExt,theName=theName,theURL=theURL,theType=theType,theDescrip=theDescrip,
            #                         next=url_for('redirectedFromExt',theName=theName,theURL=theURL, theType=theType,theDescrip=theDescrip)))


    # URL reached through GET if redirected from login or manually entered #
    # If redirected from login, resource should be in database. If manually entered, resource will not be in database #
    # Check if resource in database in extensionEvaluation #
    else:
        # Got here from login or manually entered while logged in #
        if current_user.is_authenticated:
            theName = request.args.get('theName').strip()
            theURL = request.args.get('theURL')
            theType = request.args.get('theType')
            theDescrip = request.args.get('theDescrip').strip()
            return extensionEvaluation(theName=theName,theURL=theURL,theType=theType,theDescrip=theDescrip)
        # Got here by manual entering #
        else:
            return render_template('error.html',errormsg='Invalid URL.')


def extensionEvaluation(theName,theURL,theType,theDescrip):
    conx = mysql.get_db()
    cursor = conx.cursor()

    # Check if resource with these fields exists in database first #
    query1 = "select * from resource where resource_name=%s and url=%s and resource_type=%s and description=%s"
    cursor.execute(query1,(theName,theURL,theType,theDescrip))
    resd = cursor.fetchall()

    # This resource does not exist - wrong URL #
    if not resd:
        return render_template('error.html',errormsg='No such digital object.')

    # Resource does exist --> pull up correct form #
    else:
        setq=[]

        query3 = "select resource_id from resource where resource_name=%s"
        cursor.execute(query3, (theName))
        rtt = cursor.fetchall()
        resource_id = rtt[0][0]

        for i in range(1, 17):
            query4 = "select num,version,content from question where res_type=%s and num=%s and version=(select max(version) from question where res_type=%s) order by num"
            cursor.execute(query4, (theType, i, theType))
            cursor.execute("select num,version,content from question where res_type='" + theType
                           + "' and num=" + str(i) + " and version=(select max(version) from question) order by num")
            qd = cursor.fetchall()
            for row in qd:
                setq.append(row)

        # Decide whether to show modify evaluation or new evaluation #
        query5 = "select * from evaluation where resource_id=%s and user_id=%s"
        cursor.execute(query5, (resource_id, current_user.user_id))
        chr = cursor.fetchall()

        # User has not evaluated this resource yet --> show new evaluation #
        if not chr:
            return render_template('newevaluation.html', resource_name=theName, resource_id=resource_id,
                                   resource_type=theType, url=theURL,
                                   description=theDescrip, setq=setq, redirectedFromExt='yes')

        # User has evaluated resource --> show modify evaluation #
        else:
            setanswers = []
            setcomments = []

            query6 = "select q_id, answer from evaluation where resource_id=%s and user_id=%s order by q_id"
            cursor.execute(query6, (resource_id, current_user.user_id))
            data = cursor.fetchall()
            for row in data:
                setanswers.append(row)

            query7 = "select comment from evaluation where resource_id=%s and user_id=%s order by q_id"
            cursor.execute(query7, (resource_id, current_user.user_id))
            data = cursor.fetchall()
            for row in data:
                setcomments.append(str(row[0]))

            return render_template('modifyevaluation.html',
                                   resource_name=theName, resource_id=resource_id, resource_type=theType, url=theURL,
                                   description=theDescrip, setanswers=setanswers, setcomments=setcomments, setq=setq,redirectedFromExt='yes')


@app.route(ENTRY_POINT + '/testerror')
def testerror():
    return errorpage('its an error')


def errorpage(errormsg):
    return render_template('error.html',errormsg=errormsg)


# Logged in user #
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
    app.run(debug=True, host='0.0.0.0')
