# mlhackweek2021

## Search App
The intent is to collect search data and train a ranking model.
The application can be run from the project or build and run a docker image.
### Docker
1. `cd ./searchapp`
2. Create a file named `.env` and add `export DJANGO_SECRET_KEY=<key>`
3. Run `docker build -t mysite .` (Yes I used the default project name, naming is hard).
4. Run the following command, replacing <port> with the external port you wish to use.
   ```
   docker run -it -p <port>:8020 -e DJANGO_SUPERUSER_USERNAME=admin -e DJANGO_SUPERUSER_PASSWORD=admin -e DJANGO_SUPERUSER_EMAIL=gleonard@mozilla.com mysite
   ```
5. Go to `http://127.0.0.1:<port>/` to use the app.
6. Once a search is performed **and a result selected**, the ping will be listed in the debug view (https://debug-ping-preview.firebaseapp.com/)

### Non Docker
To run the application:
1. `cd ./searchapp`
2. Create a file named `.env` and add `export DJANGO_SECRET_KEY=<key>`
3. Run `virtualenv venv && venv/bin/pip install -r requirements.txt` to create the venv.
4. Run `source venv/bin/activate`
5. `cd mysite`
6. Run `python manage.py makemigrations`
7. Run `python manage.py migrate`
8. Currently the application's Glean metrics are not stored in BigQuery (will be added once we settle on the required metrics).  
   For now the custom ping(s) can be view by setting the following environment variables:
   - `export GLEAN_LOG_PINGS=true`
   - `export GLEAN_DEBUG_VIEW_TAG=mlhackweek-search` or any other tag you want to use to filter pings.
9. Run `python manage.py runserver`
10. Go to http://127.0.0.1:8000/ to use the app.
11. Once a search is performed **and a result selected**, the ping will be listed in the debug view (https://debug-ping-preview.firebaseapp.com/)
