FROM python

RUN mkdir /server

COPY *.py /server/

CMD [ "python", "/server/Server.py" ]
