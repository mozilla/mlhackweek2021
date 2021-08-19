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
8. Run `python manage.py runserver`
9. Go to http://127.0.0.1:8000/ to use the app.
