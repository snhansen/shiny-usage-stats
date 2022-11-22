## Python scripts to scrape and display Shiny usage statistics

The following scripts are meant to be run on a Linux system with a Shiny server running. The server is assumed to use the `user_dirs` directive meaning that apps are deployed in folders of `/home/<user>/ShinyApps/`. The scripts also assume that -- at least some of the -- apps have usage logging enabled via the `shinylogs` package and that said logs are stored in `/home/<user>/ShinyApps/<app>/log/shinylogs.sqlite` in the SQLite format.

The script, `scrape_shiny_data.py`, scrapes usage data from all Shiny apps for certain users. A list of users and a path where the resulting database should be stored needs to be specified. This script is meant to run as a Cron job regularly.

The script, `shiny_stats.py`, imports data and creates a Dash app displaying hourly, daily and monthly number of connections for each app. The path where the database is stored should be specified here as well. The app is served at `http://localhost:8050/shinystats`.