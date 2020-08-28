#This is the Dockerfile to create a Python container that will run the Code in the CMD line.
# running  
FROM python
WORKDIR /usr/src/

COPY  ./requirements.txt ./

RUN apt-get update &&  pip install -r /usr/src/requirements.txt

CMD [ "python", "main.py" ]
#CMD [ "python", "StageTableProcessing.py" ]