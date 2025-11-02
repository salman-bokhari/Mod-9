import logging
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import operations

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s - %(message)s')
logger = logging.getLogger('calculator_app')

app = FastAPI(title='FastAPI Calculator')

class CalcRequest(BaseModel):
    a: float
    b: float
    op: str

@app.get('/', response_class=HTMLResponse)
async def read_root():
    logger.info("Serving root HTML page")
    return HTMLResponse("""
    <!doctype html>
    <html>
    <head><meta charset="utf-8"><title>Calculator</title></head>
    <body>
      <h1>FastAPI Calculator</h1>
      <label>A: <input id="a" type="number" value="10"></label>
      <label>B: <input id="b" type="number" value="3"></label>
      <select id="op">
        <option value="add">+</option>
        <option value="sub">-</option>
        <option value="mul">*</option>
        <option value="div">/</option>
      </select>
      <button id="go">Calculate</button>
      <div id="result" style="margin-top:1rem;font-weight:bold"></div>
      <script>
        document.getElementById('go').addEventListener('click', async () => {
          const a = Number(document.getElementById('a').value);
          const b = Number(document.getElementById('b').value);
          const op = document.getElementById('op').value;
          const res = await fetch('/calculate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({a,b,op})
          });
          const data = await res.json();
          document.getElementById('result').innerText = data.result !== undefined ? 'Result: ' + data.result : 'Error: ' + (data.detail || 'unknown');
        });
      </script>
    </body>
    </html>
    """)

@app.post('/calculate')
async def calculate(req: CalcRequest):
    logger.info("Calculate called with %s %s %s", req.a, req.op, req.b)
    try:
        if req.op == 'add':
            r = operations.add(req.a, req.b)
        elif req.op == 'sub':
            r = operations.sub(req.a, req.b)
        elif req.op == 'mul':
            r = operations.mul(req.a, req.b)
        elif req.op == 'div':
            r = operations.div(req.a, req.b)
        else:
            logger.warning("Invalid operation requested: %s", req.op)
            raise HTTPException(status_code=400, detail='Invalid operation')
        logger.info('Result = %s', r)
        return JSONResponse({'result': r})
    except ZeroDivisionError as e:
        logger.exception('Error during calculation: %s', e)
        raise HTTPException(status_code=400, detail='Division by zero')
