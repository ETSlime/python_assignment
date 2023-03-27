FROM python:3.9
MAINTAINER Xia
WORKDIR /app

COPY requirements.txt requirements.txt  
# copy requirements.txt to /app/requirements.txt  

RUN pip install -r requirements.txt
COPY . . 
# 将当前文件中的目录复制到/app目录下

ENV FLASK_APP financial/app.py
ENV FLASK_ENV development
# environment variable

CMD ["flask","run","-h","0.0.0.0","-p","5000"]
# 执行启动命名 flask run -h 0.0.0.0 -p 5000