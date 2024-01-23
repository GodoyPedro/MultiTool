import tkinter as tk
from tkinter import ttk
import keyboard
import pyperclip
import time
import os
import subprocess
import yaml
from tkinter.tix import *
from ttkthemes import ThemedTk
import re
from codecs import encode

from archivos import *
from encriptacion import *
from interfaz import *

class Error(Exception):
    def __init__(self, descripcion) -> None:
        self.descripcion = descripcion

    def __repr__(self) -> str:
        return self.descripcion

class Properties:
    def __init__(self) -> None:
        self.dir_base = os.getcwd()
        self.ruta_base = None
        self.ruta_properties = None
        self.datos_encriptar = None
        self.instancia_archivos = Archivos()
        self.asignar_valor_desde_toml()
        self.instancia_encriptacion = Encriptacion(self.datos_encriptar)
        self.repos_activos = self.get_git_branch()
        self.instancia_interfaz = Interfaz(self.repos_activos)
        self.asignar_funciones()
        self.repo_activo = ""
        self.json_properties = self.instancia_archivos.cargar_json(self.ruta_properties)
        self.activo = True
        self.solo_ramas_entornos = ["master", "release", "release_sp", "release_pr", "develop_sp", "develop_pr", "global"]
        
        self.mapeo_entornos_variable_env = {
            "pro":"master",
            "prod": "master",
            "pre":"release",
            "preprod":"release",
            "qa":"release_sp",
            "qaproj":"release_pr",
            "latam":"release_pr",
            "dev":"develop_sp",
            "devproj":"develop_pr",
            "local":"local"
        }
        

    def cambiar_repo_y_rama_activa(self, event) -> None:
        """
        Actualiza el repo activo y la rama que posee ese repo, como tambien las labels 
        que muestran estos valores en la ventana
        """
        api = self.instancia_interfaz.combo.get() 
        self.repo_activo = api
        self.rama_repo_activo = self.repos_activos[self.repo_activo]['branch']
        self.instancia_interfaz.cambiar_valores_labels_info_labels(self.repo_activo, self.rama_repo_activo)

    def asignar_valor_desde_toml(self) -> None:
        """
        Abre el archivo toml y almacena los valores en variables
        """
        valores = self.instancia_archivos.cargar_toml()
        self.ruta_base = valores["ruta_base"]
        self.ruta_properties = valores["ruta_properties"]
        self.datos_encriptar = valores["datos_encriptar"]
    
    def click_cabecera(self, boton, accion) -> None:
        """
        Cada vez que se presiona un boton, se ejecuta esta funcion.
        Recibe el objeto boton y la accion asociada a ese boton en forma de cadena de texto.
        Dependiendo de la accion seleccionada, se ejecutara el codigo correspondiente.

        Args:
            boton (tk.Button): Objeto del boton presionado.
            accion (str): Cadena de texto con la accion correspondiente al boton.
        """
        if accion == "Activar":
            self.activo = not self.activo
            self.instancia_interfaz.cambiar_color_boton(boton, self.activo)
            
        elif accion == "ComprobarProperties":
            if not self.activo:
                return
            self.chequear_existencia_properties()

    def get_git_branch(self) -> dict[str, str]:
        """
        Busca todos los repositorios activos que existan dentro de la ruta base
        especificada en el archivo .toml.
        Para cada uno de ellos, averigua la rama que se encuentra seleccionada.

        Returns:
            dict[str, str]: Un diccionario donde la clave es el nombre del repositorio y el valor,
            la rama seleccionada.
        """
        repos = os.listdir(self.ruta_base)
        repos_activos = {}
        for repo in repos:
            if ".git" in os.listdir(f"{self.ruta_base}/{repo}"):
                repos_activos[repo] = {
                    "branch": ""
                }

        for repo in repos_activos:
            os.chdir(f"{self.ruta_base}/{repo}")
            branchInbyteOutput = subprocess.Popen(["git","branch","--show-current"], stdout=subprocess.PIPE).communicate()[0]
            repos_activos[repo]["branch"] = branchInbyteOutput.decode('UTF-8').rstrip()

        os.chdir(self.dir_base)

        return {k.split("berge-mulesoft-")[1]:v for k,v in repos_activos.items()}

    def buscar_propertie(self, archivo_yaml:str, string_copiada_usuario:str) -> str:
        """
        Toma un archivo yaml en forma de dict y lo que haya copiado el usuario al apretar CTRL+c
        Limpia la cadena de texto e intenta encontrar la propiedad en el archivo yaml.
        Si la propiedad que se encontro es una secure propertie, se va a intentar desencriptarla.
        
        Args:
            archivo_yaml (str): Archivo yaml en forma de dict.
            string_copiada_usuario (str): Lo que haya en el portapapeles del usuario.

        Returns:
            str: El valor de la propiedad encontrada o "La propertie no existe"
        """
        string_copiada_usuario = string_copiada_usuario.replace("{","").replace("}","").replace("$","").replace("secure::","").replace("Mule::p","").replace("p::","").replace("(","").replace(")","").replace('"',"").replace("'","").split(".")
        archivo = archivo_yaml
        if not archivo:
            raise Error("No existe el archivo")
        try:
            for propertie in string_copiada_usuario:
                archivo = archivo[propertie]
            es_secure, valor = self.instancia_encriptacion.es_secure_propertie(archivo, self.ruta_base, self.repo_activo)
            if es_secure:
                return valor
            return archivo
        except KeyError as e:
            print(e)
            print("La propertie no existe")
        return "La propertie no existe"

    def __obtener_rutas_archivos_config_a_revisar(self) -> list[str]:
        """
        Para buscar si existe una propiedad en el repositorio, necesito encontrarla en los 
        archivos .yaml, este metodo devuelve la ruta de los archivos .yaml 
        donde se va a buscar la propiedad.

        Returns:
            list[str]: Rutas de los archivos .yaml
        """
        rutas_properties = []
        entorno = None
        self.properties_repo_activo = self.json_properties[self.repo_activo]
        # Si el entorno es None entonces quiere decir que la rama no es una de las de entorno
        # Hay que buscar el xml de global la variable env y usar esa
        if self.rama_repo_activo in self.solo_ramas_entornos:
            entorno = self.rama_repo_activo
        else:
            entorno = self.mapeo_entornos_variable_env[self.instancia_archivos.buscar_entorno_en_global()]
        lista_rutas_a_revisar = []
        claves_a_revisar = [entorno,"global","siempre"]
        for clave in claves_a_revisar:
            if clave and self.properties_repo_activo.get(clave):
                 lista_rutas_a_revisar.extend(self.properties_repo_activo[clave])

        print(lista_rutas_a_revisar)
        if lista_rutas_a_revisar:
            try:
                for archivo_prop in lista_rutas_a_revisar:
                    rutas_properties.append(f"{self.ruta_base}/berge-mulesoft-{self.repo_activo}/{archivo_prop}")
            except:
                print(f"No se pudo abrir el archivo: {archivo_prop}")
        
        return rutas_properties

    def handle_key_event(self, evento:keyboard._Event) -> None:
        """
        Cada vez que se aprete algo en el teclado se llama a esta funcion.
        Si se presiono la combinacion CTRL+c entonces se iniciara el proceso que buscara en 
        los archivos yaml correspondientes la supuesta propiedad que fue copiada.
        Ademas formatea la respuesta de las propiedades de forma legible
        para su posterior escritura en la interfaz.

        Args:
            evento (keyboard._Event): _description_
        """
        if self.activo and evento.name == "c" and keyboard.is_pressed("ctrl"):
            print("Se presionó Ctrl+C")
            time.sleep(0.1)
            string_copiada_usuario = pyperclip.paste()
            self.instancia_interfaz.text_label3.config(text=string_copiada_usuario)
            if not self.repo_activo:
                self.instancia_interfaz.text_label2.config(text="Seleccionar una api antes")
            else:
                try:
                    properties = self.buscar_propertie_en_archivos(string_copiada_usuario)
                except:
                    properties = "No existe"
                print("properties", type(properties), properties)
                self.instancia_interfaz.formatear_properties_escribir_texto(properties, "green")
                print(self.rama_repo_activo)
                print(properties)

    def buscar_properties_regex(self, archivo:str) -> list[str]:
        resultados_corchetes = re.findall(r"\$\{[^}]*\}", archivo, re.DOTALL)
        resultados_mule_p_simple = re.findall(r"Mule::p\('[^']*'\)", archivo, re.DOTALL)
        resultados_mule_p_dobles = re.findall(r"""Mule::p\("[^"]*"\)""", archivo, re.DOTALL)
        resultados_p_simple = re.findall(r"p\('[^']*'\)", archivo, re.DOTALL)
        resultados_p_doble = re.findall(r"""p\("[^"]*"\)""", archivo, re.DOTALL)

        resultados_flows_limpias = [x.replace("${","").replace("}","") for x in resultados_corchetes]
        resultados_mule_p_simples_limpias = [x.replace("Mule::p('","").replace("')","") for x in resultados_mule_p_simple]
        resultados_mule_p_dobles_limpias = [x.replace('Mule::p("',"").replace('")',"") for x in resultados_mule_p_dobles]
        resultados_p_simples_limpias = [x.replace("p('","").replace("')","") for x in resultados_p_simple]
        resultados_p_dobles_limpias = [x.replace('p("',"").replace('")',"") for x in resultados_p_doble]
        #Aca estan todas las properties
        resultados = list(set(resultados_flows_limpias + resultados_mule_p_simples_limpias + resultados_mule_p_dobles_limpias + resultados_p_simples_limpias + resultados_p_dobles_limpias))
        resultados = map(lambda x: x.replace("secure::",""), resultados)

        return resultados

    def chequear_existencia_properties(self) -> None:
        """
        Este metodo agrega la funcionalidad de buscar si las propiedades definidas en el codigo,
        estan presentes en los archivos de configuracion correspondientes.
        Para realizar este proceso se averiguan todos los archivos yaml en los que hay que buscar una propiedad
        (archivo correspondiente al entorno y global.yaml mas alguno extra particular de cada api)
        Luego se juntan todos los archivos yaml en 1 solo para facilitar la busqueda.
        Usando expresiones regex se buscan properties en todos los archivos .xml.
        Todas las propiedades encontradas se intentan encontrar en los archivos .yaml de configuracion.
        Si alguna no se logra encontrar, se guarda en una estructura interna a la funcion para luego 
        mostrarla en la interfaz.
        """
        if not self.activo:
            return
        rutas_properties = self.__obtener_rutas_archivos_config_a_revisar()
        yaml_junto = self.instancia_archivos.juntar_yamls(rutas_properties)
        ruta_base_xml = f"{self.ruta_base}/berge-mulesoft-{self.repo_activo}/src/main/mule"
        rutas_xmls = [f"{ruta_base_xml}/{nombre}" for nombre in os.listdir(ruta_base_xml) if nombre[-3:] == "xml"]
        
        print(rutas_properties)
        print(rutas_xmls)

        dict_xmls = {nombre:[] for nombre in os.listdir(ruta_base_xml) if nombre[-3:] == "xml"}

        #Recorro cada XML y les extraigo las properties
        for archivo_xml in rutas_xmls:
            datos = self.instancia_archivos.cargar_archivo(archivo_xml)
            resultados = self.buscar_properties_regex(datos)
            # Recorrer estas properties y fijarme si estan en el yaml de "yaml_junto"
            # Si estan no hago nada
            # Si no estan las agrego a dict_xmls
            for propertie_ in resultados:
                propertie_ = propertie_.split(".")
                archivo = yaml_junto
                try:
                    for propertie in propertie_:
                        archivo = archivo[propertie]
                except KeyError:
                    archivo_solo_nombre = archivo_xml.split("/")[-1]
                    dict_xmls[archivo_solo_nombre].append('.'.join(propertie_))

        self.instancia_interfaz.formatear_properties_escribir_texto(dict_xmls, "red")

    def buscar_propertie_en_archivos(self, string_copiada_usuario: str, rutas_properties: list[str]) -> dict[str:list[str]]: #rutas_properties = __obtener_rutas_archivos_config_a_revisar
        """
        Obtiene las rutas de los archivos a revisar, abre cada uno y busca la propiedad
        que copio el usuario

        Args:
            string_copiada_usuario (str): Lo que haya en el portapapeles del usuario.
            rutas_properties (list[str]): Listado de archivos .yaml donde buscar la propiedad.

        Returns:
            dict[str:list[str]]: Un diccionario cuya clave es el nombre del archivo y como valor
            una lista donde se guardaran las propiedades encontradas
        """
        print(rutas_properties)
        properties = {}

        for ruta in rutas_properties:
            if ruta.split("/")[-1] not in properties:
                properties[ruta.split("/")[-1]] = []
            try:
                contenido = self.instancia_archivos.cargar_yaml(ruta)
                properties[ruta.split("/")[-1]].append(self.buscar_propertie(contenido, string_copiada_usuario))
            except (yaml.YAMLError, FileNotFoundError) as e:
                contenido = None
                properties[ruta.split("/")[-1]].append(f"Hubo un error al intentar cargar el archivo yaml: {ruta}")

        return properties


    def asignar_funciones(self):
        self.instancia_interfaz.combo.bind("<<ComboboxSelected>>", self.cambiar_repo_y_rama_activa)
        self.instancia_interfaz.boton_copiar.config(command=self.instancia_interfaz.recuperar_texto_caja_texto)
        self.instancia_interfaz.button1.config(command=lambda btn=[self.instancia_interfaz.button1, self.instancia_interfaz.button2, self.instancia_interfaz.button3, self.instancia_interfaz.button4]: self.click_cabecera(btn,"Activar"))
        self.instancia_interfaz.button2.config(command=lambda btn=self.instancia_interfaz.button2: self.click_cabecera(btn,"ComprobarProperties"))
        self.instancia_interfaz.button3.config(command=lambda btn=self.instancia_interfaz.button3: self.click_cabecera(btn,None))
        self.instancia_interfaz.button4.config(command=lambda btn=self.instancia_interfaz.button4: self.click_cabecera(btn,None))

    def main(self):

        keyboard.on_press(self.handle_key_event)
        self.instancia_interfaz.root.mainloop()

        #root.mainloop()

propiedades = Properties()
propiedades.main()