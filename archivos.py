import yaml
import json
from tkinter.tix import *
import re
import toml
from codecs import encode

class Archivos:
    def cargar_toml(self) -> dict[str:str|dict]:
        """
        Carga el archivo .toml y devuelve un dict con los datos

        Raises:
            e: Error

        Returns:
            dict[str:str|dict]: Un diccionario con los datos que fueron cargados del archivo .toml
        """
        try:
            config = toml.load("config.toml")
            datos_encriptar = config["encryption"]
            datos_encriptar["headers"]["Content-type"] = datos_encriptar["headers"]["Content-type"].replace("TOBEREPLACED", datos_encriptar["boundary"])
            datos = {
                "ruta_base": rf'{config["paths"]["repositorios"]}',
                "ruta_properties": rf'{config["config_files"]["apis_properties"]}',
                "datos_encriptar": datos_encriptar
            }
            return datos
        except Exception as e:
            raise e

    def cargar_json(self, ruta) -> dict:
        """
        Abre un archivo JSON

        Returns:
            dict: JSON
        """
        with open(ruta, "r") as f:
            return json.load(f)  

    def cargar_yaml(self, ruta: str) -> dict:
        """        
        Abre un archivo yaml y devuelve su contenido o un error

        Args:
            ruta (str): Ruta del archivo .yaml a abrir

        Returns:
            dict | Error: Devuelve el diccionario correspondiente al archivo .yaml
            o un error.
        """
        with open(ruta, 'r') as archivo:  
            return yaml.safe_load(archivo)


    def __buscar_valores_env(self, cadena: str) -> list[str]:
        """
        Devuelve el valor de la variable "env" encontrada en el archivo global.xml

        Args:
            cadena (str): archivo global.xml en formato texto

        Returns:
            list[str]: Valor de la variable "env"
        """
        patron = r'(?<=name="env" value=")[^"]+(?=")'
        valores = re.findall(patron, cadena)
        return valores

    def buscar_entorno_en_global(self, ruta_base:str, repo_activo:str) -> str:
        """
        Abre el archivo global.xml del repositorio activo y busca el valor
        de la variable "env"

        Args:
            ruta_base (str): Ruta donde se encuentran los repositorios
            repo_activo (str): Nombre del repositorio activo

        Returns:
            str: Valor de la variable "env"
        """
        entorno = None
        try:
            with open(rf"{ruta_base}\berge-mulesoft-{repo_activo}\src\main\mule\global.xml", "r") as f:
                entorno = self.__buscar_valores_env(f.read())[0]
                print(entorno)
        except:
            print("No tiene global.xml")

        return entorno

    def juntar_yamls(self, rutas_properties: list[str]) -> dict: #rutas_properties = __obtener_rutas_archivos_config_a_revisar
        """
        Averigua rutas de archivos .yaml, los abre y los junta en 1 solo diccionario.

        Args:
            rutas_properties (list[str]): Listado de archivos .yaml donde buscar la propiedad.

        Returns:
            dict: Los archivos .yaml correspondientes a las rutas pasadas por parametros todos juntos
            en un solo diccionario
        """
        yaml_junto = {}
        for ruta in rutas_properties:
            try:
                archivo = self.cargar_yaml(ruta)
                for key in archivo:
                    if key not in yaml_junto:
                        yaml_junto[key] = archivo[key]
                    elif yaml_junto[key] == archivo[key] and type(yaml_junto[key]) == str and type(archivo[key]) == str:
                        pass
                    elif yaml_junto[key] != archivo[key] and type(yaml_junto[key]) == str and type(archivo[key]) == str:
                        valor = yaml_junto[key]
                        yaml_junto[key].update(archivo[key])
            except (yaml.YAMLError, FileNotFoundError) as e:
                print(e)
        
        return yaml_junto
    