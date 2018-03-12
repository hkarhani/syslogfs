FROM hkarhani/jccp

ADD syslogfs.py /
ADD fsconfig.yml / 
ADD pyFS.py / 

EXPOSE 514:514/udp

CMD [ "python", "./syslogfs.py" ]