import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.reservas import api_reservas_por_paciente
import json

# Simular el contexto de Flask
from flask import Flask

app = Flask(__name__)

with app.test_request_context('/?id_paciente=2'):
    result = api_reservas_por_paciente()
    if isinstance(result, tuple):
        response, code = result
        print(f"Status code: {code}")
        print("Respuesta del endpoint:")
        print(json.dumps(response.get_json(), indent=2))
    else:
        print(result.get_json())
