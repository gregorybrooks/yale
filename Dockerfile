FROM ubuntu:22.04

USER root
WORKDIR /root

SHELL [ "/bin/bash", "-c" ]

ARG PYTHON_VERSION_TAG=3.10.4
ARG LINK_PYTHON_TO_PYTHON3=1

RUN apt-get -qq -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
        gcc \
        g++ \
        wget \
        curl \
        git \
        make \
        sudo \
        bash-completion \
        tree \
        vim \
        software-properties-common \
        python3.10-venv

RUN apt-get -qq -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
        cmake
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y install default-jre python3.10 python3-pip
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y install docker.io

RUN python3 -m pip install --upgrade pip
RUN pip3 install entrezpy
# Create user with sudo powers
RUN useradd -m greg && \
    usermod -aG sudo greg && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    cp /root/.bashrc /home/greg/ && \
    chown -R --from=root greg /home/greg

# Use C.UTF-8 locale to avoid issues with ASCII encoding
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV HOME /home/greg
ENV USER greg
USER greg

# Avoid first use of sudo warning. c.f. https://askubuntu.com/a/22614/781671
RUN touch $HOME/.sudo_as_admin_successful

WORKDIR /home/greg
ADD . .
RUN sudo chown -R greg .