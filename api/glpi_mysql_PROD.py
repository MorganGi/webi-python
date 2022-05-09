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


def get_id(phone,mydb):

    s = "|"
    extract = "title{0}firstname{0}lastname{0}displayname{0}society{0}phone{0}email{0}id\n".format(s)
    
    # print(phone)

    mycursor = mydb.cursor()
    mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM glpi_users where phone LIKE '%{}';".format(phone))
    myresult = mycursor.fetchall()
    
    if len(myresult) == 0 :
        mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM {0} where mobile LIKE '%{1}';".format(TABLE_USERS,phone))
        myresult = mycursor.fetchall()

        if len(myresult) == 0 :
            mycursor.execute("SELECT  firstname,realname,name,phone, phone2, mobile, entities_id FROM glpi_users where phone2 LIKE '%{}';".format(phone))
            myresult = mycursor.fetchall()
    #########

    try: 

        mycursor.execute("SELECT name FROM glpi_entities where id = '{}';".format(myresult[0][6]))
        getSociety = mycursor.fetchall()
        print(getSociety)
        society = getSociety[0][0]
        print(society)

    except:
        print("Requête society Erreur")
        society = "societyNotFound"


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
    

        extract += "mr{0}{1}{0}{2}{0}{3}{0}{6}{0}0033{4}{0}default@mail.fr{0}{5}\n".format(s,myresult[0][0],myresult[0][1],myresult[0][2],tel,str(myresult[0][6]),society)
    except IndexError as err:
        print("Numéro inconnu et l'erreur:\n ",err)
    mycursor.close()
    mydb.close()
    return extract      
    
def get_name(search,mydb):
   
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
        mycursor.execute("SELECT name FROM glpi_entities where id = '{}';".format(myresult[0][6]))
        getSociety = mycursor.fetchall()
        print(getSociety)
        society = getSociety[0][0]
        print(society)

    except:
        print("Requête society Erreur")
        society = "societyNotFound"
    
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

        extract += "mr{0}{1}{0}{2}{0}{3}{0}{6}{0}0033{4}{0}default@mail.fr{0}{5}\n".format(s,myresult[0][0],myresult[0][1],myresult[0][2],tel,str(myresult[0][6]),society)
        # print(extract)
    
    except IndexError as err:
        return ("Personne Inconnue: \n error : ",err )
    except :
        print("Erreur Search")
    mycursor.close()
    mydb.close()
    return extract

##################################################################################################


@app.route('/api/ws-phonebook/all', methods=['GET'])
def api_glpi_all():
    return "all"
   

@app.route('/api/ws-phonebook', methods=['GET'])
def api_glpi_annuaire():
    try :
        mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PWD,
        database= DATABASE
        )
    except :
        print("Echec de connexion à la base de données.")

    # time_start = time.time()
    
    if 'phone' in flask.request.args and flask.request.args['phone'] != "unknown" :
        phone = str(flask.request.args['phone'])
        # print("REQUESTED PHONE",phone)
        phone = phone[-9:] # On garde les 9 derniers digits
        # print("SEARCHED PHONE : ", phone)

        extract = get_id(phone,mydb)
        # time_end = time.time()
        # print("Time before return : ", time_end - time_start)
        return extract

    elif 'search' in flask.request.args:
        search = str(flask.request.args['search'])
        return get_name(search,mydb)
    else:
        print("Error_Field : ", flask.request.args['phone'])
        return flask.request.args['phone']

app.run(host="0.0.0.0")