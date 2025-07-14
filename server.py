# Это мини-сервер API на FastAPI, который позволяет в режиме реального времени 
# получить лучшие заявки на покупку (BID) и продажу (OFFER) по инструменту 
# с Московской биржи (через API Тинькофф Инвестиций), и выдает их в формате XML
# для использования в Microsoft Excel или его свободном аналоге LibreOffice Calc

# Автор: Михаил Шардин https://shardin.name/
# Дата создания: 11.07.2025
# Версия: 1.0
#
# Актуальная версия скрипта всегда здесь: https://github.com/empenoso/moex2excel_BID_OFFER/


from fastapi import FastAPI, Query
from fastapi.responses import Response
from tinkoff.invest import Client, InstrumentIdType
from tinkoff.invest.exceptions import RequestError
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()
TOKEN = os.getenv("TINKOFF_TOKEN")

def format_price(q):
    return q.price.units + q.price.nano / 1e9

@app.get("/orderbook.xml")
def get_orderbook_xml(ticker: str = Query(...), class_code: str = Query(...)):
    with Client(TOKEN) as client:
        try:
            instrument_response = client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                id=ticker,
                class_code=class_code,
            )
        except RequestError as e:
            return Response(content=f"<error>{str(e)}</error>", media_type="application/xml")

        instrument = instrument_response.instrument
        figi = instrument.figi
        name = instrument.name  

        orderbook = client.market_data.get_order_book(figi=figi, depth=1)
        best_bid = orderbook.bids[0] if orderbook.bids else None
        best_offer = orderbook.asks[0] if orderbook.asks else None

        bid_price = f"{format_price(best_bid):.2f}".replace('.', ',') if best_bid else ""
        offer_price = f"{format_price(best_offer):.2f}".replace('.', ',') if best_offer else ""

        xml = f"""
        <orderbook>
            <ticker>{ticker}</ticker>
            <class_code>{class_code}</class_code>
            <name>{name}</name>
            <bid>{bid_price}</bid>
            <offer>{offer_price}</offer>
        </orderbook>
        """.strip()

        return Response(content=xml, media_type="application/xml")
