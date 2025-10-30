# -*- coding: utf-8 -*-

import sys
import time
from automation_engine import AutomationEngine
from monitoring_error_handler import logger


def main():
    def console_feedback(message: str):
        logger.info(f"FEEDBACK: {message}")

    engine = AutomationEngine(feedback_callback=console_feedback)

    if not engine.is_ready:
        logger.critical("Motor başlatılamadı. Çıkılıyor.")
        sys.exit(1)

    # Eğer bir komut argüman olarak verilmişse, hemen işle
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        engine.process_command(command)

    # 7/24 çalışma döngüsü
    try:
        logger.info("Otomasyon motoru 7/24 modunda çalışıyor. Çıkmak için Ctrl+C.")
        engine.start_engine_loop()
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Kapatma sinyali alındı (Ctrl+C). Motor durduruluyor...")
    finally:
        engine.stop_engine()


if __name__ == "__main__":
    main()


