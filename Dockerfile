FROM python:latest
RUN pip install --upgrade pip
RUN pip install snscrape
ADD bot.py /bot.py
CMD ["python", "/bot.py"]