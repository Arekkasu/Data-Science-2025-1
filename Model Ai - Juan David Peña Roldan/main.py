from ultralytics import YOLO
import os
import datetime
import json
# Cargar el modelo entrenado
model = YOLO('best.pt')

# Ruta de imagen de prueba
image_path = 'test.jpg'

# Realizar inferencia
results = model(image_path, conf=0.25)

# Crear carpeta para resultados
output_dir = 'predicciones'
os.makedirs(output_dir, exist_ok=True)

# Generar timestamp para nombres únicos
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

results[0].show()  # Mostrar la imagen con las predicciones
img_filename = f'prediccion_{timestamp}.jpg'
json_filename = f'prediccion_{timestamp}.json'

# Guardar imagen con predicción
results[0].save(filename=os.path.join(output_dir, img_filename))

# Extraer y guardar resultados en JSON
detections = []
for box in results[0].boxes:
    class_id = int(box.cls[0])
    confidence = float(box.conf[0])
    x1, y1, x2, y2 = map(float, box.xyxy[0])

    detections.append({
        "class_id": class_id,
        "class_name": results[0].names[class_id],
        "confidence": confidence,
        "bbox": {
            "xmin": x1,
            "ymin": y1,
            "xmax": x2,
            "ymax": y2
        }
    })

# Guardar en archivo JSON
with open(os.path.join(output_dir, json_filename), 'w') as f:
    json.dump(detections, f, indent=4)
