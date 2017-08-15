# Chrome extension API to get this resource's questions for insignia #
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


# Chrome extension API to get this resource's average scores for insignia #
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


# Download Chrome extension page #
@app.route(ENTRY_POINT + '/chromeextension')
def chromeextension():
    return render_template('chromext.html')


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
    # If redirected from login, resource should be in database. If manually entered, resource may not be in database #
    # Check if resource in database in extensionEvaluation #
    else:
        # Got here from login or manually entered while logged in #
        if current_user.is_authenticated:
            theName = request.args.get('theName').strip()
            theURL = request.args.get('theURL')
            theType = request.args.get('theType')
            theDescrip = request.args.get('theDescrip').strip()
            return extensionEvaluation(theName=theName,theURL=theURL,theType=theType,theDescrip=theDescrip)
        # Got here by manual entering because still not logged in #
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

