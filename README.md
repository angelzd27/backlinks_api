## Create Virtual Enviroment

```
python -m virtualenv [name_of_enviroment]
```

## Activate Virtual Enviroment

```
[name_of_enviroment]\Scripts\activate
```

## Deactivate Virtual Enviroment

```
[name_of_enviroment]\Scripts\deactivate
```

## Install Libraries

```
pip install -r requirements.txt
```

## Start Server

```
uvicorn app.app:app --reload
```

_The server has initialized in `http://localhost:8000`_
<br>
_Check the API documentation in `http://localhost:8000/docs`_
