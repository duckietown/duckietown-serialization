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

RUN pip3 install -U pip>=20.2
COPY requirements.* ./
RUN cat requirements.* > .requirements.txt
RUN  pip3 install --use-feature=2020-resolver -r .requirements.txt




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

RUN pip install .

ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

#ENTRYPOINT ["dts"]
