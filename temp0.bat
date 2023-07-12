@echo off

REM Set the command to your_installation.exe and specify the output file
set "command=your_installation.exe"
set "output_file=output.txt"

REM Start the process and redirect the output to a temporary file
start /B cmd /C "%command% > %output_file% 2>&1"
set "pid="

REM Set the timeout value and process running flag
set timeout=300
set process_running=1

REM Monitor the process and get the process ID
:CHECK_PROCESS
for /f "tokens=2 delims==; " %%P in ('wmic process where "CommandLine like '%%cmd /C %command%%%'" get ProcessId /value') do set "pid=%%P"
if "%pid%"=="" (
    set process_running=0
    goto PROCESS_ENDED
)

REM Decrement the timeout value
set /a timeout-=1

REM Check if the timeout has expired
if %timeout% LEQ 0 (
    taskkill /PID %pid% /F > nul
    goto TIMEOUT_REACHED
)

REM Wait for 1 second
timeout /T 1 /NOBREAK > nul
goto CHECK_PROCESS

:PROCESS_ENDED
REM Print the output file contents
type "%output_file%"
echo Process has ended.
goto CLEANUP

:TIMEOUT_REACHED
REM Print the output file contents
type "%output_file%"
echo Timeout reached. Exiting...
goto CLEANUP

:CLEANUP
REM Delete the temporary output file 
del "%output_file%" > nul

REM Add any necessary cleanup or error handling code here
REM ...

exit /b
