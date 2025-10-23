# Proyecto de prueba de ATOM, Agente con query tool e información básica de una empresa.

Este documento describe brevemente los principales aspectos del proyecto **Atom**, incluyendo instrucciones para la instalación, configuración y ejecución del agente y su entorno de pruebas.

---
## Pruebas

En esta sección se hablará de las configuraciones y comandos que se deben correr para probar el proyecto.

### Archivo requirements.txt
Después de tener el entorno del proyecto creado es necesario instalar todas las dependencias del proyecto con el siguiente comando:

```bash
pip install -r requirements.txt
```

### Archivo .env
Se debe de tomar en cuenta que el proyecto ahora mismo está utilizando el API de Gemini para realizar las pruebas de los agentes, un ejemplo de como se vería el archivo .env es este:

```bash
GOOGLE_API_KEY=***********************************************
```
, se puede observar que solo es necesario cambiar el api de Google para realizar las pruebas.

### Carpeta notebooks_prueba
En esta carpeta se pueden observar diferentes notebooks donde se observa archivos de prueba del código realizado en este proyecto, no es necesario correr nada de aquí, pero si se quiere ver parte de la lógica del código y diferentes pruebas, se puede consultar la carpeta.

### Archivo database_settings.py
Es necesario correr este archivo para que el agente pueda realizar llamadas a las bases de datos de prueba. El comnado de ejecución se ve de esta manera:

Command: 

```bash
python database_settings.py
```

Output:

```bash
Database created successfully!

Data in the database:

id | producto    | categoria   | precio | pais      | fecha_venta
------------------------------------------------------------
 1 | iPhone 14   | smartphones | 1300.0 | Argentina | 2024-05-10
 2 | MacBook Air | notebooks   | 1800.0 | Chile     | 2024-05-12
```

### Archivo agent_runtime.py 
Este archivo contiene la lógica principal del agente, el backend se conecta desde aquí para poder realizar utilizar la lógica del agente creado.

### Archivo main.py
En este archivo se encuentra la lógica del backend del proyecto, desde aquí se lanza un endpoint de manera local de donde el frontend se conecta y puede realizar diferentes llamadas al agente. Para correr el backend solo es necesario correr el siguiente comando en la ruta del proyecto:

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```


### Archivo index.html
En este archivo se encuentra un frontend sencillo para realizar las diferentes pruebas de los agentes. Es necesario tener el backend corriendo con el comando anterior para poder realizar las pruebas, se puede acceder al Frontend abriendo el archivo desde cualquier navegador. 

---

## CONSIDERACIONES:
- El agente no tiene memoria de las conversaciones, es decir, que no puede recordar lo que se le dice anteriormente, las preguntas deben de ser puntuales y no se le puede preguntar sobre algo dicho anteriormente. 

- No se colocan restricciones de queries ni por prompt ni por codigo como tal, el agente puede hacer queries dañinos.

## Características principales del computador

Las características del computador utilizado son las siguientes según el comando neofetch:

```bash
nelson@nelsonpc:~$ neofetch
            .-/+oossssoo+/-.               nelson@nelsonpc 
        `:+ssssssssssssssssss+:`           --------------- 
      -+ssssssssssssssssssyyssss+-         OS: Ubuntu 22.04.5 LTS x86_64 
    .ossssssssssssssssssdMMMNysssso.       Host: 82K2 IdeaPad Gaming 3 15ACH6 
   /ssssssssssshdmmNNmmyNMMMMhssssss/      Kernel: 6.8.0-79-generic 
  +ssssssssshmydMMMMMMMNddddyssssssss+     Uptime: 1 hour, 49 mins 
 /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/    Packages: 2782 (dpkg), 6 (flatpak),  
.ssssssssdMMMNhsssssssssshNMMMdssssssss.   Shell: bash 5.1.16 
+sssshhhyNMMNyssssssssssssyNMMMysssssss+   Resolution: 1920x1080, 2560x1440 
ossyNMMMNyMMhsssssssssssssshmmmhssssssso   DE: GNOME 42.9 
ossyNMMMNyMMhsssssssssssssshmmmhssssssso   WM: Mutter 
+sssshhhyNMMNyssssssssssssyNMMMysssssss+   WM Theme: Adwaita 
.ssssssssdMMMNhsssssssssshNMMMdssssssss.   Theme: Yaru-dark [GTK2/3] 
 /sssssssshNMMMyhhyyyyhdNMMMNhssssssss/    Icons: Yaru [GTK2/3] 
  +sssssssssdmydMMMMMMMMddddyssssssss+     Terminal: gnome-terminal 
   /ssssssssssshdmNNNNmyNMMMMhssssss/      CPU: AMD Ryzen 5 5600H with Radeon G 
    .ossssssssssssssssssdMMMNysssso.       GPU: NVIDIA GeForce RTX 3050 Ti Mobi 
      -+sssssssssssssssssyyyssss+-         GPU: AMD ATI 06:00.0 Cezanne 
        `:+ssssssssssssssssss+:`           Memory: 9053MiB / 13824MiB 
            .-/+oossssoo+/-.
                                                                   
                                    
```              
---
### Ejemplos de preguntas y respuestas

Q: cual fue el precio promedio de venta en chile
A: El precio promedio de venta en Chile fue de 1800.

Q: cuales son los productos principales que tiene la empresa y como se llama
A: La empresa TechNova vende productos electrónicos. Sus categorías principales son smartphones, notebooks y accesorios.

Q: Cuales son los productos que tiene la empresa en venta y su categoria según su base de datos
A: La empresa TechNova tiene los siguientes productos en venta, clasificados por categoría: * **Smartphones:** iPhone 14 * **Notebooks:** MacBook Air

Q: Cualees son los precios y las fechas de venta que tienen registrados para el pais de argentina
A: En Argentina, se registró una venta con fecha 2024-05-10 y un precio de 1300.

Q: Cualees son los precios y las fechas de venta que tienen registrados para el pais de uruguay
A: No se encontraron registros de ventas para Uruguay en la base de datos.