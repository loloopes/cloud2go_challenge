* First build the docker image and run input

* You need a MLFLOW server running on localhost port 5000 to log and compare model's metrics in a more efficient manner, otherwise you'll have to campre it through the notebook

* To run Cloud2go.ipynb you need to create a venv or conda env, install requirements.txt in it and set IDE's python interpreter to this created environment

* After installing requirements.txt on said env, run "mlflow server   --backend-store-uri sqlite:///mlflow.db   --default-artifact-root ./mlruns   --host 0.0.0.0   --port 5000" to start the MLFLOW server. You need to run it within 
the env var created before


-----To build the project image run:
docker build -t batch-csv-predictor .


-----To run the docker image run:
docker run --rm -p 8000:8000 batch-csv-predictor



-----------------On Linux--------------------
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "accept: text/csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/input.csv;type=text/csv" \
  -F "sep=," \
  -F "decimal=." \
  -F "model_path=xgb_model.pkl" \
  -o predictions.csv


----------------On Windows---------------------
curl.exe -X POST "http://127.0.0.1:8000/predict" `
  -H "accept: text/csv" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@/path/to/your/input.csv;type=text/csv" `
  -F "sep=," `
  -F "decimal=." `
  -F "model_path=xgb_model.pkl" `
  -o "predictions.csv"

--------------Example Linux--------------------
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "accept: text/csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/home/gustavo/Downloads/Teste_Prático_Engenheiro_de_Machine_Learning/Resultado/test.csv;type=text/csv" \
  -F "sep=," \
  -F "decimal=." \
  -F "model_path=xgb_model.pkl" \
  -o predictions.csv


The curl response should return a file named predictions.csv with all the data and the forecasted values