@echo off
echo Resetting PostgreSQL password for user 'postgres' to '1234'...
echo.

"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "ALTER USER postgres WITH PASSWORD '1234';"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Password has been reset to: 1234
    echo.
) else (
    echo.
    echo FAILED! You may need to enter the current password when prompted.
    echo Or run this as Administrator.
    echo.
)

pause
