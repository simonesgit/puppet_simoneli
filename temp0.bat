@echo off

REM Set the command to your_installation.exe and specify the output file
set "command=your_installation.exe"
set "command=temp0.bat"
set "output_file=output.txt"

REM Start the process and redirect the output to a temporary file
start /B cmd /C "%command% > %output_file% 2>&1"

REM Set the timeout value and process running flag
set timeout=300
set process_running=1

REM Monitor the process
:CHECK_PROCESS
tasklist /FI "WINDOWTITLE eq %command%" | find ":" > nul
if errorlevel 1 (
    set process_running=0
    goto PROCESS_ENDED
)

REM Print the output file contents
type "%output_file%"

REM Decrement the timeout value
set /a timeout-=1

REM Check if the timeout has expired
if %timeout% LEQ 0 (
    goto TIMEOUT_REACHED
)

REM Wait for 1 second
timeout /T 1 /NOBREAK > nul
goto CHECK_PROCESS

:PROCESS_ENDED
echo Process has ended.
goto CLEANUP

:TIMEOUT_REACHED
echo Timeout reached. Exiting...
goto CLEANUP

:CLEANUP
REM Delete the temporary output file
del "%output_file%" > nul

REM Add any necessary cleanup or error handling code here
REM ...

exit /b
