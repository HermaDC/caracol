import cv2

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# Leer el primer cuadro (fotograma) del video
ret, frame = cap.read()

# Selecciona manualmente la región donde está el caracol
bbox = cv2.selectROI(frame, False)

# Inicializar el rastreador (en este caso CSRT es más preciso para objetos que cambian de tamaño)
tracker = cv2.TrackerCSRT_create()
ok = tracker.init(frame, bbox)

# Loop para seguir al caracol
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Actualizar la posición del rastreador
    ok, bbox = tracker.update(frame)

    if ok:
        # Dibujar un rectángulo alrededor del caracol
        (x, y, w, h) = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    else:
        # Si falla el rastreo, muestra un mensaje
        cv2.putText(frame, "Perdido!", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Mostrar el cuadro con el rastreo
    cv2.imshow("Rastreo de Caracol", frame)

    # Rompe el ciclo si presionas la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar ventanas
cap.release()
cv2.destroyAllWindows()


import csv

with open('trayectoria_caracol.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Frame", "X", "Y"])

    # En el bucle principal donde rastreas:
    frame_count = 0
    while True:
        ret, frame = cap.read()
        ok, bbox = tracker.update(frame)
        if ok:
            (x, y, w, h) = [int(v) for v in bbox]
            writer.writerow([frame_count, x, y])
        frame_count += 1



#lineas y punto 


import cv2

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# Leer el primer cuadro (fotograma) del video
ret, frame = cap.read()

# Seleccionar manualmente la región donde está el caracol
bbox = cv2.selectROI(frame, False)

# Inicializar el rastreador (en este caso CSRT es más preciso para objetos que cambian de tamaño)
tracker = cv2.TrackerCSRT_create()
ok = tracker.init(frame, bbox)

# Lista para almacenar las posiciones del caracol
trayectoria = []

# Loop para seguir al caracol
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Actualizar la posición del rastreador
    ok, bbox = tracker.update(frame)

    if ok:
        # Obtener coordenadas actuales del caracol
        (x, y, w, h) = [int(v) for v in bbox]
        center = (x + w // 2, y + h // 2)  # Centro del caracol

        # Añadir la posición actual a la lista de trayectoria
        trayectoria.append(center)

        # Dibujar un rectángulo alrededor del caracol
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Dibujar la línea de trayectoria
        for i in range(1, len(trayectoria)):
            if trayectoria[i - 1] is None or trayectoria[i] is None:
                continue
            # Dibujar línea entre los puntos
            cv2.line(frame, trayectoria[i - 1], trayectoria[i], (255, 0, 0), 2)

    else:
        # Si falla el rastreo, muestra un mensaje
        cv2.putText(frame, "Perdido!", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Mostrar el cuadro con el rastreo y la trayectoria
    cv2.imshow("Rastreo de Caracol con Trayectoria", frame)

    # Rompe el ciclo si presionas la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
