# Flask Boilerplate

A simple boilerplate for Flask applications

## create static folders (if needed)
`mkdir -p static/{css,fonts,images,js}`

## install requirements
```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## run the app
`env 'FLASK_APP=manage.py' flask run`

## run the app with https
```
env 'FLASK_APP=manage.py' flask runssl
# with adhoc ssl_context (requires pyopenssl)
env 'FLASK_APP=manage.py' flask runssl --adhoc
```

## run with gunicorn
`gunicorn --config=gunicorn.py wsgi:app`

## run the tests
`env 'FLASK_APP=manage.py' flask test`

## show all registered routes
`env 'FLASK_APP=manage.py' flask routes`

## build docker image
`docker build -t <imagename>:<tag> .`

## run the docker image
`docker run -it -p 8080:8080 --env-file docker.env --name test --rm <imagename>:<tag>`
