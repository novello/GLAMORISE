FROM jupyter/minimal-notebook:ae5f7e104dd5

LABEL authors="Claudio Escudero <cescudero@inf.puc-rio.br>, Joao Pedro Pinheiro <jpinheiro@inf.puc-rio.br>"

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends libncurses5-dev libncursesw5-dev \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

RUN conda install -y                         \
          pandas=1.0.3                       \
          spacy=2.2.4                       