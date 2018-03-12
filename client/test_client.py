import syslog_client

log = syslog_client.Syslog(host="10.0.1.1",port=514)

msg1 = "<134>1 2018-03-11T08:02:22.00Z-04:00 10.0.1.20 - - - Mar 11 2018 08:02:22,Traps Agent,4.1.3.33176,Threat,Prevention Event,w10,W10\Demo,New prevention event. Prevention Key: cc9cc24e-06a9-4e72-905f-1e76df05e859,9,WildFire,wildfire-test-pe-file.exe,0a752ca47654a3e8ccd2babedecc6e7c7dbd52acbb0f0177e2efe8bf3678414c,36-2416,10.0.1.51,,Mar 11 2018 08:02:22,"
msg2 = "<134>1 2018-03-11T08:02:22.00Z-04:00 10.0.1.20 - - - Mar 11 2018 08:02:22,Traps Agent,4.1.3.33176,Threat,Prevention Event,w10,W10\Demo,New prevention event. Prevention Key: cc9cc24e-06a9-4e72-905f-1e76df05e859,9,WildFire,wildfire-test-pe-file1.exe,0a752ca47654a3e8ccd2babedecc6e7c7dbd52acbb0f0177e2efe8bf3678414c,36-2416,10.0.1.54,,Mar 11 2018 08:02:22,"
msg3 = "<134>1 2018-03-11T08:02:22.00Z-04:00 10.0.1.20 - - - Mar 11 2018 08:02:22,Traps Agent,4.1.3.33176,Threat,Prevention Event,w10,W10\Demo,New prevention event. Prevention Key: cc9cc24e-06a9-4e72-905f-1e76df05e859,9,WildFire,wildfire-test-pe-file2.exe,0a752ca47654a3e8ccd2babedecc6e7c7dbd52acbb0f0177e2efe8bf3678414c,36-2416,10.0.1.58,,Mar 11 2018 08:02:22,"
msgs = [msg1, msg2, msg3]
for _msg in msgs: 
    log.send(_msg, syslog_client.Level.WARNING)