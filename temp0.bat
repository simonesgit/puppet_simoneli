@echo off

REM Set the command to your_installation.exe and specify the output file
set "command=your_installation.exe"
set "output_file=output.txt"

REM Start the process and redirect the output to a temporary file
start /B "" cmd /C "%command% > %output_file% 2>&1"
set "pid="

REM Set the timeout value and process running flag
set timeout=300
set process_running=1

REM Loop until the process has started and obtain its PID
:GET_PID
for /f "tokens=2" %%P in ('TASKLIST /NH /FI "IMAGENAME eq %command%" /FO CSV') do (
    set "pid=%%~P"
    goto CHECK_PROCESS
)

REM Delay for 1 second and retry obtaining the process PID
timeout /T 1 > nul
set /a timeout-=1
if %timeout% gtr 0 goto GET_PID

REM Clean up if the process didn't start within the timeout period
echo Process start timeout. Exiting...
goto CLEANUP

:CHECK_PROCESS
REM Print the output file contents
type "%output_file%"

REM Check if the process has ended
TASKLIST /NH /FI "PID eq %pid%" 2>nul | find /i "%pid%" >nul
if %errorlevel% neq 0 (
    echo Process with PID %pid% has ended.
    goto CLEANUP
)

REM Decrement the timeout value
set /a timeout-=1

REM Check if the timeout has expired
if %timeout% LEQ 0 (
    taskkill /PID %pid% /F > nul
    echo Timeout reached. Exiting...
    goto CLEANUP
)

REM Wait for 1 second
timeout /T 1 > nul
goto CHECK_PROCESS

:CLEANUP
REM Delete the temporary output file
del "%output_file%" > nul

REM Add any necessary cleanup or error handling code here
REM ...

exit /b
