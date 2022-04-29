FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./api/glpi_mysql_PROD.py . 

CMD [ "python3", "./glpi_mysql_PROD.py" ]
