import tkinter as tk
from tkinter import ttk
import pyperclip
from tkinter.tix import *
from ttkthemes import ThemedTk

class Interfaz:
    
    def __init__(self, repos_activos) -> None:
        self.repos_activos = repos_activos
        self.color = ""
        self.combo = ""
        self.combo = None
        self.text = None
        self.text_label = None
        self.text_label2 = None
        self.text_label3 = None
        self.text_label4 = None
        self.button1 = None
        self.button2 = None
        self.button3 = None
        self.button4 = None
        self.color = {
            "activo": "#00c22d",
            "inactivo": "#c2000d",
            "fondo": "#f0f0f0",
            "negro": "#000000",
            "rojo": "#ff0000",
            "rojo_fondo": "#f59090",
            "verde": "#008000"
        }
        self.crear_interfaz()
        
    def crear_interfaz(self):
        self.root = ThemedTk(theme="arc")
        self.root.resizable(width=False, height=False)
        self.root.title("Ventana con Texto y Botones")
        
        button_frame = tk.Frame(self.root)
        button_frame.pack()
        self.button1 = tk.Button(button_frame, text=f"Activo", width=11, height=2, font=("Arial", 16))
        self.button2 = tk.Button(button_frame, text=f"Comprobar\nProperties", width=11, height=2, font=("Arial", 16))
        self.button3 = tk.Button(button_frame, text=f"3", width=11, height=2, font=("Arial", 16))
        self.button4 = tk.Button(button_frame, text=f"4", width=11, height=2, font=("Arial", 16))
        self.button1.grid(row=0, column=1, padx=5, pady=5)
        self.button2.grid(row=0, column=2, padx=5, pady=5)
        self.button3.grid(row=0, column=3, padx=5, pady=5)
        self.button4.grid(row=0, column=4, padx=5, pady=5)
        self.button1.config(bg="#00c22d")
        
        text_frame = tk.Frame(self.root, height=130)
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
        self.combo = ttk.Combobox(state="readonly", values=list(self.repos_activos.keys()),font="Verdana 16 bold")
        self.combo.set("Selecciona una api")
        self.combo.pack() 
        self.boton_copiar = tk.Button(self.root, text=f"Copy", width=5, height=2, font=("Arial", 11))
        self.scroll = tk.Scrollbar(self.root, orient='vertical')
        self.text = tk.Text(self.root, width=70, height=10, yscrollcommand=self.scroll.set)
        self.text.config(font=('Helvatical bold',20))
        self.text.tag_configure("even", background="#e0e0e0")
        self.text.insert(tk.END,"prueba")
        self.text.config(state=tk.DISABLED)
        self.boton_copiar.pack(anchor="ne")
        self.text.pack(side=tk.LEFT, pady=(0, 10))
        self.scroll.pack(side=tk.LEFT, fill='y')
        self.scroll.config(command=self.text.yview)
    
    # Sin uso actualmente
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

    def formatear_properties_escribir_texto(self, dict_xmls:dict[str,list[str]], color:str) -> tuple[str,list[list[int,int]]]:
        string_a_mostrar, posiciones_a_colorear = self.__formatear_existencia_properties(dict_xmls)
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END,string_a_mostrar)
        for i, posiciones in enumerate(posiciones_a_colorear):
            fila, largo = posiciones
            self.text.tag_add(f"x{i}", f"{fila}.0", f"{fila}.{largo}")
            self.text.tag_config(f"x{i}", foreground=color)
        self.text.config(state=tk.DISABLED)

    def __formatear_existencia_properties(self, dict_xmls:dict[str,list[str]]) -> tuple[str,list[list[int,int]]]:
        """
        Devuelve una cadena de texto de una sola linea con espacios y "\n" y una lista de posiciones.
        Estas posiciones hacen referencia a la posicion del nombre del archivo 
        dentro de la cadena de texto de una sola linea
        El proposito es colorear los nombres de los archivos utilizando las posiciones retornadas.

        Args:
            dict_xmls (dict[str,list[str]]): Diccionario donde se especifica el nombre del archivo como clave
        y como valor, una lista de las propiedades correspondientes a dicho archivo.

        Returns:
            tuple[str,list[list[int,int]]]: Una cadena de texto de una sola linea con espacios y "\n" y una lista de posiciones.
        """
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

    def cambiar_color_boton(self, boton:tk.Button, activo:bool) -> None:
        """
        Cambia el color y texto del boton dependiendo si esta o no activo.

        Args:
            boton (tk.Button): Objeto del boton presionado.
            activo (bool): Identifica si el boton tiene o no que estar activo
        """
        texto_boton = "Activo" if activo else "Inactivo"
        boton[0].config(text=texto_boton)
        for btn in boton:
            btn.config(bg=self.color[texto_boton.lower()])


    def cambiar_valores_labels_info_labels(self, repo_activo:str, rama_repo_activo:str) -> None:
        """
        Actualiza el texto de las labels en pantalla

        Args:
            repo_activo (str): Nombre del repositorio activo
            rama_repo_activo (str): Nombre de la rama del repositorio activo
        """
        self.text_label.config(text=f"La API seleccionada es: {repo_activo}")
        self.text_label2.config(text=f"La rama seleccionada es: {rama_repo_activo}")
        self.text_label3.config(text="")
        self.text_label4.config(text="",bg=self.color["fondo"])


    def recuperar_texto_caja_texto(self) -> None:
        """
        Copia al portapapeles del usuario, todo el texto que este escrito
        en el recuadro de texto.
        """
        contenido = self.text.get("1.0",'end-1c')
        print(contenido)
        pyperclip.copy(contenido)