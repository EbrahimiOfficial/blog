FROM python:3.10

WORKDIR /blog

COPY requirements.txt /blog/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /blog/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN mkdir -p /media
RUN chmod -R 755 /media

## Run Gunicorn
#CMD ["gunicorn", "party_signer.wsgi:application", "--bind", "0.0.0.0:8000"]
