Si estás utilizando un sensor de **CO2 CCS811**, el proceso de integración es ligeramente diferente ya que este sensor utiliza el bus **I2C** y ofrece mediciones de CO2 y **TVOC** (compuestos orgánicos volátiles). Vamos a modificar los pasos para leer este sensor y usarlo en tu proyecto con la **Rock Pi 4SE**.

### Pasos para Integrar el Sensor CCS811

### 1. Conectar el Sensor **CCS811** a la **Rock Pi 4SE**

El **CCS811** utiliza el bus **I2C**, por lo que deberás conectarlo a los pines I2C de la **Rock Pi 4SE**.

#### Conexión del **CCS811**:
- **VCC** -> Pin 1 (3.3V)
- **GND** -> Pin 6 (GND)
- **SCL** -> Pin 5 (I2C1 SCL)
- **SDA** -> Pin 3 (I2C1 SDA)

### 2. Instalar Bibliotecas para el **CCS811**

En este caso, usaremos la biblioteca `adafruit-ccs811` para interactuar con el sensor desde Python. Asegúrate de tener **pip** instalado y luego instala las bibliotecas necesarias:

1. Instala la biblioteca de Adafruit para el **CCS811**:
   ```bash
   sudo pip3 install adafruit-circuitpython-ccs811
   ```

2. Asegúrate de que el bus **I2C** está habilitado (si ya lo habilitaste en los pasos anteriores, no necesitas repetir este paso):
   ```bash
   sudo i2cdetect -y 1
   ```

   Esto debería mostrar la dirección del **CCS811** (normalmente `0x5A` o `0x5B`).

### 3. Código para Leer el Sensor **CCS811**

Vamos a crear un nuevo archivo Python que lea los datos del sensor **CCS811**. Este sensor mide **CO2 equivalente (eCO2)** y **TVOC** (Total Volatile Organic Compounds), así que tendrás estos dos valores disponibles.

#### Crear un archivo Python para el **CCS811**:
```bash
nano ccs811_reader.py
```

#### Código ejemplo para el **CCS811**:
```python
import time
import board
import busio
import adafruit_ccs811

# Inicializa el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializa el sensor CCS811
ccs811 = adafruit_ccs811.CCS811(i2c)

# Espera hasta que el sensor esté listo para proporcionar lecturas válidas
while not ccs811.data_ready:
    time.sleep(1)

# Leer los valores del CCS811
co2 = ccs811.eco2
tvoc = ccs811.tvoc

print(f"CO2: {co2} ppm")
print(f"TVOC: {tvoc} ppb")
```

Este script inicializa el sensor **CCS811** y luego lee los valores de **CO2** (eCO2) y **TVOC**. Al ejecutarlo, deberías obtener las lecturas de los valores de **CO2** y **TVOC**.

Guarda el archivo y ejecútalo para probar que funciona:
```bash
python3 ccs811_reader.py
```

### 4. Integrar el Sensor **CCS811** en el Servidor Flask

Ahora, vamos a actualizar el servidor Flask para leer el **CCS811** en lugar del **MH-Z19** y mostrar los datos en la página web.

#### Modificar el archivo `server.py` para usar el **CCS811**:

Edita el archivo `server.py` para incluir la lectura del **CCS811**.

```python
from flask import Flask, jsonify, render_template
import smbus2
import bme280
import board
import busio
import adafruit_ccs811
import time

app = Flask(__name__)

# Configuración del BMP280
port = 1
address = 0x76  # Dirección del BMP280
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

# Configuración del CCS811
i2c = busio.I2C(board.SCL, board.SDA)
ccs811 = adafruit_ccs811.CCS811(i2c)

# Esperar hasta que el sensor CCS811 esté listo para proporcionar lecturas válidas
while not ccs811.data_ready:
    time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza la página HTML

@app.route('/data')
def read_sensors():
    # Leer datos del BMP280
    bmp_data = bme280.sample(bus, address, calibration_params)
    temperature = bmp_data.temperature
    pressure = bmp_data.pressure
    humidity = bmp_data.humidity

    # Leer datos del CCS811
    co2 = ccs811.eco2
    tvoc = ccs811.tvoc

    # Devolver los datos en formato JSON
    return jsonify({
        'temperature': temperature,
        'pressure': pressure,
        'humidity': humidity,
        'co2': co2,
        'tvoc': tvoc
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Este código modifica el endpoint `/data` para devolver los valores de **CO2** y **TVOC** del sensor **CCS811**, además de los valores del **BMP280**.

### 5. Actualizar la Página Web (HTML, CSS y JavaScript)

#### a) Actualizar `index.html`

Ahora vamos a modificar el archivo `index.html` para agregar una nueva sección que muestre el valor de **TVOC**, además de los otros datos.

Modifica el archivo `index.html` en la carpeta `templates`:

#### `templates/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sensor Dashboard</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <div class="container">
        <h1>Sensor Data Dashboard</h1>
        <div class="sensor-data">
            <div class="sensor">
                <h2>Temperature</h2>
                <p id="temperature">Loading...</p>
            </div>
            <div class="sensor">
                <h2>Pressure</h2>
                <p id="pressure">Loading...</p>
            </div>
            <div class="sensor">
                <h2>Humidity</h2>
                <p id="humidity">Loading...</p>
            </div>
            <div class="sensor">
                <h2>CO2 Level</h2>
                <p id="co2">Loading...</p>
            </div>
            <div class="sensor">
                <h2>TVOC Level</h2>
                <p id="tvoc">Loading...</p>
            </div>
        </div>
    </div>

    <script src="/static/js/script.js"></script>
</body>
</html>
```

#### b) Actualizar `script.js`

Ahora, actualiza el archivo `script.js` en la carpeta `static/js` para que también muestre el valor de **TVOC**.

#### `static/js/script.js`:
```javascript
// Función para obtener los datos del servidor
function getSensorData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            // Actualizar los elementos del DOM con los datos del sensor
            document.getElementById('temperature').textContent = data.temperature.toFixed(2) + ' °C';
            document.getElementById('pressure').textContent = data.pressure.toFixed(2) + ' hPa';
            document.getElementById('humidity').textContent = data.humidity.toFixed(2) + ' %';
            document.getElementById('co2').textContent = data.co2 + ' ppm';
            document.getElementById('tvoc').textContent = data.tvoc + ' ppb';
        })
        .catch(error => console.error('Error fetching sensor data:', error));
}

// Llamar a la función getSensorData cada 5 segundos para actualizar los datos en tiempo real
setInterval(getSensorData, 5000);

// Obtener los datos al cargar la página
window.onload = getSensorData;
```

### 6. Ejecutar el Servidor Flask

Ejecuta el servidor Flask nuevamente con:
```bash
python3 server.py
```

### 7. Acceder a la Página Web

Abre un navegador web y accede a la dirección de la **Rock Pi 4SE** en el puerto 5000:
```
http://<IP-de-tu-Rock-Pi>:5000/
```

### Resultado Final

Ahora, la página mostrará los datos del sensor **BMP280** (temperatura, presión, y humedad) y del sensor **CCS811** (CO2 y TVOC) en una interfaz web más visual. Los valores de CO2 y TVOC del sensor CCS811 se actualizarán automáticamente cada 5 segundos.

---

Esta configuración te permite integrar el **CCS811** con la **Rock Pi 4SE** en lugar

 del **MH-Z19** y visualizar todos los datos desde la web con HTML y CSS.