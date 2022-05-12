import flask
from flask import Flask
import mysql.connector

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# #VERSION : 5.5.53-0+deb8u1 
HOST = "192.168.240.20"
USER = "glpi_service_ro"
PWD = "superpass"
DATABASE = "dbglpi"
TABLE_USERS = "glpi_users"

def get_id(phone,prefix,mydb):

    s = "|"
    extract = "title{0}firstname{0}lastname{0}displayname{0}society{0}phone{0}email{0}id\n".format(s)
    
    mycursor = mydb.cursor()
    #SELECT firstname, realname, glpi_users.name, phone, phone2, mobile, glpi_users.entities_id, glpi_entities.name FROM glpi_users LEFT JOIN glpi_entities ON glpi_users.entities_id = glpi_entities.id WHERE phone LIKE '%{0}' OR mobile LIKE '%{0}' OR phone2 LIKE '%{0}';"
    mycursor.execute("SELECT firstname, realname, glpi_users.name, phone, phone2, mobile, glpi_users.entities_id, glpi_entities.name FROM glpi_users LEFT JOIN glpi_entities ON glpi_users.entities_id = glpi_entities.id WHERE REPLACE(REPLACE(REPLACE(phone, ' ', ''), '.', ''), '-', '') LIKE '%{0}' OR REPLACE(REPLACE(REPLACE(mobile, ' ', ''), '.', ''), '-', '') LIKE '%{0}' OR REPLACE(REPLACE(REPLACE(mobile, ' ', ''), '.', ''), '-', '') LIKE '%{0}';".format(phone))    
    myresult = mycursor.fetchall()

    try:
        extract += "mr{0}{1}{0}{2}{0}{3}{0}{6}{0}{7}{4}{0}default@mail.fr{0}{5}\n".format(s,myresult[0][0],myresult[0][1],myresult[0][2],phone,str(myresult[0][6]),myresult[0][7],prefix)
    except :
        return "Numéro inconnue"

    mycursor.close()
    return extract      
    
def get_name(search,mydb):
   
    s = "|"
    extract = "title{0}firstname{0}lastname{0}displayname{0}society{0}phone{0}email{0}id\n".format(s)

    mycursor = mydb.cursor()
    mycursor.execute("SELECT firstname,realname,glpi_users.name,phone, phone2, mobile, glpi_users.entities_id, glpi_entities.name FROM glpi_users LEFT JOIN glpi_entities ON glpi_users.entities_id = glpi_entities.id WHERE firstname LIKE '{0}%' OR realname LIKE '{0}%' OR glpi_users.name LIKE '{0}%';".format(search))
    myresult = mycursor.fetchall()
    
    try:
        if len(myresult) == 1:
            iteration = [0]
        else:
            iteration = range(len(myresult))
        for i in iteration:
            if myresult[i][3]:
                tel = myresult[i][3]
                tel = tel[-9:]
            elif myresult[i][4] != '':
                tel = myresult[i][4]
                tel = tel[-9:]
            elif myresult[i][5] != '':
                tel = myresult[i][5]
                tel = tel[-9:]
            else:
                print("Téléphone non renseigné")

            extract += "mr{0}{1}{0}{2}{0}{3}{0}{6}{0}0033{4}{0}default@mail.fr{0}{5}\n".format(s,myresult[i][0],myresult[i][1],myresult[i][2],tel,str(myresult[i][6]),myresult[i][7])
    
    except :
        return "Personne inconnue"

    mycursor.close()
    return extract

# ROUTE
@app.route('/api/ws-phonebook', methods=['GET'])
def request_glpi():
    try :
        mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PWD,
        database= DATABASE
        )

        if 'phone' in flask.request.args and flask.request.args['phone'] != "unknown" :
            phone = str(flask.request.args['phone'])
            prefix = phone[:-9]
            phone = phone[-9:] # On garde les 9 derniers digits
            extract = get_id(phone,prefix,mydb)
            mydb.close()
            return extract

        elif 'search' in flask.request.args:
            search = str(flask.request.args['search'])
            extract = get_name(search,mydb)
            mydb.close()
            return extract
        else:
            mydb.close()
            return "pas d'arguments passés"

    except :
        print("Echec de la connexion à la base de données.")

app.run(host="0.0.0.0")