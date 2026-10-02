# Medidor Digital de Mili-ohmios Inalámbrico (IoT)

<p align="center">
  <img src="logo.png" alt="Logo UIS" width="140"/>
</p>

**Proyecto Final – Diseño de Sistemas Electrónicos**  
*Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T)*  
**Universidad Industrial de Santander (UIS)**  
**Grupo:** C1B-A1A  

---

## Autores
* **Gabriel Camilo Quijano Celis** – *Código:* 2192312
* **Carlos Daniel Aguilera Iglesias** – *Código:* 2192318

---

## Descripción del Proyecto

El **Medidor Digital de Mili-ohmios Inalámbrico** es un instrumento de metrología portátil diseñado para medir resistencias de ultra-bajo valor en el rango de **$0.5\,\text{m}\Omega$ a $1000\,\text{m}\Omega$**[cite: 6]. 

Fundamentado en el **método de cuatro hilos (Conexión Kelvin)** y **medición ratiométrica**, elimina por completo los errores introducidos por resistencias parásitas de cables, conectores y derivas térmicas por efecto Seebeck[cite: 6, 8]. Los datos metrológicos se procesan mediante un microcontrolador ESP32-C3 SuperMini y se transmiten vía **Bluetooth Low Energy (BLE 5)** hacia una interfaz web responsiva e interactiva[cite: 6, 11].

---

## Probar la Aplicación Web (Sin Descargas)

Puedes probar e interactuar con la interfaz gráfica del instrumento directamente desde tu navegador sin instalar nada:  
**[Abrir Aplicación en GitHub Pages](https://gabrielqc44.github.io/Proyecto-Final-Medidor-Digital-de-Mili-ohmios-Inal-mbrico/)**

---

## Arquitectura del Hardware

El hardware se divide en cuatro etapas funcionales integradas en una placa de $7 \times 7\,\text{cm}$:

1. **Etapa 1: Gestión de Alimentación y Carga:** Módulo TP4056 con protección BMS para batería Li-Po 1S y regulador Buck-Boost TPS63802 ($3.3\,\text{V}$ estables)[cite: 6, 16].
2. **Etapa 2: Fuente de Corriente Constante y Escalas:** Lazo analógico de precisión (OPA376 + MOSFET IRLZ44N) accionado por un buffer 74LVC1G125 mediante excitación pulsada de $55\,\text{ms}$ ($100\,\text{mA}$, $500\,\text{mA}$ y $1\,\text{A}$)[cite: 6, 8, 16].
3. **Etapa 3: Adquisición Analógica de Alta Precisión:** Convertidor $\Delta-\Sigma$ ADS1220 de 24 bits configurado en modo diferencial ratiométrico[cite: 6, 17, 18].
4. **Etapa 4: Control y Comunicaciones:** Microcontrolador ESP32-C3 SuperMini ejecutando el servidor BLE GATT y algoritmos de *Auto-Zeroing* (compensación ON/OFF)[cite: 6, 11, 18, 19].

---

## Estructura del Repositorio

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| `esquemas/` | Planos esquemáticos del circuito impreso y documentación técnica[cite: 20]. |
| `Aplicacion.apk` | Instalador compilado para dispositivos móviles Android[cite: 22, 24]. |
| `Codigo_ESP.txt` | Código fuente del firmware en C++ para el microcontrolador ESP32-C3[cite: 22, 24]. |
| `Interfazz.html` | Código fuente de la interfaz gráfica web en HTML5, CSS3 y JavaScript[cite: 22, 24]. |
| `index.html` | Despliegue de la interfaz web para el servidor de GitHub Pages[cite: 22, 24]. |
| `logo.png` | Logotipo oficial e identidad visual del proyecto[cite: 13, 24]. |

---

## Características Clave
* **Modo Ratiométrico:** Inmune a fluctuaciones o derivas en la corriente de excitación[cite: 6, 8, 18].
* **Excitación Pulsada ($<10\%$ Ciclo de Trabajo):** Disipa menos de $0.41\,\text{W}$, evitando autocalentamiento en resistencias SMD 2512[cite: 6, 8].
* **Compensación de Offset:** Técnica de dos fases ($V_{\text{ON}} - V_{\text{OFF}}$) que anula tensiones termoeléctricas[cite: 6, 8, 19].
* **Costo-Efectivo:** Construcción total por **$20.40 USD** (~$88\%$ de ahorro frente a equipos comerciales equivalentes)[cite: 21].
