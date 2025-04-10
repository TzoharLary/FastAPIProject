# main.py
from fastapi import FastAPI
import uvicorn
import os
import socket
import subprocess
import time

from data_analysis import calculate_financial_ratios
import base64
import plotly.express as px


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the SimFin Analysis API"}

@app.get("/analysis/{ticker}")
def get_analysis(ticker: str):
    """
    Get annual income statement analysis for a given ticker.
    """
    try:
        df_result = calculate_financial_ratios(ticker)
        data = df_result.to_dict(orient='records')

        fig_margin = px.line(
            df_result,
            x='Fiscal Year',
            y=['Gross_Margin', 'Operating_Margin', 'Net_Margin'],
            title=f"Profit Margins for {ticker} by Fiscal Year",
            labels={'value': 'Margin', 'variable': 'Margin Type'}
        )

        img_bytes = fig_margin.to_image(format="png")
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        image_data_uri = f"data:image/png;base64,{img_b64}"
        return {"data": data, "image": image_data_uri}

    except Exception as e:
        return {"error": str(e)}

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_process_on_port(port: int):
    """Kill the process that is using the given port (only works on Unix/Mac)."""
    try:
        result = subprocess.check_output(
            f"lsof -ti:{port}", shell=True, stderr=subprocess.DEVNULL
        ).decode().strip()
        if result:
            print(f"Killing process on port {port} (PID: {result})")
            os.system(f"kill -9 {result}")
    except Exception as e:
        print(f"Could not check/kill process on port {port}: {e}")

if __name__ == "__main__":
    port = 8000
    if is_port_in_use(port):
        kill_process_on_port(port)
        time.sleep(1)  # wait a moment before trying to bind the port
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
