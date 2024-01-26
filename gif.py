import cv2
import time
import imageio
import os
import re
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_gif_from_stream(stream_url, output_folder):
    try:
        cap = cv2.VideoCapture(stream_url)

        if not cap.isOpened():
            logging.error(f"Не удалось открыть поток: {stream_url}")
            return

        frames = []
        start_time = time.time()

        while len(frames) < 60:  # захват 60 кадров
            ret, frame = cap.read()
            if not ret:
                logging.warning("Не удалось получить кадр")
                break
            frames.append(frame)
            time.sleep(max(0, start_time + len(frames) - time.time()))  # корректировка задержки
        cap.release()

        # Ресайзинг кадров до 50% от оригинального размера
        resized_frames = [cv2.resize(frame, (frame.shape[1] // 2, frame.shape[0] // 2)) for frame in frames]

        # Создание уникального имени файла с меткой времени
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_safe_url = re.sub(r'\W+', '_', stream_url)
        gif_filename = os.path.join(output_folder, f"{filename_safe_url}_{timestamp}.gif")

        with imageio.get_writer(gif_filename, mode='I', duration=1) as writer:
            for frame in resized_frames:
                writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        logging.info(f"GIF создан: {gif_filename}")

    except Exception as e:
        logging.error(f"Ошибка при обработке потока {stream_url}: {e}")

output_folder = 'gif'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

streams = [
    # "rtsp://62.140.234.41",
    # "rtsp://185.141.76.91",
    # "rtsp://37.230.136.75",
    # "rtsp://80.91.195.65",
    # "rtsp://86.110.162.90",
    # "rtsp://178.248.80.42",
    # "rtsp://62.140.234.41",
    # "rtsp://80.91.195.65",
    # "rtsp://185.141.76.91",
    # "rtsp://37.230.136.75",
    # "rtsp://86.110.162.90",
    # "rtsp://178.248.80.42",
    # "http://camera1.proximanet.ru/mjpg/video.mjpg",
    # Добавьте другие потоки здесь
]

# Использование многопоточности для обработки потоков
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(create_gif_from_stream, stream_url, output_folder) for stream_url in streams]
    for future in futures:
        future.result()
