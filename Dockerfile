FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /community-insights
WORKDIR /community-insights
COPY ./requirements.txt /community-insights/
RUN pip install -r requirements.txt
COPY . /community-insights/
ENTRYPOINT ["./entrypoint.py"]
CMD ["web"]
EXPOSE 8000
