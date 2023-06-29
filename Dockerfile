FROM ubuntu:jammy

RUN apt update \
  && apt install -y --no-install-recommends \
  git \
  openjdk-11-jdk \
  && rm -rf /var/lib/apt/lists/*

RUN cd /tmp \
  && git clone --recursive -b v2.5.1 https://github.com/eProsima/Fast-DDS-Gen.git \
  && cd Fast-DDS-Gen \
  && ./gradlew assemble install --install_path=/tmp/Fast-DDS-Gen/install

FROM ubuntu:jammy

RUN apt update \
  && apt install -y --no-install-recommends \
  python3 \
  python3-pip\
  openjdk-11-jre-headless \
  && rm -rf /var/lib/apt/lists/*

COPY --from=0 /tmp/Fast-DDS-Gen/install /usr/local
COPY . /tmp/msg2fastdds

RUN cd /tmp/msg2fastdds \
  && pip3 install . \
  && cd .. \
  && rm -rf msg2fastdds

CMD [ "msg2fastdds", "/msg2fastdds/package_dir", "/msg2fastdds/output_dir" ]
