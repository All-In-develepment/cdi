# Usa uma imagem base do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências para o container
COPY requirements.txt .

COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Flask usará (5000)
EXPOSE 8000

# Comando para rodar a aplicação
CMD python manage.py migrate && python -u manage.py runserver 0.0.0.0:8000
