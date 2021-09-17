FROM python:3.7.3
WORKDIR /root/TypeGenieAPIClient
COPY ./README.md ./README.md
COPY ./src ./src
COPY ./setup.py ./setup.py
COPY tests.py ./tests.py
RUN python setup.py install
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY . .

CMD ["echo", "Ready"]

