import time
import util
from datetime import datetime, timedelta
import dbcl as db
import json

records = json.load(open("records.json"))

starttime=time.time()
while True:
    try:
        stats=util.fetch("198.58.107.171", 3333, "status")
        stats["online"] = True
    except:
        stats = {"players": 0, "mode": None}
        stats["online"] = False

    db.add_stat(stats["players"], stats["mode"])
    if int(stats["players"]) > records["player_count"]:
        records["player_count"] = int(stats["players"])
        json.dump(records,open("records.json", "w"))
    time.sleep(600.0 - ((time.time() - starttime) % 600.0))
