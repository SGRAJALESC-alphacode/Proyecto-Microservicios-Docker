# Ecosistema de Microservicios Distribuidos con Docker

**Universidad Autónoma de Manizales** **Asignatura:** Sistemas Operativos  
**Docente:** Ernesto Guevara  
**Estudiante:** Sergio Grajales Clavijo, Juan Diego Higinio, Josue Daniel Castaño, Juan Camilo Bueno.

---

## 1. Descripción del Proyecto
Este proyecto implementa una arquitectura híbrida de microservicios distribuidos para la gestión y monitoreo de sensores climáticos IoT. El sistema simula un entorno de producción real dividido en dos nodos:
1.  **Nodo Nube (Servidor Linux):** Aloja la persistencia de datos y la seguridad perimetral.
2.  **Nodo Local (Cliente Windows):** Aloja la lógica de negocio, visualización, simulación de sensores y copias de seguridad.

El objetivo es demostrar el dominio de la orquestación con **Docker Compose**, gestión de redes (Networking), volúmenes para persistencia y concurrencia en aplicaciones web.

---

## 2. Arquitectura del Sistema

La solución se compone de 5 microservicios interconectados:

### A. Entorno en la Nube (Simulado en Linux VM)
* **Base de Datos Maestra (MySQL 8.0):** Almacén principal de las lecturas de los sensores. Configurada con zona horaria `America/Bogota` (GMT-5).
* **Proxy Inverso (Nginx Stream):** Actúa como capa de seguridad. No expone el puerto 3306 de la base de datos directamente; en su lugar, utiliza un túnel TCP en el puerto `33060` para enrutar el tráfico de forma segura mediante resolución de nombres DNS interna.

### B. Entorno Local (Docker Desktop)
* **Frontend (Flask Web App):** Interfaz de usuario que visualiza los datos. Implementa **Concurrencia** para consultar APIs externas sin bloquear el hilo principal.
    * *Recursos Limitados:* Estrictamente configurado a 2 vCPU y 2 GB de RAM.
* **Sensor Simulator (IoT Worker):** Microservicio autónomo que obtiene datos climáticos reales (Open-Meteo API) de diferentes ciudades de Colombia y los inyecta en la base de datos remota cada 15 segundos.
* **Backup Worker:** Servicio de mantenimiento que realiza copias de seguridad periódicas (JSON) de la base de datos remota al almacenamiento local.

---

## 3. Justificación Técnica (Concurrencia)

Para el requisito de la API Externa en el Frontend, se seleccionó el modelo de **Concurrencia basado en Hilos (`ThreadPoolExecutor`)**.

**Justificación:**
La tarea de consultar una API externa (Open-Meteo) es una operación **I/O-Bound** (limitada por la entrada/salida de red), no por la CPU. Utilizar `Multiprocessing` habría sido ineficiente por el overhead de crear nuevos procesos. Los hilos permiten liberar el intérprete de Python mientras se espera la respuesta HTTP, garantizando que la interfaz web no se congele durante la consulta.

---

## 4. Prerrequisitos de Despliegue

* **En la Nube (VM):** Docker Engine y Docker Compose V2.
* **En Local:** Docker Desktop.
* Puertos libres: `5000` (Web), `33060` (Proxy Nginx).

---

## 5. Instrucciones de Despliegue

### Paso 1: Configuración del Servidor (Nube)
1.  Acceda a la carpeta `nube/` del repositorio.
2.  Copie los archivos al servidor Linux.
3.  Despliegue los servicios de persistencia:
    ```bash
    docker-compose up -d
    ```
4.  El servidor quedará escuchando en el puerto `33060`.

### Paso 2: Configuración del Cliente (Local)
1.  Acceda a la carpeta `local/`.
2.  Edite el archivo `docker-compose.yml` y reemplace la variable `CLOUD_DB_HOST` con la IP de su servidor Linux.
3.  Despliegue los microservicios:
    ```bash
    docker-compose up -d --build
    ```
4.  Acceda al panel de control en: `http://localhost:5000`

---

## 6. Evidencias de Funcionamiento

### Arquitectura Tolerante a Fallos
Se realizaron pruebas de caos eliminando los contenedores de la nube. El sistema demostró resiliencia: el Frontend continuó operando (mostrando datos de la API externa) y manejó la desconexión de la BD de forma controlada.

### Persistencia de Datos
Se verificó que tras destruir los contenedores de la nube, los datos históricos se mantuvieron intactos gracias a la correcta configuración de los `Docker Volumes`.

---

## 7. Tecnologías Utilizadas
* **Docker & Compose:** Orquestación.
* **Python (Flask):** Backend y Frontend.
* **Nginx:** Proxy Inverso TCP.
* **MySQL:** Persistencia.
* **Git:** Control de versiones.
