from fastapi import FastAPI
from db.models import models #importar los models
from db import client as db
from datetime import datetime
from fastapi import FastAPI, HTTPException


#objeto de tipo FastAPI
app = FastAPI()

#METODOS POST
#metodo para agregar productos
@app.post("/usuario/{nombre}/{descripcion}/{precio}/{cantidad}")
async def agregar_usuario(nombre:str,descripcion:str,precio:float,cantidad:int):
    return agregar_producto(nombre,descripcion,precio,cantidad)

@app.post("/actualizarInventario/{id}/{cantidad}")
async def actualizar_inventario(id:int,cantidad:int):
    return Actualizar_inventario(id,cantidad)

#METODOS GET
#metodo get para obtener todos los productos de la base de datos
@app.get("/productos")
async def listar_productos():
    productos = obtener_productos()
    return {"productos": productos}

#metodo get para obtener un producto
@app.get("/{id}")
async def buscar_producto(id:int):
    return buscar_producto_por_id(id)

#metodo get para buscar por nombre
@app.get("/nombre/{nombreB}")
async def buscar_producto_por_nombre(nombreB:str):
    return buscar_por_nombre(nombreB)

#buscar el precio de un producto
@app.get("/precio/{id}")
async def buscar_precio(id:int):
    return buscar_precio(id)

#dar el precio total lo recomendable es usar post porque se va a crear un registro en tablas pero como tambien se va a retornar un valor preferi dejarlo en get
@app.get("/precioTotal/{id}/{cantidad}")
async def precio_total(id:int,cantidad:int):
    return vender(id,cantidad)

#obtener los elentos de la tabla ventas
@app.get("/ventas/get")
async def ventas():
    return mostrar_ventas()

#obtenr inventario
@app.get("/inventario/{id}")
async def inventario(id:int):
    return obtener_inventario(id)

#funciones..........................................................................................................
#funcion obtener resultados
def obtener_productos():
    try:
        
        #ejecutar consulta de prueba
        consulta = "SELECT * FROM inventario"
        db.cursor.execute(consulta)

        #obtener todas las filas de la columna
        resultados = db.cursor.fetchall()

        # Crear una lista de diccionarios con los resultados
        productos = [{"id_producto": row[0],
                      "nombre_producto": row[1], 
                      "descripcion": row[2], 
                      "precio": row[3], 
                      "cantidad_disponible": row[4]} 
                      for row in resultados]

        #returnar resultados
        return productos
    
    except Exception as e:
        print(f"Error al obtener productos: {str(e)}")
        return []

#funcion para buscar por id        
def buscar_producto_por_id(id_producto:int):
    try:
        # Ejecutar consulta SQL con una cláusula WHERE para buscar por ID
        consulta = "SELECT * FROM inventario WHERE id_producto = %s"
        db.cursor.execute(consulta, (id_producto,))

        # Obtener el resultado de la consulta
        producto = db.cursor.fetchone()

        if producto:
            # Si se encontró un producto con el ID especificado
            return {
                "id_producto": producto[0],
                "nombre_producto": producto[1],
                "descripcion": producto[2],
                "precio": producto[3],
                "cantidad_disponible": producto[4]
            }
        else:
            # Si no se encontró ningún producto con el ID especificado
            return None
    except Exception as e:
        print(f"Error al buscar producto por ID: {str(e)}")
        return None
    
#buscar por nombre
def buscar_por_nombre(nombre:str):
    try:
        #consulta sql WHERE para buscar por nombre
        consulta = "SELECT * FROM inventario WHERE nombre_producto = %s"
        
        #ejecucion de la consulta con la variable nombre
        db.cursor.execute(consulta, (nombre,))

        #guardar todos los productos
        producto = db.cursor.fetchall()
        
        #variable que contendra los datos en formato json
        productos = []

        #validacion de que se encontraron los productos o producto
        if producto:
            #iteracion para desempaquetar en un json los datos y guardarlos
            for row in producto:
                productos.append({
                "id_producto": row[0],
                "nombre_producto": row[1],
                "descripcion": row[2],
                "precio": row[3],
                "cantidad_disponible": row[4]
               })
            return productos
        else:
            #si no se encontro ningun producto con el nombre
            return {"producto":"producto no encontrado revise que el nombre este bien escrito"}


    except Exception as e:
        print(f"Error al buscar producto por nombre: {str(e)}")
        return {"Error":"no se pudo encontrar el producto"}

#metodo para buscar el precio por id
def buscar_precio(id:int):
    
    try:
        #consulta sql
        consulta = "SELECT precio FROM inventario WHERE id_producto = %s"
        
        #ejecutar la consulta
        db.cursor.execute(consulta,(id,))

        #guardar el resultado
        resultado = db.cursor.fetchone()

        #validacion de obtencion de precio
        if resultado:
            precio = resultado[0]
            return {"precio":precio}
        else:
            return {"Error":"no se encontro el precio"}

        
    except Exception as e:
        print(f"Error al buscar el precio")
        return {"Error":"no se pudo encontrar el precio"}


#metodo para vender un producto y descontarlo de la base de datos
def vender(id:int,cantidad:int):
    #validar si existe el id
    if buscar_producto_por_id(id) != None:
         #obtener el inventario para trabajarlo actualizando la base de datos
        inventario = obtener_inventario(id)
        if inventario>0:
            #obtener fecha actual
            fecha_actual = datetime.now()
            
            #variables
            precio:float
            precio_total:float
            fecha_actual_formateada = fecha_actual.strftime("%Y-%m-%d")

            #consulta sql
            consulta = "SELECT precio FROM inventario WHERE id_producto = %s"
            
            #ejecutar la consulta
            db.cursor.execute(consulta,(id,))

            #guardar el resultado
            resultado = db.cursor.fetchone()

            #validacion de obtencion de precio
            if resultado:
                precio = resultado[0]
                precio_total=precio*cantidad
                
                
                #crear un modelo para agregarlo
                agregar = models.venta(
                    id_venta=None,
                    fecha_venta=fecha_actual_formateada,
                    id_producto=id,
                    cantidad_vendida=cantidad,
                    precio_pieza=precio,
                    total=precio_total
                )
                
            
                #calcular la nueva cantidad en existencia
                valor = inventario-cantidad

                if valor<0:
                    valor=0
                
                #consulta para actualizar la base de datos REVISAR EL MANUAL DE SQL LA PETICION ESTA EQUIVOCADA
                consulta = "UPDATE inventario SET cantidad_disponible = %s WHERE id_producto = %s"
                
                print(valor)
                #ejecucion de consulta sql para cambiar el numero de productos en inventario
                db.cursor.execute(consulta,(valor,id))
                db.conector.commit()
        else:
            consulta = "UPDATE inventario SET cantidad_disponible = %s WHERE id_producto = %s"
             #ejecucion de consulta sql para cambiar el numero de productos en inventario
            db.cursor.execute(consulta,(0,id))
            db.conector.commit()  
            raise HTTPException(status_code=400,detail="Stock insuficiente") 
            return {"Error":"No hay suficiente stock"}

            
        return agregar_venta(agregar)
       
    else:
        return None

#metodo para agregar a venta  
def agregar_venta(agregar:models.venta):
     # consulta para agregarlo a las tablas
        consulta = "INSERT INTO ventas (fecha_venta, id_producto, cantidad_vendida, precio_unitario, total_venta) VALUES (%s, %s, %s, %s, %s)"
        valores = (agregar.fecha_venta, agregar.id_producto, agregar.cantidad_vendida, agregar.precio_pieza, agregar.total)
        try:
            #ejecutar consulta y autorizarla
            db.cursor.execute(consulta, valores)
            db.conector.commit()

            #obtener el ultimo id creado
            id_nuevo = db.cursor.lastrowid

            print("Nueva fila agregada con éxito.")
        except Exception as e:
            print(f"Error al agregar nueva fila: {str(e)}")
            db.conector.rollback()
        return {"total":agregar.total,
                "id venta":id_nuevo}


#metodo para mostrar los elementos de ventas
def mostrar_ventas():
    
    try:
        #consulta sql
        consulta = "SELECT * FROM ventas"
        db.cursor.execute(consulta)

        #guardar los resultados
        datos = db.cursor.fetchall()
        datos_final = []
        for row in datos:
            datos_final.append({
            "id_venta":row[0],
            "fecha_venta":row[1],
            "id_producto":row[2],
            "cantidad_vendida":row[3],
            "precio_unitario":row[4],
            "precio_total":row[5]
        })
        return datos_final
    except Exception as e:
        print(f"erro al mostrar los elementos de la fila:{str(e)}")

#metodo para agragar productos
def agregar_producto(nombre:str,descripcion:str,precio:float,cantidad:int):
    #consulta sql
    consulta = "INSERT INTO inventario (nombre_producto, descripcion, precio, cantidad_disponible) VALUES (%s, %s, %s, %s)"
    valores = (nombre,descripcion,precio,cantidad)

    try:
        #ejacutar consulta
        db.cursor.execute(consulta,valores)
        #autorizar ejecucion
        db.conector.commit()
        id_nuevo = db.cursor.lastrowid
        return {"producto agregado con el id":id_nuevo}
    except Exception as e:
        db.conector.rollback()
        print(f"Error al agregar producto: {str(e)}")


#fincion para buscar el inventario de un producto por id
def obtener_inventario(id:int):

    #consulta sql 
    consulta = "SELECT cantidad_disponible FROM inventario WHERE id_producto = %s"
    
    try:
        db.cursor.execute(consulta,(id,))
        cantidad = db.cursor.fetchone()
        if cantidad:
            return cantidad[0]
        else:
            return None
    except Exception as e:
        print(f"error al buscar el inventario {str(e)}")
        return None
    
#actualizar la cantidad de inventario
def Actualizar_inventario(id:int,cantidad:int):

    #consulta sql
    consulta = "UPDATE inventario SET cantidad_disponible = %s WHERE id_producto = %s"

    try:
    #ejecutar consulta
        if cantidad>=0:
            db.cursor.execute(consulta,(cantidad,id))
            db.conector.commit()
            return{"Cantidad Actualizada":cantidad}
        else:
            db.conector.rollback()
            return {"Error":"Cantidad Invalida"}
    except Exception as e:
        
        raise HTTPException(status_code=400,detail="error al agregar inventario") 

        


#fin de funciones.........................................................................................................






# Cerrar la conexión al finalizar la aplicación
@app.on_event("shutdown")
async def cerrar_app():
    if hasattr(db, 'conector'):#verificar si un objeto tiene un atributo con un nombre específico. Retorna True si el atributo existe en el objeto y False si no existe.
        db.conector.close()
  
