from pydantic import BaseModel
from datetime import date

#modelo de productos
class producto(BaseModel):
    id_producto:None
    nombre_producto:str
    descripcion:str
    precio:float
    cantidad_disponible:int

#modelo de venta
class venta(BaseModel):
    id_venta:None
    fecha_venta:date
    id_producto:int
    cantidad_vendida:int
    precio_pieza:float
    total:float




