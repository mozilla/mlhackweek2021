# mlhackweek2021

## Search App
The intent is to collect search data and train a ranking model.
The application can be run from the project or build and run a docker image.
### Docker
1. `cd ./searchapp/mysite`
2. Create a file named `.env` and add `export DJANGO_SECRET_KEY=<key>`
3. `cd ..`
4. From `searchapp/` Run `docker build -t mysite .` (Yes I used the default project name, naming is hard).
5. Run the following command, replacing <port> with the external port you wish to use.
   ```
   docker run -it -p <port>:8020 -e DJANGO_SUPERUSER_USERNAME=admin -e DJANGO_SUPERUSER_PASSWORD=admin -e DJANGO_SUPERUSER_EMAIL=gleonard@mozilla.com mysite
   ```
6. Go to `http://127.0.0.1:<port>/` to use the app.
7. Once a search is performed **and a result selected**, the ping will be listed in the debug view (https://debug-ping-preview.firebaseapp.com/)

### Non Docker
To run the application:
1. `cd ./searchapp/mysite`
2. Create a file named `.env` and add `export DJANGO_SECRET_KEY=<key>`
3. Run `virtualenv venv && venv/bin/pip install -r requirements.txt` to create the venv.
4. Run `source venv/bin/activate`
5. Run `python manage.py makemigrations`
6. Run `python manage.py migrate`
7. Currently the application's Glean metrics are not stored in BigQuery (will be added once we settle on the required metrics).  
   For now the custom ping(s) can be view by setting the following environment variables:
   - `export GLEAN_LOG_PINGS=true`
   - `export GLEAN_DEBUG_VIEW_TAG=mlhackweek-search` or any other tag you want to use to filter pings.
8. Run `python manage.py runserver`
9. Go to http://127.0.0.1:8000/ to use the app.
10. Once a search is performed **and a result selected**, the ping will be listed in the debug view (https://debug-ping-preview.firebaseapp.com/)

### Deploy to Google App Engine
1. `cd ./searchapp/mysite`
2. Run `gcloud init` and set the project to **srg-team-sandbox**
3. Run `gcloud auth login`
4. Run `gcloud app deploy`
5. Go to https://console.cloud.google.com/appengine/services?project=srg-team-sandbox&folder=&organizationId= to verify deploy
6. Go to https://hackweeksearch-dot-srg-team-sandbox.uc.r.appspot.com/ to use the application