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

# HOST = "192.168.18.192"
# USER = "python"
# PWD = "python"
# DATABASE = "glpi"

def get_id(phone,mydb):

    s = "|"
    extract = "title{0}firstname{0}lastname{0}displayname{0}society{0}phone{0}email{0}id\n".format(s)
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT firstname, realname, glpi_users.name, phone, phone2, mobile, glpi_users.entities_id, glpi_entities.name FROM glpi_users LEFT JOIN glpi_entities ON glpi_users.entities_id = glpi_entities.id WHERE phone LIKE '%{0}' OR mobile LIKE '%{0}' OR phone2 LIKE '%{0}';".format(phone))    
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
    
        extract += "mr{0}{1}{0}{2}{0}{3}{0}{6}{0}0033{4}{0}default@mail.fr{0}{5}\n".format(s,myresult[0][0],myresult[0][1],myresult[0][2],tel,str(myresult[0][6]),myresult[0][7])
    
    except IndexError as err:
        print("Numéro inconnu, Erreur:\n ",err)

    mycursor.close()
    return extract      
    
def get_name(search,mydb):
   
    s = "|"
    extract = "title{0}firstname{0}lastname{0}displayname{0}society{0}phone{0}email{0}id\n".format(s)

    mycursor = mydb.cursor()
    mycursor.execute("SELECT firstname,realname,glpi_users.name,phone, phone2, mobile, glpi_users.entities_id, glpi_entities.name FROM glpi_users LEFT JOIN glpi_entities ON glpi_users.entities_id = glpi_entities.id WHERE firstname LIKE '{0}%' OR realname LIKE '{0}%' OR glpi_users.name LIKE '{0}%';".format(search))
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

        extract += "mr{0}{1}{0}{2}{0}{3}{0}{6}{0}0033{4}{0}default@mail.fr{0}{5}\n".format(s,myresult[0][0],myresult[0][1],myresult[0][2],tel,str(myresult[0][6]),myresult[0][7])
    
    except IndexError as err:
        return ("Personne Inconnue: \n error : ",err )
    except :
        print("Erreur Search")

    mycursor.close()
    return extract

# ROUTES

@app.route('/api/ws-phonebook/all', methods=['GET'])
def api_glpi_all():
    return "all"
   

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
            phone = phone[-9:] # On garde les 9 derniers digits
            extract = get_id(phone,mydb)
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
        print("Echec de connexion à la base de données.")

app.run(host="0.0.0.0")