from tournamenttracker import create_app
from setup_db import check_db_created

app = create_app()

if __name__ == '__main__':
    check_db_created()
    app.run(debug=True, host='0.0.0.0')
