FROM amazonlinux:1

# workdir
WORKDIR /

# update 
RUN yum update -y
# Install libraries
RUN yum install gcc openssl-devel mesa-libGL wget tar -y

# download python
RUN wget https://www.python.org/ftp/python/3.8.19/Python-3.8.19.tgz
RUN tar -xzvf Python-3.8.19.tgz

# change workdir
WORKDIR /Python-3.8.19

# install python
RUN ./configure --enable-optimizations
RUN make install

# install python packages
RUN mkdir /packages
# wirte cv2 to reuqirements.txt
RUN echo "opencv-python-headless" >> /packages/requirements.txt
RUN mkdir -p /packages/opencv-python-3.8/python/lib/python3.8/site-packages
RUN python3.8 -m pip install -r /packages/requirements.txt -t /packages/opencv-python-3.8/python/lib/python3.8/site-packages
