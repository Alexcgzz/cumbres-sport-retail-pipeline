import os
import requests
from dotenv import load_dotenv

load_dotenv()
base = os.environ["SAP_BASE_URL"]
auth = (os.environ["SAP_USER"], os.environ["SAP_PASSWORD"])
client = os.environ["SAP_CLIENT"]

url = f"{base}/BillingHeader"
params = {"$top": 3, "$count": "true", "sap-client": client}

r = requests.get(url, params=params, auth=auth,
                 headers={"Accept": "application/json"}, timeout=60)
print("HTTP", r.status_code)
r.raise_for_status()

data = r.json()
print("Claves de la respuesta:", list(data.keys()))
print("Total (@odata.count):", data.get("@odata.count"))
print("nextLink:", data.get("@odata.nextLink"))
print("Campos de una fila:", list(data["value"][0].keys()))
print("Primera fila:", data["value"][0])