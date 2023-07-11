@echo off

REM Loop until interrupted
:LOOP
REM Get the current datetime
set current_datetime=%DATE% %TIME%

REM Output the current datetime
echo %current_datetime%

REM Ping the local machine
ping 127.0.0.1 -n 1 > nul

REM Go back to the LOOP
goto LOOP
