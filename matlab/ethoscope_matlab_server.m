%  This is a matlab server to control the backlight controller from the
%  server node
% Sever should receive a message in this format
% data_time_machineName_signal
% example: 
% OFF signal: 190614_223000_ETHOSCOPE_002_False 
% ON signal: 190614_210000_ETHOSCOPE_002_True

%  author: Salma Elmalaki

while 1
    try
            disp('Connecting ... ')
            t = tcpip('0.0.0.0', 9998, 'NetworkRole', 'Server');
            fopen(t);
            disp('started')
            while t.BytesAvailable  == 0
                pause(1)
                disp('wait');
            end
            data = fread(t,t.BytesAvailable, 'char');
            %data = strjoin(string(data), '')
            data = convertCharstoStrings(char(data))
    catch ex
            disp(ex.message)
            disp('Exception - Light Controller Server is Down!')
            fclose(t);
            delete(t)
            clear t
    end
end




