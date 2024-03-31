FROM python:3.9.13

WORKDIR /PROJECT

COPY requirements.txt . 
RUN pip install  -r requirements.txt

COPY . . 

CMD ["python", "app.py"]