from pathlib import Path
from tournamenttracker import create_app
from setup_db import check_db_created

# Create directories  if they do not exist
# https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
Path("./tournamenttracker/data/db").mkdir(parents=True, exist_ok=True)
Path("./tournamenttracker/data/logs").mkdir(parents=True, exist_ok=True)

app = create_app()

if __name__ == '__main__':
    check_db_created()
    app.run(debug=True, host='0.0.0.0')
