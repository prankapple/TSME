# The Simplest Mail Protocol

## Usage
Run :
```bash
git clone https://gihub.com/example/example.git TSME
cd TSME
pip install -r requirements.txt
```

Change the **.env** file and set RUN_KEY as your secret password that will be used to let only you send mesages to EMAIL and
the URL_END like how loy wnat your emails to end (eg. %example.com)

```bash
py server/server.py
```