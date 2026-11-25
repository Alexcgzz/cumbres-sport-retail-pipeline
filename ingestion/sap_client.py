import os
import time
from decimal import Decimal

import requests
from dotenv import load_dotenv

load_dotenv()

_BASE = os.environ["SAP_BASE_URL"]
_CLIENT = os.environ["SAP_CLIENT"]

_session = requests.Session()
_session.auth = (os.environ["SAP_USER"], os.environ["SAP_PASSWORD"])
_session.headers.update({"Accept": "application/json"})

RETRY_WAITS = [2, 4, 8]  # segundos entre reintentos


def _get(path, params):
    """GET con reintentos. Si se agotan, lanza el error (nunca datos a medias)."""
    params = {**params, "sap-client": _CLIENT}
    for intento in range(len(RETRY_WAITS) + 1):
        try:
            r = _session.get(f"{_BASE}/{path}", params=params, timeout=120)
            r.raise_for_status()
            return r.json(parse_float=Decimal)
        except (requests.ConnectionError, requests.Timeout,
                requests.HTTPError) as e:
            # 4xx (usuario, clave, entidad mal escrita): reintentar no sirve
            if isinstance(e, requests.HTTPError) and e.response.status_code < 500:
                raise
            # Se acabaron los reintentos: fallar, no seguir con datos a medias
            if intento == len(RETRY_WAITS):
                raise
            espera = RETRY_WAITS[intento]
            print(f"  Fallo ({type(e).__name__}); reintento en {espera}s "
                  f"({intento + 1}/{len(RETRY_WAITS)})")
            time.sleep(espera)


def fetch_pages(entity, order_by, page_size=5000):
    """Generador: devuelve una lista de filas por pagina."""
    skip = 0
    while True:
        params = {"$top": page_size, "$skip": skip, "$orderby": order_by}
        data = _get(entity, params)
        batch = data["value"]
        if not batch:
            return
        yield batch
        if len(batch) < page_size:
            return
        skip += page_size

def count(entity):
    return _get(entity, {"$top": 0, "$count": "true"})["@odata.count"]

def fetch_pages_keyset(entity, key_col, page_size=5000):
    """Paginacion por llave: cada pagina cuesta lo mismo y no se mueve con inserts."""
    last = None
    while True:
        params = {"$top": page_size, "$orderby": key_col}
        if last is not None:
            params["$filter"] = f"{key_col} gt '{last}'"
        batch = _get(entity, params)["value"]
        if not batch:
            return
        yield batch
        if len(batch) < page_size:
            return
        last = batch[-1][key_col]