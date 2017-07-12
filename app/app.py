from flask import Flask, request, redirect, render_template, flash, jsonify
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin, confirm_login, \
    fresh_login_required
from flask_cors import CORS
from flaskext.mysql import MySQL

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

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):  # given user id, returns user object
    conx = mysql.get_db()
    cursor = conx.cursor()
    cursor.execute("select username from user where user_id='" + str(user_id) + "'")
    username = cursor.fetchone()[0]

    conxp = mysql.get_db()
    cursorp = conxp.cursor()
    cursorp.execute("select password from user where user_id='" + str(user_id) + "'")
    password = cursorp.fetchone()[0]

    return User(username, user_id, password)


login_manager.login_view = "/fairshake/login"

ENTRY_POINT = app.config['ENTRY_POINT']

@app.route(ENTRY_POINT + "/")
def index():
    return render_template('index.html')


@app.route(ENTRY_POINT + "/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conx = mysql.get_db()
        cursor = conx.cursor()
        cursor.execute(
            "select username,password from user where username='" + username + "' and password='" + password + "'")
        data = cursor.fetchone()

        if data is None:
            flash("Username or password is wrong.","danger")
            return redirect('/fairshake/login')
        else:
            conxlogin = mysql.get_db()
            cursorlogin = conxlogin.cursor()
            cursorlogin.execute("select user_id from user where username='" + username + "'")
            user_id = cursorlogin.fetchone()
            user = load_user(user_id[0])
            login_user(user)
            return redirect('/fairshake/myaccount')

    return render_template('login.html')


@app.route(ENTRY_POINT + "/myaccount", methods=["GET", 'POST'])
@login_required
def myaccount():
    current_userid = current_user.user_id
    return render_template('acchome.html', current_userid=current_userid)


@app.route(ENTRY_POINT + "/logout", methods=["GET"])
@login_required
def logout():
    # Logout the current user
    logout_user()
    return redirect('/fairshake/login')


@app.route(ENTRY_POINT + "/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        conx_register = mysql.get_db()
        cursor = conx_register.cursor()
        cursor.execute("select username from user where username='" + username + "'")
        data = cursor.fetchone()

        if data is None:  # username is new
            if (not (password1 == password2)):  # passwords don't match
                flash("Passwords do not match.", "danger")
                return redirect('/fairshake/register')
            else:
                conx_add = mysql.get_db()
                cursor = conx_add.cursor()
                cursor.execute("insert into user (username,password) values ('" + username + "','" + password1 + "')")
                conx_add.commit()
                flash("Account successfully created.", "success")
                return redirect('/fairshake/login')
        else:  # data returned something , this username already in database
            flash("Account with this username already exists.","danger")
            return redirect('/fairshake/register')

    return render_template('register.html')


@app.route(ENTRY_POINT + '/resources/', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route(ENTRY_POINT + '/resources', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route(ENTRY_POINT + '/resources/page/<int:page>', methods=['GET'])
def resourcelist(page):
    mylist = []
    userres = []
    listeval = []
    per_page = 5
    pagecount = per_page * page
    showlast = 0
    templist = []

    avginfo = []
    qdat = []

    conx_getevalc = mysql.get_db()
    cursor = conx_getevalc.cursor()
    cursor.execute("select count(*) from resource")  # for pagination
    data1 = cursor.fetchall()
    total = data1[0][0]

    conx_getres1 = mysql.get_db()
    cursor = conx_getres1.cursor()
    cursor.execute("select * from resource")  # get resource info to display
    data = cursor.fetchall()
    for row in data:
        mylist.append(row)

    for i in range(total):
        templist = []
        xlist = []

        conx_getnumeval1 = mysql.get_db()
        cursor = conx_getnumeval1.cursor()
        cursor.execute("select count(distinct(user_id)) from evaluation where resource_id=" + str(
            mylist[i][0]))  # get # of evaluations
        eval1 = cursor.fetchall()
        listeval.append(eval1[0][0])

        templist.append(str(mylist[i][0]))
        xlist.append(str(mylist[i][0]))

        for t in range(16):
            cursor.execute("select q_id from question where num=" + str((t + 1)) + " and res_type='" + str(
                mylist[i][3]) + "' and version=(select max(version) from question)")
            q_id = cursor.fetchall()[0][0]

            cursor.execute("select avg from average where resource_id=" + str(mylist[i][0]) + " and q_id=" + str(q_id))
            adata = cursor.fetchall()
            templist.append(adata[0][0])

            cursor.execute("select content from question where q_id=" + str(q_id))
            tst = cursor.fetchall()
            xlist.append(tst[0][0])

        avginfo.append(templist)  # put into avginfo array the average data
        qdat.append(xlist)

    if (current_user.is_anonymous == False):  # this person is logged in (resourceslist is a public page)
        conx_getres = mysql.get_db()
        cursor = conx_getres.cursor()
        cursor.execute(
            "select * from resource where resource_id in (select resource_id from evaluation where user_id=" + current_user.user_id + ")")  # should maybe change this in subquery #check off ones that this user has evaluated
        data = cursor.fetchall()
        for row in data:
            userres.append(row[0])  # list containing resource ids of resources this user evaluated

    if (pagecount > total):
        showlast = total
    else:
        showlast = pagecount

        # avginfo[0] returns first row (first resource's info)
        # avginfo[0][1] returns first resource's q1 avg
    return render_template('resourcelist2.html', \
                           mylist=mylist, listeval=listeval, total=total, pagecount=pagecount, page=page,
                           per_page=per_page, showlast=showlast, userres=userres, avginfo=avginfo, qdat=qdat)


@app.route(ENTRY_POINT + "/myevaluations", defaults={'page': 1}, methods=['GET'])
@app.route(ENTRY_POINT + "/myevaluations/", defaults={'page': 1}, methods=['GET'])
@app.route(ENTRY_POINT + "/myevaluations/page/<int:page>", methods=['GET'])
@login_required
def myevals(page):
    resources = []
    listeval = []
    per_page = 5
    pagecount = per_page * page
    showlast = 0

    avginfo = []  # average insignia
    ans = []  # my answers insignia
    qdat = []

    conx_getres = mysql.get_db()
    cursor = conx_getres.cursor()
    cursor.execute(
        "select count(distinct(resource_id)) from evaluation where user_id=" + current_user.user_id)  # display only those resources this user has evaluated
    data1 = cursor.fetchall()
    totalres = data1[0][0]

    conx_getres1 = mysql.get_db()
    cursor = conx_getres1.cursor()
    cursor.execute(
        "select * from resource where resource_id in (select resource_id from evaluation where user_id=" + current_user.user_id + ")")  # get res info
    data = cursor.fetchall()
    for row in data:
        resources.append(row)

    for i in range(totalres):  # go through all my evaluations
        nlist = []
        templist = []  # average insignia
        xlist = []

        conx_getnumeval1 = mysql.get_db()
        cursor = conx_getnumeval1.cursor()
        cursor.execute("select count(distinct(user_id)) from evaluation where resource_id=" + str(resources[i][0]))
        eval1 = cursor.fetchall()
        listeval.append(eval1[0][0])

        templist.append(str(resources[i][0]))
        xlist.append(str(resources[i][0]))

        for t in range(16):  # about question

            cursor.execute("select q_id from question where num=" + str((t + 1)) + " and res_type='" + str(
                resources[i][3]) + "' and version=(select max(version) from question)")
            q_id = cursor.fetchall()[0][0]
            cursor.execute(
                "select avg from average where resource_id=" + str(resources[i][0]) + " and q_id=" + str(q_id))
            adata = cursor.fetchall()
            templist.append(adata[0][0])

            cursor.execute("select content from question where q_id=" + str(q_id))
            tst = cursor.fetchall()
            xlist.append(tst[0][0])

        avginfo.append(templist)
        qdat.append(xlist)

        nlist.append(resources[i][0])  # first index 0 is resource_id
        cursor.execute("select resource_id,answer from evaluation where resource_id=" + str(
            resources[i][0]) + " and user_id=" + current_user.user_id)  # my insignia answers
        nd = cursor.fetchall()  # iterating through
        for row in nd:
            if row[1] == 'yes':
                nlist.append(1)
            elif row[1] == 'no':
                nlist.append(-1)
            elif row[1] == 'yesbut':
                nlist.append(0)
        ans.append(nlist)

    if (pagecount > totalres):
        showlast = totalres
    else:
        showlast = pagecount

        # return str(ans[0][3])
    return render_template('myevaluations.html', \
                           page=page, resources=resources, per_page=per_page, pagecount=pagecount, showlast=showlast,
                           totalres=totalres, listeval=listeval, avginfo=avginfo, ans=ans, qdat=qdat)

@app.route(ENTRY_POINT + "/modifyevaluation", methods=['POST'])
@login_required
def modifyevaluation():
    setanswers = []
    setcomments = []
    setq = []

    resourceid = request.form['resourceid']

    conx_getres = mysql.get_db()
    cursor = conx_getres.cursor()
    cursor.execute(
        "select q_id,answer from evaluation where resource_id =" + resourceid + " and user_id=" + current_user.user_id)
    data = cursor.fetchall()
    for row in data:
        setanswers.append(row)

    cursor.execute(
        "select comment from evaluation where resource_id =" + resourceid + " and user_id=" + current_user.user_id)
    data = cursor.fetchall()
    for row in data:
        setcomments.append(str(row[0]))

    conx_getresource = mysql.get_db()
    cursor1 = conx_getresource.cursor()
    cursor1.execute("select * from resource where resource_id=" + resourceid)
    row1 = cursor1.fetchone()
    resource_name = row1[1]
    resource_id = row1[0]
    resource_type = row1[3]
    url = row1[2]
    description = row1[4]

    for i in range(1, 17):
        cursor.execute("select num,version,content from question where res_type='" + resource_type + "' and num=" + str(
            i) + " and version=(select max(version) from question)")
        qd = cursor.fetchall()
        for row in qd:
            setq.append(row)


    return render_template('modifyevaluation.html',
                           resource_name=resource_name, resource_id=resource_id, resource_type=resource_type, url=url,
                           description=description, setanswers=setanswers, setcomments=setcomments, setq=setq)


@app.route(ENTRY_POINT + "/newevaluation", methods=['POST'])
@login_required
def newevaluation():
    setanswers = []
    setcomments = []
    setq = []

    resourceid = request.form['resourceid']

    conx_getres = mysql.get_db()
    cursor = conx_getres.cursor()
    cursor.execute(
        "select q_id,answer from evaluation where resource_id =" + resourceid + " and user_id=" + current_user.user_id)
    data = cursor.fetchall()
    for row in data:
        setanswers.append(row)

    cursor.execute(
        "select comment from evaluation where resource_id =" + resourceid + " and user_id=" + current_user.user_id)
    data = cursor.fetchall()
    for row in data:
        setcomments.append(str(row[0]))

    conx_getresource = mysql.get_db()
    cursor1 = conx_getresource.cursor()
    cursor1.execute("select * from resource where resource_id=" + resourceid)
    row1 = cursor1.fetchone()
    resource_name = row1[1]
    resource_id = row1[0]
    resource_type = row1[3]
    url = row1[2]
    description = row1[4]

    for i in range(1, 17):
        cursor.execute("select num,version,content from question where res_type='" + resource_type + "' and num=" + str(
            i) + " and version=(select max(version) from question)")
        qd = cursor.fetchall()
        for row in qd:
            setq.append(row)

    return render_template('newevaluation.html',
                           resource_name=resource_name, resource_id=resource_id, resource_type=resource_type, url=url,
                           description=description, setanswers=setanswers, setcomments=setcomments, setq=setq)


@app.route(ENTRY_POINT + '/modifysubmitted', methods=['POST'])
@login_required
def modifysubmitted():
    answerlist = []
    commentlist = []

    resource_id = request.form['hiddenfield']

    conx = mysql.get_db()
    cursor = conx.cursor()

    cursor.execute("select resource_type from resource where resource_id=" + resource_id)  # get resource type
    tt = cursor.fetchall()
    res_type = tt[0][0]

    for i in range(16):  # for each question 1-16
        thisanswer = request.form['q' + str((i + 1))]  # get answer for this question 1-16
        thiscomment = request.form['q' + str((i + 1)) + 'yesbutcomment']  # get comment for this question 1-16

        cursor.execute("select q_id from question where num=" + str((
                                                                    i + 1)) + " and res_type='" + res_type + "' and version=(select max(version) from question)")  # get q_id of most recent q 1-16
        q_id = cursor.fetchall()[0][0]  # use most recent q_id for this question 1-16

        cursor.execute("delete from evaluation where q_id=" + str(
            q_id) + " and resource_id=" + resource_id + " and user_id=" + current_user.user_id)  # clear from evaluation my evaluation for this resource (of most updated q version)
        conx.commit()

        cursor.execute("insert into evaluation(q_id,answer,user_id,resource_id) values(" + str(
            q_id) + ",'" + thisanswer + "'," + current_user.user_id + "," + resource_id + ")")
        conx.commit()
        if thisanswer == 'yesbut':
            cursor.execute("update evaluation set comment='" + thiscomment +
                           "' where q_id=" + str(
                q_id) + " and user_id=" + current_user.user_id + " and resource_id=" + resource_id)
            conx.commit()

        templist = []
        total = 0;
        num = 0;

        cursor.execute("select answer from evaluation where resource_id=" + resource_id + " and q_id=" + str(
            q_id))  # start to update average in average table
        data = cursor.fetchall()
        for row in data:
            templist.append(row[0])
            if row[0] == 'yes':
                total = total + 1
            elif row[0] == 'no':
                total = total - 1

        cursor.execute(
            "select count(answer) from evaluation where resource_id=" + resource_id + " and q_id=" + str(q_id))
        dd = cursor.fetchall()
        count = dd[0][0]

        average = float(total) / count
        cursor.execute("delete from average where resource_id=" + resource_id + " and q_id=" + str(q_id))
        conx.commit()  # clear this entry in average
        cursor.execute("insert into average values(" + resource_id + "," + str(q_id) + "," + str(average) + ")")
        conx.commit()
    flash("Evaluation submitted.", "success")
    return redirect('/fairshake/myevaluations')

@app.route(ENTRY_POINT + '/evaluationsubmitted', methods=['POST'])
@login_required
def evaluationsubmitted():
    answerlist = []
    commentlist = []

    resource_id = request.form['hiddenfield']

    conx = mysql.get_db()
    cursor = conx.cursor()

    cursor.execute("select resource_type from resource where resource_id=" + resource_id)  # get resource type
    tt = cursor.fetchall()
    res_type = tt[0][0]

    for i in range(16):  # for each question 1-16
        thisanswer = request.form['q' + str((i + 1))]  # get answer for this question 1-16
        thiscomment = request.form['q' + str((i + 1)) + 'yesbutcomment']  # get comment for this question 1-16

        cursor.execute("select q_id from question where num=" + str((
                                                                    i + 1)) + " and res_type='" + res_type + "' and version=(select max(version) from question)")  # get q_id of most recent q 1-16
        q_id = cursor.fetchall()[0][0]  # use most recent q_id for this question 1-16

        cursor.execute("delete from evaluation where q_id=" + str(
            q_id) + " and resource_id=" + resource_id + " and user_id=" + current_user.user_id)  # clear from evaluation my evaluation for this resource (of most updated q version)
        conx.commit()

        cursor.execute("insert into evaluation(q_id,answer,user_id,resource_id) values(" + str(
            q_id) + ",'" + thisanswer + "'," + current_user.user_id + "," + resource_id + ")")
        conx.commit()
        if thisanswer == 'yesbut':
            cursor.execute("update evaluation set comment='" + thiscomment +
                           "' where q_id=" + str(
                q_id) + " and user_id=" + current_user.user_id + " and resource_id=" + resource_id)
            conx.commit()

        templist = []
        total = 0;
        num = 0;

        cursor.execute("select answer from evaluation where resource_id=" + resource_id + " and q_id=" + str(
            q_id))  # start to update average in average table
        data = cursor.fetchall()
        for row in data:
            templist.append(row[0])
            if row[0] == 'yes':
                total = total + 1
            elif row[0] == 'no':
                total = total - 1

        cursor.execute(
            "select count(answer) from evaluation where resource_id=" + resource_id + " and q_id=" + str(q_id))
        dd = cursor.fetchall()
        count = dd[0][0]

        average = float(total) / count
        cursor.execute("delete from average where resource_id=" + resource_id + " and q_id=" + str(q_id))
        conx.commit()  # clear this entry in average
        cursor.execute("insert into average values(" + resource_id + "," + str(q_id) + "," + str(average) + ")")
        conx.commit()

    flash("Evaluation submitted.", "success")
    return redirect('/fairshake/resources')


@app.route(ENTRY_POINT + '/refreshavg', methods=['GET'])
def refreshavg():
    conx = mysql.get_db()
    cursor = conx.cursor()

    cursor.execute("select count(distinct(resource_id)) from resource")
    eqq = cursor.fetchall()
    tres = eqq[0][0]

    for j in range(1, tres + 1):  # for each resource

        cursor.execute("select resource_type from resource where resource_id=" + str(j))
        res_type = cursor.fetchall()[0][0]

        for i in range(16):  # for each question

            templist = []
            total = 0;
            num = 0;

            cursor.execute("select answer from evaluation where resource_id=" + str(
                j) + " and q_id=(select q_id from question where num=" + str(
                (i + 1)) + " and res_type='" + res_type + "' and version=(select max(version) from question))")
            data = cursor.fetchall()
            for row in data:
                templist.append(row[0])  # for each question 1-16
                if row[0] == 'yes':
                    total = total + 1
                elif row[0] == 'no':
                    total = total - 1

            cursor.execute("select count(answer) from evaluation where resource_id=" + str(
                j) + " and q_id=(select q_id from question where num=" + str(
                (i + 1)) + " and res_type='" + res_type + "' and version=(select max(version) from question))")
            dd = cursor.fetchall()
            count = dd[0][0]

            average = float(total) / count
            cursor.execute("insert into average(avg,q_id,resource_id) values(" + str(
                average) + ",(select q_id from question where num=" + str(
                (i + 1)) + " and res_type='" + res_type + "' and version=(select max(version) from question))," + str(
                j) + ")")
            conx.commit()

    return "ok"


@app.route(ENTRY_POINT + "/forgotpassword")
def forgotpass():
    return render_template('forgotpass.html')


@app.route(ENTRY_POINT + '/sentpassword', methods=['POST'])
def sentpass():
    username = request.form['username']

    conx_forgotp = mysql.get_db()
    cursor = conx_forgotp.cursor()
    cursor.execute("select password from user where username='" + username + "'")

    data = cursor.fetchone()

    if data is None:
        return "No account under this username"
    else:
        return "Email placeholder"


@app.route(ENTRY_POINT + "/resetpassword", methods=["GET"])
@login_required
def resetpass():
    return render_template('resetpass.html')


@app.route(ENTRY_POINT + '/passwordreset', methods=['POST', 'GET'])
@login_required
def passreset():
    username = current_user.username
    passwordold = request.form['passwordold']
    password1 = request.form['password1']
    password2 = request.form['password2']

    conx_checkup = mysql.get_db()
    cursor = conx_checkup.cursor()
    cursor.execute("select username from user where username='" + username + "' and password='" + passwordold + "'")
    data = cursor.fetchone()

    if data is None:
        return "Wrong password"
    else:  # old pass + this username match
        if (not (password1 == password2)):  # passwords don't match
            return "Passwords do not match"
        else:  # passwords match, now c
            conx_resetp = mysql.get_db()
            cursor = conx_resetp.cursor()
            cursor.execute("update user set password='" + password1 + "' where username='" + username + "'")
            conx_resetp.commit()
            return "Password reset"


@app.route(ENTRY_POINT + '/doe', methods=['GET'])
def doe():
    return render_template('doehome.html')


@app.route(ENTRY_POINT + '/projects', methods=['GET'])
def projects():
    return render_template('projects.html')


@app.route(ENTRY_POINT + '/account', methods=['GET'])
def myprojects():
    return render_template('doeacchome.html')


class User(UserMixin):
    '''
    This provides default implementations for the methods that Flask-Login
    expects user objects to have.

    if not PY2:  # pragma: no cover
        # Python 3 implicitly set __hash__ to None if we override __eq__
        # We set it back to its default implementation
        __hash__ = object.__hash__'''

    def __init__(self, username, user_id, password):
        self.username = username
        self.user_id = user_id
        self.password = password

    @property
    def is_active(self):  # active: activated account through email etc
        return True

    @property
    def is_authenticated(self):  # authentication = user + password match
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)


if __name__ == "__main__":
    app.run(debug=True)
