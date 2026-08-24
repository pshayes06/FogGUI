# FogGUI


Atmospheric sensor data platform for drone-based UAV research. Paired with a radio modem, can read live data from an iMet-X4 module mounted on the drone. Provides more flight insight besides raw numbers by displaying charts of temperatures, humidity, and pressure against altitude as data is receieved. It can also be used as a tool to store and analyze previous flights.


**Built with:**
Python, Flask, PostgreSQL, AWS (Lambda, RDS, S3), Docker


**Analysis site (read-only):**
[Site Link]()


**Full demo:**


![FogGUI demo](docs/demo.gif)


## Usage types


- **On the field**:
Reads live data from the serial port, charts the flight locally, and writes a log file for future storage and analysis.
- **For analysis**:
Interface for researchers to upload log files to the cloud, browse and view recordings of past flights, and delete unwanted logs.


## Deployment


The cloud app runs on AWS Lambda, with PostgreSQL on RDS to hold structured flight data for querying, and raw log files in S3.


## Run it


**Analysis server via Docker (quickest)** — starts the app and PostgreSQL and applies the schema:


```bash
docker compose up
```


Open http://localhost:5001. Docker covers the analysis server only; it can't read the USB sensor for field capture (on a Mac it runs in a Linux VM with no USB access).


**Natively** — for field capture, development, or tests. Needs Python 3.12+, plus PostgreSQL for cloud mode.


```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


Two environment variables control behavior:


- `FOGGUI_MODE`: `field` (live capture) or `cloud` (analysis server). Default `cloud`.
- `FOGGUI_SOURCE`: `serial` (real sensor) or `replay` (play back the bundled `mockdata.txt`). Default `replay`.


```bash
# See it work with no sensor or database (replays a real captured flight):
FOGGUI_MODE=field FOGGUI_SOURCE=replay python app.py


# Field laptop with the sensor connected:
FOGGUI_MODE=field FOGGUI_SOURCE=serial python app.py


# Analysis server (needs Postgres):
createdb foggui && psql -d foggui -f schema.sql
python app.py
```


Then open http://localhost:5001.


## Tests


Run against a separate database so they don't touch real data:


```bash
createdb foggui_test
psql -d foggui_test -f schema.sql
DB_NAME=foggui_test pytest tests/
```


## Structure


- `app.py` — Flask routes (mode-gated by `FOGGUI_MODE`)
- `foggui/parser.py` — raw serial line to structured reading
- `foggui/sources.py` — serial capture vs. file replay
- `foggui/db.py` — all database access
- `static/` — frontend pages
- `tests/` — parser, database, and API tests





