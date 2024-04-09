FROM nvidia/cuda:11.8.0-base-ubuntu20.04

RUN apt-get update

USER root

RUN apt-get install -y wget git git-lfs unzip xz-utils vim libglu1-mesa-dev libxrender1 libxxf86vm-dev libxfixes-dev libxi6 libxkbcommon-x11-0 libsm6 

# Install and set up conda
RUN mkdir -p ~/miniconda3
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
RUN bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
RUN rm -rf ~/miniconda3/miniconda.sh

RUN ~/miniconda3/bin/conda init bash
RUN ~/miniconda3/bin/conda init zsh

RUN . ~/.bashrc
RUN . /root/miniconda3/etc/profile.d/conda.sh

RUN export PATH="/root/miniconda3/bin:$PATH"

RUN /root/miniconda3/bin/conda create -y -n mgpt python=3.10 
RUN cd /home

# RUN mkdir /home/MotionGPT
RUN mkdir /home/motiongpt_output

COPY . /home/
RUN unzip /home/MotionGPT.zip -d /home
# RUN git clone https://github.com/tamirtbd/MotionGPT.git /home/MotionGPT

WORKDIR /home/MotionGPT
RUN git pull

RUN /root/miniconda3/envs/mgpt/bin/pip install -r /home/MotionGPT/requirements.txt
RUN /root/miniconda3/envs/mgpt/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN /root/miniconda3/envs/mgpt/bin/pip install gdown flask flasgger bert-score==0.3.13

RUN tar -xJvf /home/blender-4.1.0-linux-x64.tar.xz -C /home

EXPOSE 8089/TCP

CMD [ "/root/miniconda3/envs/mgpt/bin/python", "/home/MotionGPT/simple_app.py" ]