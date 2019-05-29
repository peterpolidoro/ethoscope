% light_controller_server
% The server receives a message in the form of: id_%y%m%d_%H%M%S
% Example:  “ETHOSCOPE_002_190529_190946”
% id:  ETHOSCOPE_002
% y: 19
% m:05
% d:29
% H:19
% M:09
% S:46
% When the tracking starts, a python client generates a message and sends it to the matlab server
try
    disp('started')
    t = tcpip('0.0.0.0', 9998, 'NetworkRole', 'server');
    fopen(t);
    while t.BytesAvailable == 0
        pause(1)
        disp('wait');
    end
    data = char(fread(t,t.BytesAvailable));
    data = strjoin(string(data),'')
    fclose(t);
catch
    disp('Exception');
    fclose(t);
end

