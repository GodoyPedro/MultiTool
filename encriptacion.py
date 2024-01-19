import subprocess
import json
from tkinter.tix import *
import xml.etree.ElementTree as ET
import requests
from codecs import encode

#Cuando se instancie la clase encriptacion, hay que llamar al metodo que abre el .toml

class Encriptacion:

    def __init__(self, datos_encriptar: str) -> None:
        """
        Recibe los datos cargados del archivo .toml

        Args:
            datos_encriptar (str): Diccionario con los datos cargados del .toml
        """
        self.datos_encriptar = datos_encriptar

    def __peticion_api_secure_properties(self, key:str, propertie:str) -> str: #✅
        """
        Utilizando una llave y un valor a desencriptar, realiza una peticion
        hacia una url que va a devolver el valor desencriptado.
        Todos los valores para realizar la llamada salvo la llave y el valor a desencriptar
        se toman del archivo config.toml.

        Args:
            key (str): Llave que fue utilizada para encriptar la propiedad
            propertie (str): Cadena de texto a desencriptar

        Returns:
            str: Cadena de texto desencriptada
        """
        lista_body_request = []
        json_data = {'operation': 'decrypt',
            'algorithm': 'Blowfish',
            'mode': 'CBC',
            'key': key,
            'value': propertie,
            'method': 'string'}
        boundary = self.datos_encriptar["boundary"]
        url = self.datos_encriptar["url"]
        headers = self.datos_encriptar["headers"]
        for key, data in json_data.items():
            lista_body_request.append(encode('--' + boundary))
            lista_body_request.append(encode(f'Content-Disposition: form-data; name={key};'))
            lista_body_request.append(encode('Content-Type: {}'.format('text/plain')))
            lista_body_request.append(encode(''))
            lista_body_request.append(encode(data))

        lista_body_request.append(encode('--'+boundary+'--'))
        lista_body_request.append(encode(''))
        body = b'\r\n'.join(lista_body_request)
        response = requests.request("POST", url, headers=headers, data=body, files=[])
        return json.loads(response.text)["property"]

    def __desencriptar_usando_java(self, key:str, propertie:str) -> str:
        """
        Utilizando una llave y un valor a desencriptar, se ejecuta un comando de cmd utilizando 
        el archivo "secure-properties-tool.jar" que devuelve el valor desencriptado.
        Este metodo requiere que el equipo posea Java instalado.

        Args:
            key (str): Llave que fue utilizada para encriptar la propiedad.
            propertie (str): Cadena de texto a desencriptar.

        Returns:
            str: Cadena de texto desencriptada.
        """
        propertie_desencriptada = subprocess.Popen(["java","-cp","secure-properties-tool.jar","com.mulesoft.tools.SecurePropertiesTool","string","decrypt","Blowfish","CBC",key,propertie], stdout=subprocess.PIPE).communicate()[0]
        return propertie_desencriptada.decode('UTF-8').rstrip()
    
    def __buscar_encrypt_key(self, ruta_base:str, repo_activo:str) -> str: #✅
        """
        Toma el archivo global.xml del repositorio activo y busca la variable "encryptKey".

        Args:
            ruta_base (str): Ruta de la carpeta donde estan todos los repositorios
            repo_activo (str): Nombre del repositorio activo

        Returns:
            str: Llave para desencriptar propiedades.
        """
        encrypt_key = None
        try:
            tree = ET.parse(rf"{ruta_base}\berge-mulesoft-{repo_activo}\src\main\mule\global.xml")
            resultados = tree.findall('.//{http://www.mulesoft.org/schema/mule/core}global-property')
            for x in resultados:
                if x.attrib['name'] != "env":
                    encrypt_key = x.attrib['value']
        except Exception as e:
            print(f"{repo_activo} No tiene global")

        return encrypt_key

    def __desencriptar_propertie(self, propertie: str, ruta_base:str, repo_activo:str) -> str: #✅
        """
        Metodo publico para desencriptar una propiedad.
        La llava utilizada para desencriptar la misma, sera obtenida del archivo 
        global.xml correspondiente al respositorio activo.

        Args:
            propertie (str): Cadena de texto a desencriptar.

        Returns:
            str: Cadena de texto desencriptada.
        """
        key = self.__buscar_encrypt_key(ruta_base, repo_activo)
        print(key, propertie)
        valor_desencriptada = self.__peticion_api_secure_properties(key, propertie)
        return valor_desencriptada

    def es_secure_propertie(self, propertie:str, ruta_base:str, repo_activo:str) -> tuple: #✅
        """
        Comprueba si el valor de una propiedad esta encriptado.
        Si asi lo fuere, intenta desencriptarla y devuelve su valor.

        Args:
            propertie (str): Valor de la propiedad a comprobar.

        Returns:
            tuple: Devuelve un booleano que determina si la propiedad estaba o no encriptada
            y el valor de la misma en caso de que lo anterior sea verdadero.
        """
        es_secure = False
        valor = None
        if type(propertie) == dict:
            return es_secure,valor
        
        if propertie[:2] == "![" and propertie[-1] == "]":
            es_secure = True
            valor = self.__desencriptar_propertie(propertie[2:-1], ruta_base, repo_activo)
        return es_secure,valor