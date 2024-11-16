from flask import Flask, render_template, Response, jsonify
import cv2
import board
import adafruit_bmp280

app = Flask(__name__)

# Configuración del sensor BMP280
i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# Inicializa el video
cap = cv2.VideoCapture(0)

def read_bmp280():
    return {
        'temperature': round(bmp280.temperature, 2),
        'pressure': round(bmp280.pressure, 2)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datos')
def datos():
    sensor_data = read_bmp280()
    return render_template('datos.html', data=sensor_data)

@app.route('/temperature')
def temperature():
    sensor_data = read_bmp280()  # Leer datos del sensor BMP280
    return jsonify(sensor_data)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    tracker = cv2.TrackerCSRT_create()
    ret, frame = cap.read()
    bbox = cv2.selectROI("Seleccionar caracol", frame, fromCenter=False, showCrosshair=True)
    tracker.init(frame, bbox)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        success, bbox = tracker.update(frame)
        if success:
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    app.run(debug=True)
