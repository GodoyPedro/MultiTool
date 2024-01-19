import tkinter as tk
import pyperclip
from tkinter.tix import *
from ttkthemes import ThemedTk

class Interfaz:
    
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

    def formatear_existencia_properties(self, dict_xmls:dict[str,list[str]]) -> tuple[str,list[list[int,int]]]:
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

    def crear_botones_cabecera(self, root:ThemedTk) -> None:
        """
        Crea y ubica los botones que se visualizan en la parte superior de la aplicacion.

        Args:
            root (ThemedTk): Ventana principal creada.
        """
        button_frame = tk.Frame(root)
        button_frame.pack()

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

    def cambio_seleccion_api(self) -> None:
        """
        Esta funcion se ejecuta cada vez que se selecciona una nueva opcion
        de la lista desplegable de API's.
        Reemplazara el repositorio activo por el seleccionado
        Reemplazara la rama activa por la rama seleccionada del nuevo repositorio activo
        Reemplaza los valores de las etiquetas en la interfaz que muestran estos datos
        """
        api = self.combo.get()         # Instancia de Propiedades
        repo_activo, rama_repo_activo = self.propiedades.cambiar_repo_y_rama_activa(str(api))
        self.text_label.config(text=f"La API seleccionada es: {repo_activo}")
        self.text_label2.config(text=f"La rama seleccionada es: {rama_repo_activo}")
        self.text_label3.config(text="")
        self.text_label4.config(text="",bg=self.color["fondo"])

    def cambiar_repo_y_rama_activa(self, api:str) -> None:
        """
        Recibe la seleccion de repositorio hecha por el usuario y actualiza
        el repo activo y la rama que posee ese repo

        Args:
            api (str): _description_

        Returns:
            _type_: _description_
        """
        self.repo_activo = api
        self.rama_repo_activo = self.repos_activos[self.repo_activo]['branch']

        return self.repo_activo, self.rama_repo_activo

    def recuperar_texto_caja_texto(self) -> None:
        """
        Copia al portapapeles del usuario, todo el texto que este escrito
        en el recuadro de texto.
        """
        contenido = self.text.get("1.0",'end-1c')
        print(contenido)
        pyperclip.copy(contenido)