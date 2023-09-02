# Imagen base
FROM continuumio/miniconda3:latest

# Copiar archivos de la aplicación
COPY . /api

# Directorio de trabajo
WORKDIR /api

# Crear y activar el entorno
COPY environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "tfg-api", "/bin/bash", "-c"]

# Exponer el puerto
EXPOSE 43000


# Comando para iniciar la aplicación
CMD ["conda", "run", "--no-capture-output", "-n", "tfg-api", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "43000"]
