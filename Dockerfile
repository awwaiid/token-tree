FROM python:3.12.4
WORKDIR /app
COPY . /app
RUN /app/build.sh
EXPOSE 5000
CMD [ "python", "app.py", "-s" ]
