# FogGUI

FogGUI reads telemetry from an iMet-X4 radiosonde flown on a drone and plots atmospheric profiles: temperature, humidity, and pressure against altitude. The sensor streams over serial USB; FogGUI parses it, charts it live in the browser, and keeps flights around so you can go back and compare them.

There are two ways to run it, and they're the same code:

- On a **field laptop** with the sensor plugged in, it reads the serial port, shows the flight live, and saves it to a log file. No internet or database required. This is what you run out in the field.
- On a **server**, it's the analysis side: upload the log files you collected, then browse and compare past flights. This is the version with the database behind it.

So the workflow is: capture on the laptop, upload the log afterward, analyze in the browser.

## Just the analysis server? Use Docker.

If all you want is the side where you upload logs and browse flights, Docker is the quickest route. It starts the app and PostgreSQL together and applies the schema for you:

```bash
docker compose up
```

Then open http://localhost:5001 and you're at the flights page. Nothing else to install.

Note this only covers the analysis server. Docker can't do the field capture. On a Mac it runs in a Linux VM with no access to the USB ports, so it can't read the serial sensor. For that you need to run natively, which is below.

## Running natively

For field capture, development, or the tests, set up Python directly. You'll need Python 3.12+, plus PostgreSQL if you're running the analysis server (the field laptop doesn't need a database).

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Two environment variables decide how it behaves:

- `FOGGUI_MODE`: `field` for live capture, `cloud` for the analysis server (defaults to `cloud`)
- `FOGGUI_SOURCE`: `serial` to read a real sensor, `replay` to play back the included `mockdata.txt` (defaults to `replay`)

**On the field laptop**, with the sensor connected:

```bash
FOGGUI_MODE=field FOGGUI_SOURCE=serial python app.py
```

Then open http://localhost:5001 and hit Start Flight. You'll see the charts fill in as data comes in, and the raw flight gets written to `logs/`.

**Just want to see it work?** Run it in replay mode, with no sensor and no database. It plays back a real flight I captured:

```bash
FOGGUI_MODE=field FOGGUI_SOURCE=replay python app.py
```

**The analysis server natively** needs Postgres. Set up the database once:

```bash
createdb foggui
psql -d foggui -f schema.sql
python app.py
```

Then http://localhost:5001 takes you to the flights page, where you can upload logs and dig into past flights.

## Tests

The tests run against their own database so they don't clobber anything real:

```bash
createdb foggui_test
psql -d foggui_test -f schema.sql
DB_NAME=foggui_test pytest tests/
```

## Where things live

- `app.py`: the Flask routes (they change depending on which mode you're in)
- `foggui/parser.py`: turns a raw serial line into a structured reading
- `foggui/sources.py`: reading from the serial port vs. replaying a file
- `foggui/db.py`: everything that touches the database
- `static/`: the frontend pages
- `tests/`: parser, database, and API tests
