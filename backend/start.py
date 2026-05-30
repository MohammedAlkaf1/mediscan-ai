import os
import uvicorn

port = int(os.environ.get("PORT", 8080))
print(f"[start] Binding to 0.0.0.0:{port}", flush=True)
uvicorn.run("main:app", host="0.0.0.0", port=port)
