import time
import flask
from flask import Flask
import mysql.connector

app = flask.Flask(__name__)
app.config["DEBUG"] = True

HOST = "192.168.240.20"
USER = "glpi_service_ro"
PWD = "superpass"
DATABASE = "dbglpi"
TABLE_USERS = "glpi_users"

mydb = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PWD,
    database= DATABASE
    )

def get_id(phone):

    s = "|"
    extract = "title{0}firstname{0}lastname{0}displayname{0}society{0}phone{0}email{0}id\n".format(s)
    
    print(phone)

    mycursor = mydb.cursor()
    mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM glpi_users where phone LIKE '%{}';".format(phone))
    myresult = mycursor.fetchall()
    
    if len(myresult) == 0 :
        mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM {0} where mobile LIKE '%{1}';".format(TABLE_USERS,phone))
        myresult = mycursor.fetchall()

        if len(myresult) == 0 :
            mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM glpi_users where phone2 LIKE '%{}';".format(phone))
            myresult = mycursor.fetchall()
        
    
    # print("SELECT RES : ",myresult)
    try:

        if myresult[0][3]:
            tel = myresult[0][3]
            tel = tel[-9:]
            # print("TEL:", tel)
        elif myresult[0][4] != '':
            tel = myresult[0][4]
            tel = tel[-9:]
            # print("TEL:", tel)
        elif myresult[0][5] != '':
            tel = myresult[0][5]
            tel = tel[-9:]
            # print("TEL:", tel)
        else:
            print("Téléphone non renseigné")
    

        extract += "mr{0}{1}{0}{2}{0}{3}{0}SOCIETY{0}0033{4}{0}EMAIL@mail.fr{0}{5}\n".format(s,myresult[0][0],myresult[0][1],myresult[0][2],tel,str(myresult[0][6]))
    except IndexError as err:
        print("Numéro inconnu et l'erreur:\n ",err)

    return extract      
    
def get_name(search):
   
    s = "|"
    extract = "title{0}firstname{0}lastname{0}displayname{0}society{0}phone{0}email{0}id\n".format(s)

    # print(search)

    mycursor = mydb.cursor()
    mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM glpi_users where firstname LIKE '%{}';".format(search))
    myresult = mycursor.fetchall()
    
    if len(myresult) == 0 :
        mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM glpi_users where realname LIKE '%{}';".format(search))
        myresult = mycursor.fetchall()

        if len(myresult) == 0 :
            mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM glpi_users where name LIKE '%{}';".format(search))
            myresult = mycursor.fetchall()

    try:

        if myresult[0][3]:
            tel = myresult[0][3]
            tel = tel[-9:]
        elif myresult[0][4] != '':
            tel = myresult[0][4]
            tel = tel[-9:]
        elif myresult[0][5] != '':
            tel = myresult[0][5]
            tel = tel[-9:]
        else:
            print("Téléphone non renseigné")
        extract += "mr{0}{1}{0}{2}{0}{3}{0}SOCIETY{0}0033{4}{0}EMAIL@mail.fr{0}{5}\n".format(s,myresult[0][0],myresult[0][1],myresult[0][2],tel,str(myresult[0][6]))
        print(extract)
    
    except IndexError as err:
        return ("Personne Inconnue: \n error : ",err )
    
    return extract

##################################################################################################


@app.route('/api/ws-phonebook/all', methods=['GET'])
def api_glpi_all():
    return "all"
   

@app.route('/api/ws-phonebook', methods=['GET'])
def api_glpi_annuaire():
    
    time_start = time.time()
    
    if 'phone' in flask.request.args and flask.request.args['phone'] != "unknown" :
        phone = str(flask.request.args['phone'])
        # print("REQUESTED PHONE",phone)
        phone = phone[-9:] # On garde les 9 derniers digits
        # print("SEARCHED PHONE : ", phone)

        extract = get_id(phone)
        time_end = time.time()
        # print("temps before return : ", time_end - time_start)
        return extract

    elif 'search' in flask.request.args:
        search = str(flask.request.args['search'])
        return get_name(search)
    else:
        print("Error_Field : ", flask.request.args['phone'])
        return flask.request.args['phone']

app.run(host="0.0.0.0")