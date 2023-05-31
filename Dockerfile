FROM python:3.11.0a6-alpine3.15
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
