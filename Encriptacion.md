Encriptacion
Interfaz
Archivos
Properties

Ideal:
Properties
    Encriptacion
    Interfaz
    Archivos

Problema
En interfaz tengo que bindear botones y combobox a funciones
Si creo esas funciones en Interfaz, la interfaz tendria mas responsabilidades
de las que deberia tener
Si lo hago:
    Esas funciones necesitan datos que solo estan en Properties

Si no lo hago:
    Necesito una referencia de Properties dentro de Interfaz, siendo que 
    quiero que sea al reves.

Posibilidad
Interfaz
    Encriptacion
    Properties
    Archivos

Las funciones que bindeo las podria llamar desde Properties
Dentro de esa funciones se podrian acceder a los datos porque
ya estoy en la clase,
Ademas podria actualizar la interfaz ya que estoy dentro de ella

TODOs:
Crear metodo __init__ en Interfaz donde se van a 
instanciar las demas clases y revisar los metodos
__init__ de esas clases.

Mejoras:
get_git_branch() 
se llama solo cuando se inicia el programa y recorre todos los repos obteniendo sus ramas, eso significa que si cambio de rama mientras se ejecuta el programa, los datos quedaran desactualizados.

Interfaz va a ser la clase principal
Propiedades, Encriptacion y Archivos seran instancias
dentro de esta.

Todos los regex deberian estar en un archivo de config

buscar_propertie los replace sobre la string deberian ser un metodo aparte