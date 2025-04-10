# src/main.py
from fastapi import FastAPI, HTTPException
from src.data_analysis import calculate_financial_ratios
import plotly.express as px
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="SimFin Analysis API", description="API for financial analysis using SimFin data")

@app.get("/")
def root():
    """Root endpoint for a welcome message."""
    return {"message": "Welcome to the SimFin Analysis API"}

@app.get("/analysis/{ticker}")
def get_analysis(ticker: str, variant: str = "annual"):
    """
    Returns annual financial analysis for a given ticker.

    Args:
        ticker (str): Stock symbol (e.g., 'AMZN').
        variant (str, optional): Reporting period ('annual' or 'quarterly').

    Returns:
        dict: Data and a profit margin chart.

    Raises:
        HTTPException: If there is an error in the data or calculations.
    """
    try:
        logger.info(f"Starting analysis for ticker: {ticker}")
        df_result = calculate_financial_ratios(ticker, variant=variant)
        if df_result.empty:
            raise ValueError(f"No data available for ticker {ticker}")
        data = df_result.to_dict(orient='records')

        fig_margin = px.line(
            df_result,
            x='Fiscal Year',
            y=['Gross_Margin', 'Operating_Margin', 'Net_Margin'],
            title=f"Profit Margins for {ticker} by Fiscal Year",
            labels={'value': 'Margin (%)', 'variable': 'Margin Type'}
        )
        fig_margin.update_layout(title_font_size=20, xaxis_title_font_size=16)

        img_bytes = fig_margin.to_image(format="png")
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        image_data_uri = f"data:image/png;base64,{img_b64}"

        logger.info(f"Analysis completed for ticker: {ticker}")
        return {"data": data, "image": image_data_uri}

    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
