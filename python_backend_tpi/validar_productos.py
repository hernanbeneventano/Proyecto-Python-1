#aca importamos el modulo json necesario para leer y analizar el archivo
import json

#en esta linea definimos la funcion validar_datos que recibe el nombre del archivo
def validar_datos(nombre_archivo):
    #aca iniciamos un bloque try para manejar posibles errores controladamente
    try:
        #esta linea abre el archivo en modo lectura ('r')
        with open(nombre_archivo, 'r') as archivo_json:
            #aca leemos y analizamos el archivo JSON convirtiendolo a una lista de diccionarios en Python
            datos = json.load(archivo_json)
            
            #en esta linea verificamos si los datos analizados NO son una lista
            if not isinstance(datos, list):
                #aca generamos un error ValueError si el archivo no contiene una lista
                raise ValueError("El archivo no contiene una lista de datos.")
            
            #esta linea recorre cada producto (item) dentro de la lista de datos usando un for
            for item in datos:
                #aca verificamos si el precio del producto NO es un numero (ni entero ni decimal)
                if not isinstance(item.get('precio'), (int, float)):
                    #en esta linea generamos un TypeError indicando que el precio no es numerico
                    raise TypeError(f"El precio del producto '{item.get('nombre')}' no es numérico.")
            
            #aca imprimimos un mensaje de exito si todo salio bien y no hubo errores
            print("Validación exitosa.")
            #esta linea retorna la lista de datos si es totalmente valida
            return datos
            
    #aca capturamos el error si el archivo que le pasamos no existe
    except FileNotFoundError:
        #en esta linea imprimimos un mensaje de error indicando que no se encontro
        print(f"Error: El archivo '{nombre_archivo}' no se encontró.")
        #aca retornamos None porque hubo un error
        return None
    #esta linea captura el error especifico si el formato del archivo JSON esta roto o no es valido
    except json.JSONDecodeError:
        #aca imprimimos el mensaje de error de formato
        print("Error: El archivo no tiene un formato JSON válido.")
        #en esta linea retornamos None
        return None
    #aca capturamos los errores de valor o tipo (ValueError, TypeError) que generamos nosotros arriba
    except (ValueError, TypeError) as e:
        #esta linea imprime el mensaje de error especifico que capturamos en la variable 'e'
        print(f"Error en la validación de datos: {e}")
        #aca retornamos None indicando que fallo la validacion de los datos
        return None