import tkinter as tk
from tkinter import ttk
import keyboard
import pyperclip
import time
import os
import textwrap
import subprocess
import yaml
import json
from tkinter.tix import *
from ttkthemes import ThemedTk
import re
import toml
import xml.etree.ElementTree as ET
import requests
from codecs import encode
# s-3pl.host

class Error:
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
        self.__cargar_toml()
        self.repos_activos = self.get_git_branch()
        self.repo_activo = ""
        self.text_label = None
        self.text_label2 = None
        self.text_label3 = None
        self.text_label4 = None
        self.json_properties = self.cargar_json_datos()
        self.solo_ramas_entornos = ["master", "release", "release_sp", "release_pr", "develop_sp", "develop_pr", "global"]
        self.activo = True
        self.color = {
            "activo": "#00c22d",
            "inactivo": "#c2000d",
            "fondo": "#f0f0f0",
            "negro": "#000000",
            "rojo": "#ff0000",
            "rojo_fondo": "#f59090",
            "verde": "#008000"
        }
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
        self.combo = None
        self.text = None

    def __cargar_toml(self):
        try:
            config = toml.load("config.toml")
            self.ruta_base = rf'{config["paths"]["repositorios"]}'
            self.ruta_properties = rf'{config["config_files"]["apis_properties"]}'
            self.datos_encriptar = config["encryption"]
            self.datos_encriptar["headers"]["Content-type"] = self.datos_encriptar["headers"]["Content-type"].replace("TOBEREPLACED", self.datos_encriptar["boundary"])

        except Exception as e:
            raise e

    def cargar_json_datos(self):
        with open(self.ruta_properties, "r") as f:
            return json.load(f)  

    def get_git_branch(self):
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

    def button_click(self, btn, element, btns, repos):
        print("Texto del elemento:", element) 

        self.repo_activo = ""
        self.rama_repo_activo = ""

        for button in btns:
            button.config(relief=tk.RAISED)
            button.config(fg="black")
            button.config(bg=self.color["fondo"])
        btn.config(fg=self.color["rojo"])
        btn.config(bg=self.color["rojo_fondo"])
        btn.config(relief=tk.SUNKEN) 
        self.repo_activo = str(element)
        self.rama_repo_activo = self.repos_activos[self.repo_activo]['branch']
        self.text_label.config(text=f"La API seleccionada es: {str(element)}")
        self.text_label2.config(text=f"La rama seleccionada es: {self.repos_activos[self.repo_activo]['branch']}")
        self.text_label3.config(text="")
        self.text_label4.config(text="",bg=self.color["fondo"])
        print(repos[element])

    def buscar_propertie(self, archivo_yaml, string_copiada_usuario):
        string_copiada_usuario = string_copiada_usuario.replace("{","").replace("}","").replace("$","").replace("secure::","").split(".")
        archivo = archivo_yaml
        if not archivo:
            return Error("Error")
        try:
            for propertie in string_copiada_usuario:
                archivo = archivo[propertie]
            es_secure, valor = self.__es_secure_propertie(archivo)
            if es_secure:
                return valor
            return archivo
        except Exception as e:
            print(e)
            print("La propertie no existe")
        return "La propertie no existe"

    def __peticion_api_secure_properties(self, key, propertie):
        dataList = []
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
            dataList.append(encode('--' + boundary))
            dataList.append(encode(f'Content-Disposition: form-data; name={key};'))
            dataList.append(encode('Content-Type: {}'.format('text/plain')))
            dataList.append(encode(''))
            dataList.append(encode(data))

        dataList.append(encode('--'+boundary+'--'))
        dataList.append(encode(''))
        body = b'\r\n'.join(dataList)
        response = requests.request("POST", url, headers=headers, data=body, files=[])
        return json.loads(response.text)["property"]

    # Sin uso por ahora
    def __desencriptar_usando_java(key, propertie):
        propertie_desencriptada = subprocess.Popen(["java","-cp","secure-properties-tool.jar","com.mulesoft.tools.SecurePropertiesTool","string","decrypt","Blowfish","CBC",key,propertie], stdout=subprocess.PIPE).communicate()[0]
        return propertie_desencriptada.decode('UTF-8').rstrip()

    def __desencriptar_propertie(self, propertie):
        key = self.__buscar_encrypt_key()
        print(key, propertie)
        valor_desencriptada = self.__peticion_api_secure_properties(key, propertie)
        return valor_desencriptada
    
    def __es_secure_propertie(self, propertie):
        es_secure = False
        valor = None
        if type(propertie) == dict:
            return es_secure,valor
        
        if propertie[:2] == "![" and propertie[-1] == "]":
            es_secure = True
            valor = self.__desencriptar_propertie(propertie[2:-1])
        return es_secure,valor

    def __buscar_valores_env(self, cadena):
            patron = r'(?<=name="env" value=")[^"]+(?=")'
            valores = re.findall(patron, cadena)
            return valores

    def __buscar_encrypt_key(self):
        encrypt_key = None
        try:
            tree = ET.parse(rf"{self.ruta_base}\berge-mulesoft-{self.repo_activo}\src\main\mule\global.xml")
            resultados = tree.findall('.//{http://www.mulesoft.org/schema/mule/core}global-property')
            for x in resultados:
                if x.attrib['name'] != "env":
                    encrypt_key = x.attrib['value']
        except Exception as e:
            print(f"{self.repo_activo} No tiene global")

        return encrypt_key
    
    def buscar_entorno_en_global(self):
        entorno = None
        try:
            with open(rf"{self.ruta_base}\berge-mulesoft-{self.repo_activo}\src\main\mule\global.xml", "r") as f:
                entorno = self.__buscar_valores_env(f.read())[0]
                print(entorno)
        except:
            print("No tiene global.xml")

        return entorno

    def __cargar_yaml(ruta):
        with open(ruta, 'r') as archivo:
            try:
                contenido = yaml.safe_load(archivo)
            except:
                contenido = Error(f"Hubo un error al intentar cargar el archivo yaml: {ruta}")
        return contenido

    def __obtener_archivos_config(self):
        rutas_properties = []
        entorno = None
        self.properties_repo_activo = self.json_properties[self.repo_activo]
        # Si el entorno es None entonces quiere decir que la rama no es una de las de entorno
        # Hay que buscar el xml de global la variable env y usar esa
        if self.rama_repo_activo in self.solo_ramas_entornos:
            entorno = self.rama_repo_activo
        else:
            entorno = self.mapeo_entornos_variable_env[self.buscar_entorno_en_global()]
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

    def intentar_abrir_archivo(self, string_copiada_usuario):
        print(self.repo_activo)
        print(self.rama_repo_activo)
        rutas_properties = self.__obtener_archivos_config()
        print(rutas_properties)
        properties = {}
        for ruta in rutas_properties:
            with open(ruta, 'r') as archivo:
                if ruta.split("/")[-1] not in properties:
                    properties[ruta.split("/")[-1]] = []
                try:
                    contenido = yaml.safe_load(archivo)
                    properties[ruta.split("/")[-1]].append(self.buscar_propertie(contenido, string_copiada_usuario))
                except Exception as e:
                    print(f"Hubo un error al intentar cargar el archivo yaml: {ruta}")
                    contenido = None
                    properties[ruta.split("/")[-1]].append(f"Hubo un error al intentar cargar el archivo yaml: {ruta}")
    
        return properties
#s-proxy
    def __formatear_properties(self, properties):
        string_a_mostrar = ""
        for archivo, propertie in properties:
            string_a_mostrar += "\n"
            string_a_mostrar += archivo
            string_a_mostrar += "\n"
            string_a_mostrar += "\n"
            string_a_mostrar += str(propertie) if propertie else ""
            string_a_mostrar += "\n"
            string_a_mostrar += "\n"
            

        return string_a_mostrar
#app.name
    def handle_key_event(self, event):
        if self.activo and event.name == "c" and keyboard.is_pressed("ctrl"):
            print("Se presionó Ctrl+C")
            time.sleep(0.1)
            string_copiada_usuario = pyperclip.paste()
            self.text_label3.config(text=string_copiada_usuario)
            if not self.repo_activo:
                self.text_label2.config(text="Seleccionar una api antes")
            else:
                try:
                    properties = self.intentar_abrir_archivo(string_copiada_usuario)
                except:
                    properties = "No existe"
                print("properties", type(properties), properties)
                string_a_mostrar, posiciones_a_colorear = self.__formatear_existencia_properties(properties)
                # texto_properties_encontradas = "\n".join([prop for prop in properties if prop])
                #color_fondo_texto = self.color["verde"] if texto_properties_encontradas else self.color["rojo"]
                self.text.config(state=tk.NORMAL)
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END,string_a_mostrar)
                for i, posiciones in enumerate(posiciones_a_colorear):
                    fila, largo = posiciones
                    self.text.tag_add(f"x{i}", f"{fila}.0", f"{fila}.{largo}")
                    self.text.tag_config(f"x{i}", foreground="green")
                self.text.config(state=tk.DISABLED)
                # self.text.insert(tk.END,properties if properties else "No existe la propertie" )
                self.text.config(state=tk.DISABLED)
                # self.text_label4.config(text=texto_properties_encontradas if texto_properties_encontradas else "No existe la propertie" ,bg=color_fondo_texto)
                print(self.rama_repo_activo)
                print(properties)

                
#s-proxy.port
    # def create_buttons(self, root, elements):
    #     button_frame = tk.Frame(root)
    #     button_frame.pack()
    #     buttons = []

    #     for i, element in enumerate(elements):
    #         wrapped_text = textwrap.shorten(element, width=21, placeholder="...")
    #         button = tk.Button(button_frame, text=f"{wrapped_text}\n{elements[element]['branch']}", width=21, height=2, font=("Arial", 10))
    #         button.grid(row=i // 3, column=i % 3, padx=5, pady=5)
    #         button.config(command=lambda btn=button, ele=element, btns=buttons, repos=elements: self.button_click(btn, ele, btns, repos))

    #         buttons.append(button)

    def __juntar_yamls(self):
        rutas_properties = self.__obtener_archivos_config()
        yaml_junto = {}
        for ruta in rutas_properties:
            with open(f"{ruta}", "r") as f:
                try:
                    archivo = yaml.safe_load(f)
                except:
                    print(f"Error al abrir: {ruta}")
            for key in archivo:
                if key not in yaml_junto:
                    yaml_junto[key] = archivo[key]
                elif yaml_junto[key] == archivo[key] and type(yaml_junto[key]) == str and type(archivo[key]) == str:
                    pass
                elif yaml_junto[key] != archivo[key] and type(yaml_junto[key]) == str and type(archivo[key]) == str:
                    valor = yaml_junto[key]
                    yaml_junto[key].update(archivo[key])
        
        return yaml_junto
    
    def __formatear_existencia_properties(self, dict_xmls):
        posiciones_a_colorear = []
        string_a_devolver = ""
        fila = 1
        for nombre, properties in dict_xmls.items():
            if properties:
                fila += 1
                string_a_devolver += "\n"
                string_a_devolver += nombre + "\n"
                posiciones_a_colorear.append([fila,len(nombre)])
                for prop in properties:
                    string_a_devolver += f"    {prop}\n"
                    fila += 1
                fila += 1
        return string_a_devolver, posiciones_a_colorear

    def chequear_existencia_properties(self):
        if not self.activo:
            return
        rutas_properties = self.__obtener_archivos_config()
        yaml_junto = self.__juntar_yamls()
        ruta_base_xml = f"{self.ruta_base}/berge-mulesoft-{self.repo_activo}/src/main/mule"
        rutas_xmls = [f"{ruta_base_xml}/{nombre}" for nombre in os.listdir(ruta_base_xml) if nombre[-3:] == "xml"]
        
        print(rutas_properties)
        print(rutas_xmls)

        dict_xmls = {nombre:[] for nombre in os.listdir(ruta_base_xml) if nombre[-3:] == "xml"}

        #Recorro cada XML y les extraigo las properties
        for archivox in rutas_xmls:
            with open(archivox, "r") as f:
                datos = f.read()

            resultados_corchetes = re.findall(r"\$\{[^}]*\}", datos, re.DOTALL)
            resultados_mule_p_simple = re.findall(r"Mule::p\('[^']*'\)", datos, re.DOTALL)
            resultados_mule_p_dobles = re.findall(r"""Mule::p\("[^"]*"\)""", datos, re.DOTALL)
            resultados_p_simple = re.findall(r"p\('[^']*'\)", datos, re.DOTALL)
            resultados_p_doble = re.findall(r"""p\("[^"]*"\)""", datos, re.DOTALL)

            resultados_flows_limpias = [x.replace("${","").replace("}","") for x in resultados_corchetes]
            resultados_mule_p_simples_limpias = [x.replace("Mule::p('","").replace("')","") for x in resultados_mule_p_simple]
            resultados_mule_p_dobles_limpias = [x.replace('Mule::p("',"").replace('")',"") for x in resultados_mule_p_dobles]
            resultados_p_simples_limpias = [x.replace("p('","").replace("')","") for x in resultados_p_simple]
            resultados_p_dobles_limpias = [x.replace('p("',"").replace('")',"") for x in resultados_p_doble]
            #Aca estan todas las properties
            resultados = list(set(resultados_flows_limpias + resultados_mule_p_simples_limpias + resultados_mule_p_dobles_limpias + resultados_p_simples_limpias + resultados_p_dobles_limpias))
            resultados = map(lambda x: x.replace("secure::",""), resultados)
            # Recorrer estas properties y fijarme si estan en el yaml de "yaml_junto"
            # Si estan no hago nada
            # Si no estan las agrego a dict_xmls
            for propertie_ in resultados:
                propertie_ = propertie_.split(".")
                archivo = yaml_junto
                try:
                    for propertie in propertie_:
                        archivo = archivo[propertie]
                except:
                    archivo_solo_nombre = archivox.split("/")[-1]
                    dict_xmls[archivo_solo_nombre].append('.'.join(propertie_))

        string_a_mostrar, posiciones_a_colorear = self.__formatear_existencia_properties(dict_xmls)

        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END,string_a_mostrar)
        for i, posiciones in enumerate(posiciones_a_colorear):
            fila, largo = posiciones
            self.text.tag_add(f"x{i}", f"{fila}.0", f"{fila}.{largo}")
            self.text.tag_config(f"x{i}", foreground="red")
        self.text.config(state=tk.DISABLED)

    def click_cabecera(self, boton, accion):
        if accion == "Activar":
            self.activo = not self.activo
            texto_boton = "Activo" if self.activo else "Inactivo"
            boton[0].config(text=texto_boton)
            for btn in boton:
                btn.config(bg=self.color[texto_boton.lower()])

        elif accion == "ComprobarProperties":
            if not self.activo:
                return
            self.chequear_existencia_properties()

    def crear_botones_cabecera(self, root):
        button_frame = tk.Frame(root)
        button_frame.pack()
        buttons = []

        elements = ["Hola","mundo"]

        button1 = tk.Button(button_frame, text=f"Activo", width=11, height=2, font=("Arial", 16))
        button2 = tk.Button(button_frame, text=f"Comprobar\nProperties", width=11, height=2, font=("Arial", 16))
        button3 = tk.Button(button_frame, text=f"3", width=11, height=2, font=("Arial", 16))
        button4 = tk.Button(button_frame, text=f"4", width=11, height=2, font=("Arial", 16))
        button1.grid(row=0, column=1, padx=5, pady=5)
        button2.grid(row=0, column=2, padx=5, pady=5)
        button3.grid(row=0, column=3, padx=5, pady=5)
        button4.grid(row=0, column=4, padx=5, pady=5)
        button1.config(command=lambda btn=[button1, button2, button3, button4]: self.click_cabecera(btn,"Activar"))
        button2.config(command=lambda btn=button2: self.click_cabecera(btn,"ComprobarProperties"))
        button3.config(command=lambda btn=button3: self.click_cabecera(btn,None))
        button4.config(command=lambda btn=button4: self.click_cabecera(btn,None))
        button1.config(bg="#00c22d")
        # for i, element in enumerate(elements):
        #     wrapped_text = textwrap.shorten(element, width=21, placeholder="...")
        #     button = tk.Button(button_frame, text=f"{wrapped_text}", width=11, height=4, font=("Arial", 16))
        #     button.grid(row=i // 7, column=i % 7, padx=5, pady=5)
        #     button.config(command=lambda btn=button, ele=element, btns=buttons, repos=elements: self.button_click(btn, ele, btns, repos))

        #     buttons.append(button)

    def cambio_seleccion_api(self, event):
        element = self.combo.get()
        self.repo_activo = str(element)
        self.rama_repo_activo = self.repos_activos[self.repo_activo]['branch']
        self.text_label.config(text=f"La API seleccionada es: {str(element)}")
        self.text_label2.config(text=f"La rama seleccionada es: {self.repos_activos[self.repo_activo]['branch']}")
        self.text_label3.config(text="")
        self.text_label4.config(text="",bg=self.color["fondo"])
        # print(self.combo.get())

    def recuperar_texto_caja_texto(self):
        contenido = self.text.get("1.0",'end-1c')
        print(contenido)
        pyperclip.copy(contenido)

    def main(self):
        elements = self.repos_activos

        root = ThemedTk(theme="arc")
        root.resizable(width=False, height=False)
        root.title("Ventana con Texto y Botones")

        # tip= Balloon(root)

        # T = tk.Text(root, height = 5, width = 52)
        # T.insert(tk.END,"prueba")
        # T.config(state=tk.DISABLED)
        # T.pack()

        self.crear_botones_cabecera(root)

        text_frame = tk.Frame(root, height=130)
        text_frame.pack_propagate(0)
        text_frame.pack(expand = False, fill = tk.BOTH)

        self.text_label = tk.Label(text_frame, text="Texto en la parte superior", font=("Arial", 18))
        self.text_label2 = tk.Label(text_frame, text="Texto en la parte superior", font=("Arial", 18))
        self.text_label3 = tk.Label(text_frame, text="", font=("Arial", 18))
        self.text_label4 = tk.Label(text_frame, text="Texto en la parte superior", font=("Arial", 18))
        self.text_label.pack()
        self.text_label2.pack()
        self.text_label3.pack()
        self.text_label4.pack()

        self.combo = ttk.Combobox(state="readonly", values=list(elements.keys()),font="Verdana 16 bold")
        self.combo.bind("<<ComboboxSelected>>", self.cambio_seleccion_api)
        self.combo.set("Selecciona una api")
        self.combo.pack() 
        self.boton_copiar = tk.Button(root, text=f"Copy", width=5, height=2, font=("Arial", 11))
        self.scroll = tk.Scrollbar(root, orient='vertical')
        self.text = tk.Text(root, width=70, height=10, yscrollcommand=self.scroll.set)
        self.text.config(font=('Helvatical bold',20))
        self.text.tag_configure("even", background="#e0e0e0")
        self.text.insert(tk.END,"prueba")
        self.text.config(state=tk.DISABLED)
        self.boton_copiar.pack(anchor="ne")
        self.boton_copiar.config(command=self.recuperar_texto_caja_texto)
        self.text.pack(side=tk.LEFT, pady=(0, 10))
        self.scroll.pack(side=tk.LEFT, fill='y')
        self.scroll.config(command=self.text.yview)
        
        keyboard.on_press(self.handle_key_event)

        root.mainloop()


if __name__ == "__main__":
    clase = Properties()
    clase.main()

# a = subprocess.Popen(["java","-cp","C:/Users/Pedro/Desktop/Pedro/secure-properties-tool.jar","com.mulesoft.tools.SecurePropertiesTool","string","decrypt","Blowfish","CBC","b3rg3Mul3s@ft!","S/iUEdGiT8h1t1ayQhZvkA=="], stdout=subprocess.PIPE).communicate()[0]
# print(a.decode('UTF-8').rstrip())