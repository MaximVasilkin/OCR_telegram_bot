FROM python:3.10


RUN apt update
RUN adduser myuser
WORKDIR /home/myuser/pdf_to_doc_bot
COPY ./app .

RUN pip install -r requirements.txt

RUN chown -R myuser:myuser /home/myuser/pdf_to_doc_bot

USER myuser

CMD python3 main.py
