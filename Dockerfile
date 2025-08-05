FROM python:3

WORKDIR /jellyfomo

COPY jellyfomo.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "jellyfomo.py"]