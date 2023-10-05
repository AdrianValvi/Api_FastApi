import mysql.connector


#modelo de configuracion
#usuario base de datos,contrasena, host o puerto, nombre de la base de datos, y realizar exepciones
configuracion = {

    'user': 'root',
    'password': '123456',
    'host': 'localhost',  
    'database': 'puntodeventa',
    'raise_on_warnings': True 

}

#conexion a la base de datos con los datos de configuracion
conector = mysql.connector.connect(**configuracion)

#cursor para realizar peticiones
cursor = conector.cursor()




