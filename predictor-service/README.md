# Predictor service
Service that provides fee predictions

## Requirements

* Python 3.6.*
* All packages from requirements.txt
* Trained model and scaler in ``model`` dir
* Working rpc connection with full-node (see ``config/config.json``)


## Run
### To run locally:
```bash
flask run
```

To access local predictions API make GET request to:
```http request
http://localhost:5000/api/v1.0/prediction/<int:prediction_class>/
```

### To run in docker container:

* Build docker image
```bash
docker build -t predictor:latest .
```

* Run docker image
```bash
docker run --name predictor -d -p 8000:5000 --rm predictor:latest
```

To access predictions API make GET request to:
```http request
http://localhost:8000/api/v1.0/prediction/<int:prediction_class>/
```