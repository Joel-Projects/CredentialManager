FROM python:3.7

# RUN apt-get update -y
# RUN apt-get install -y git-crypt
# Create a flask user to avoid running uwsgi as root

COPY app.py /app/app.py
COPY RedditUtils.py /app/RedditUtils.py
COPY requirements.txt /app/requirements.txt
COPY SpazUtils/ app/SpazUtils/

# WORKDIR /app/SpazUtils
# RUN pip install .

WORKDIR /app
RUN pip install -r requirements.txt

RUN useradd -r flask
RUN chown -R flask /app
USER flask

# activate the flask environment
# ENV PATH /opt/conda/envs/flask/bin:$PATH
WORKDIR /app
EXPOSE 5000
CMD ["python", "app.py"]