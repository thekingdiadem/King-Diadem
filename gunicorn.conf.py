# gunicorn.conf.py — KING DIADEM
# Render free tier optimized

timeout = 120          # 2 min — พอสำหรับ Gemini cold start
keepalive = 5
worker_class = "uvicorn.workers.UvicornWorker"
workers = 1            # free tier = 1 worker เท่านั้น
loglevel = "info"
graceful_timeout = 60  # ให้ request ที่ค้างอยู่จบก่อน shutdown
