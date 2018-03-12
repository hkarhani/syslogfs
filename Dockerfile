FROM hkarhani/jccp

ADD syslogfs.py /
ADD fsconfig.yml / 
ADD pyFS.py / 

EXPOSE 514 

CMD [ "python", "./syslogfs.py" ]