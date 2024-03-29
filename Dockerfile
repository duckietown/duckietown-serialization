FROM docker:18-dind

WORKDIR /project


RUN apk --update --no-cache add \
	python2 \
	python2-dev \
	py-pip \
	bash \
	git \
	gcc \
	musl-dev \
	linux-headers && apk del python2-dev gcc musl-dev linux-headers

RUN python3 -m pip install -U "pip>=21"
COPY requirements.* ./
RUN cat requirements.* > .requirements.txt
RUN python3 -m pip install  -r .requirements.txt




# copy the rest
COPY . .

#   Note the contents of .dockerignore:
#
#     **
#     !requirements.txt
#     !lib
#     !setup.py
#     !README.md
#
#   That's all we need - do not risk including spurious files.


# Install the package using '--no-deps': you want to pin everything
# using requirements.txt
# So, we want this to fail if we forgot anything.
#RUN pip install --prefix /usr --no-deps .

COPY . .

RUN python3 -m pip install .

ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

#ENTRYPOINT ["dts"]
