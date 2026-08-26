productos = [
    {"nombre": "Laptop", "precio": 1200, "stock": 15},
    {"nombre": "Mouse", "precio": 25, "stock": 5},
    {"nombre": "Teclado", "precio": 75, "stock": 25},
    {"nombre": "Monitor", "precio": 300, "stock": 8}
]

# #esta linea crea una lista vacía para almacenar los productos con bajo stock
# productos_bajo_stock = []
# #esta linea recorre la lista de productos usando un for
# for producto in productos:
#     #esta linea imprime el nombre y precio de cada producto
#     print(f"Producto: {producto['nombre']}, Precio: ${producto['precio']},")
#     #esta linea verifica si el stock del producto es menor a 10
#     if producto['stock'] < 10:
#         #en esta linea, si el stock es menor a 10, se agrega el producto a la lista de productos_bajo_stock
#         productos_bajo_stock.append(producto)

# #aca se hace un salto de linea y se imprime un mensaje indicando que se mostrarán los productos con bajo stock
# print("\nProductos con bajo stock:")

# #en esta linea se imprime la lista de productos con bajo stock
# print(productos_bajo_stock)


#creamos una funcion que reciba una lista de productos 
# def calcular_promedio_precio(lista):
#     #aca se verifica si la lista esta vacia
#     if not lista:
#         #si esta vacia, se retorna 0 para evitar division por cero
#         return 0
#     #aca se usa la funcion sum para calcular el total de los precios de los productos en la lista
#     total_precio = sum(p['precio'] for p in lista)
#     #se retorna el promedio de los precios dividiendo el total de precios entre la cantidad de productos en la lista
#     return total_precio / len(lista)

# #aca llamamos a la funcion calcular_promedio_precio que creamos anteriormente
# #pasando la lista de productos y almacenamos el resultado en la variable precio_promedio
# precio_promedio = calcular_promedio_precio(productos)

# #saltamos una linea e imprimimos el precio promedio de los productos con dos decimales usando f-string
# print(f"\nEl precio promedio de los productos es: ${precio_promedio:.2f}")




#importamos el modulo csv para poder leer archivos CSV
import csv

#creamos una lista vacía para almacenar los productos que se leerán desde el archivo CSV
productos_desde_csv = []

#aca se abre el archivo CSV en modo lectura
with open('./datos.csv', mode='r', encoding='utf-8') as archivo_csv:
     #aca se crea un lector de diccionario para leer el archivo CSV
     lector_diccionario = csv.DictReader(archivo_csv)
     #aca se recorre el lector de diccionario
     for linea in lector_diccionario:
         #aca se crea un diccionario para cada producto con los datos leídos desde el archivo CSV
         producto = {
             "nombre": linea['nombre'],
             "precio": float(linea['precio']),
             "stock": int(linea['stock'])
         }
         #en esta linea se agrega el producto a la lista de productos
         productos_desde_csv.append(producto)

#aca se imprime un mensaje indicando que se mostrarán los productos cargados desde el archivo CSV
print("\nProductos cargados desde el archivo CSV:")

#aca se recorre la lista de productos cargados desde el archivo CSV y se imprime cada producto con su nombre, precio y stock
for producto in productos_desde_csv:
    print(f"Producto {productos_desde_csv.index(producto) + 1}: {producto['nombre']}, Precio: ${producto['precio']}, Stock: {producto['stock']}")

#aca importamos el modulo json para poder trabajar con este formato
import json
#esta linea importa la funcion validar_datos desde el archivo validar_productos que crearemos para la tarea
from validar_productos import validar_datos

#aca verificamos si la lista productos_desde_csv tiene datos adentro
if productos_desde_csv:
    #en esta linea convertimos la lista de diccionarios a una cadena de texto en formato JSON usando json.dumps
    datos_json = json.dumps(productos_desde_csv, indent=4)
    
    #aca abrimos (o creamos) un nuevo archivo llamado salida.json en modo escritura ('w')
    with open('salida.json', 'w') as archivo_salida:
        #en esta linea escribimos la cadena de texto JSON dentro del archivo
        archivo_salida.write(datos_json)
    
    #aca imprimimos un mensaje indicando que el archivo se creó correctamente
    print("\nArchivo 'salida.json' creado con éxito.")
    
    #esta linea imprime un mensaje avisando que se va a ejecutar el validador
    print("\n--- Ejecutando el validador modular ---")
    
    #aca llamamos a la funcion validar_datos pasandole el archivo salida.json y guardamos el resultado en datos_validados
    datos_validados = validar_datos('salida.json')
    
    #esta linea verifica si la validacion fue exitosa (es decir, si datos_validados no esta vacio o nulo)
    if datos_validados:
        #aca imprimimos los datos validados correctamente
        print("Datos validados correctamente:", datos_validados)
