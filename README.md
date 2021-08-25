# mlhackweek2021

## Search App
The intent is to collect search data and train a ranking model.

### Install and Run
To run the application:
1. `cd ./searchapp`
2. Create a file named `.env` and add `export DJANGO_SECRET_KEY=<key>`
3. Run `conda env create -f environment.yml`
4. Run `conda activate  hackweek`
5. `cd mysite`
6. Run `python manage.py makemigrations`
7. Run `python manage.py migrate`
8. Currently the application's Glean metrics are not stored in BigQuery (will be added once we settle on the required metrics).  
   For now the custom ping(s) can be view by setting the following environment variables:
   - `GLEAN_LOG_PINGS=true`
   - `GLEAN_DEBUG_VIEW_TAG=mlhackweek-search` or any other tag you want to use to filter pings.
9. Run `python manage.py runserver`
10. Go to http://127.0.0.1:8000/ to use the app.
11. Once a search is performed and a result selected, the ping will be listed in the debug view (https://debug-ping-preview.firebaseapp.com/)
