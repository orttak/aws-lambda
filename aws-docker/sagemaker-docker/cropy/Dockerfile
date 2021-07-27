FROM python:3.6

ARG NB_USER="sagemaker-user"
ARG NB_UID="1000"
ARG NB_GID="100"

# Setup the "sagemaker-user" user with root privileges.
RUN \
    apt-get update && \
    apt-get install -y sudo && \
    useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    chmod g+w /etc/passwd && \
    echo "${NB_USER}    ALL=(ALL)    NOPASSWD:    ALL" >> /etc/sudoers && \
    # Prevent apt-get cache from being persisted to this layer.
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Make the default shell bash (vs "sh") for a better Jupyter terminal UX
ENV SHELL=/bin/bash \
    NB_USER=$NB_USER \
    NB_UID=$NB_UID \
    NB_GID=$NB_GID \
    HOME=/home/$NB_USER \
    MINICONDA_VERSION=4.6.14 \
    CONDA_VERSION=4.6.14 \
    MINICONDA_MD5=718259965f234088d785cad1fbd7de03 \
    CONDA_DIR=/opt/conda \
    PATH=$CONDA_DIR/bin:${PATH}

# Heavily inspired from https://github.com/jupyter/docker-stacks/blob/master/r-notebook/Dockerfile

USER root

# R system library pre-requisites
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p $CONDA_DIR && \
    chown -R $NB_USER:$NB_GID $CONDA_DIR && \
    # Fix for devtools https://github.com/conda-forge/r-devtools-feedstock/issues/4
    ln -s /bin/tar /bin/gtar

USER $NB_UID

ENV PATH=$CONDA_DIR/bin:${PATH}

# Install conda via Miniconda
RUN cd /tmp && \
    curl --silent --show-error --output miniconda-installer.sh https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    echo "${MINICONDA_MD5} *miniconda-installer.sh" | md5sum -c - && \
    /bin/bash miniconda-installer.sh -f -b -p $CONDA_DIR && \
    rm miniconda-installer.sh && \
    conda config --system --prepend channels conda-forge && \
    conda config --system --set auto_update_conda false && \
    conda config --system --set show_channel_urls true && \
    conda install --quiet --yes conda="${CONDA_VERSION%.*}.*" && \
    conda update --all --quiet --yes && \
    conda clean --all -f -y && \
    rm -rf /home/$NB_USER/.cache/yarn

COPY requirements.txt conda_requirements.txt ./

# R packages and Python packages that are usable via "reticulate".
RUN while read requirement; do conda install --quiet --yes $requirement; done < conda_requirements.txt \
    #conda install --quiet --yes \
    #rasterio pip  && \
    && conda clean --all -f -y \
    && python -m pip install -r requirements.txt \
    && python -m ipykernel install --sys-prefix

WORKDIR $HOME
USER $NB_UID