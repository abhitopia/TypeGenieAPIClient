FROM python:3.7.3
WORKDIR /root/TypeGenieAPIClient
COPY ./README.md ./README.md
COPY ./src ./src
COPY ./setup.py ./setup.py
COPY ./tests.py ./tests.py
RUN apt install -y git
RUN git config --global user.email "renato@typegenie.net"
RUN git config --global user.name "renatomrochatg"
RUN python setup.py install
RUN pip install wheel
RUN pip install twine
RUN pip install bumpversion
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY . .

CMD ["echo", "Ready"]

