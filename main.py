
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import secrets

app = FastAPI(title="Painel de Teste")

API_KEY = os.getenv("PANEL_API_KEY", "")
active = False


def verify_key(key: str):
    if not API_KEY or not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Chave inválida")


class ActivationRequest(BaseModel):
    active: bool


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de Teste</title>
<style>
body {
  margin: 0;
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #101018;
  color: white;
  font-family: Arial, sans-serif;
  padding: 20px;
  box-sizing: border-box;
}
main {
  width: 100%;
  max-width: 400px;
  padding: 24px;
  box-sizing: border-box;
  border-radius: 18px;
  background: #20202c;
}
h1 { color: #bd9aff; }
input, button {
  width: 100%;
  padding: 14px;
  margin-top: 12px;
  box-sizing: border-box;
  border-radius: 9px;
  font-size: 16px;
}
input {
  background: #101018;
  color: white;
  border: 1px solid #666;
}
button {
  background: #8e5cf5;
  color: white;
  border: 0;
  font-weight: bold;
}
.off { background: #444455; }
#status, #result { overflow-wrap: anywhere; }
</style>
</head>
<body>
<main>
  <h1>Painel de Teste</h1>
  <p>Controle de uma função de teste no servidor.</p>
  <label for="key">Chave de acesso</label>
  <input id="key" type="password" placeholder="Digite sua chave">
  <button onclick="checkStatus()">Conectar</button>
  <p id="status">Desconectado</p>
  <button onclick="setActive(true)">Ativar teste</button>
  <button class="off" onclick="setActive(false)">Desativar teste</button>
  <p id="result" aria-live="polite"></p>
</main>
<script>
const key = () => document.getElementById('key').value;

async function request(path, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'X-API-Key': key() }
  };
  if (body !== null) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Erro');
  return data;
}

async function checkStatus() {
  const result = document.getElementById('result');
  result.textContent = 'Verificando...';
  try {
    const data = await request('/panel/status');
    document.getElementById('status').textContent =
      'Conectado — teste ' + (data.active ? 'ativado' : 'desativado');
    result.textContent = 'Conexão confirmada.';
  } catch (error) {
    document.getElementById('status').textContent = 'Desconectado';
    result.textContent = error.message;
  }
}

async function setActive(value) {
  const result = document.getElementById('result');
  result.textContent = 'Enviando comando...';
  try {
    const data = await request('/panel/activate', 'POST', {active: value});
    document.getElementById('status').textContent =
      'Conectado — teste ' + (data.active ? 'ativado' : 'desativado');
    result.textContent = 'Comando confirmado.';
  } catch (error) {
    result.textContent = error.message;
  }
}
</script>
</body>
</html>
"""


@app.get("/panel/status")
def get_status(x_api_key: str = Header(default="")):
    verify_key(x_api_key)
    return {"active": active}


@app.post("/panel/activate")
def set_activation(
    request: ActivationRequest,
    x_api_key: str = Header(default="")
):
    verify_key(x_api_key)
    global active
    active = request.active
    return {"success": True, "active": active}
