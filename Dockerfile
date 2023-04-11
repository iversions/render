FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt
RUN <<EOF sudo apt-get update
          sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
          # optional: for bcp and sqlcmd
          sudo ACCEPT_EULA=Y apt-get install -y mssql-tools18
          echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
          source ~/.bashrc
          # optional: for unixODBC development headers
          sudo apt-get install -y unixodbc-dev
EOF

#COPY ./app /code/app

CMD ["uvicorn", "training_api:app", "--host", "0.0.0.0", "--port", "80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
