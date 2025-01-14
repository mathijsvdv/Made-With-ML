FROM rayproject/ray:2.6.3-py310-cu118

COPY requirements.txt ./

COPY install-docker-requirements.sh ./

# Install dependencies
RUN sudo chmod +x install-docker-requirements.sh && ./install-docker-requirements.sh

# Export installed packages
RUN $HOME/anaconda3/bin/pip freeze > /home/ray/pip-freeze.txt
