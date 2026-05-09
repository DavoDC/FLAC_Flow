@echo off
echo ================================
echo  Deploy Test Data to Input
echo ================================
echo.
echo Resetting input folder to gold standard "before" state...
echo.

set ROOT=%~dp0..
set INPUT=%ROOT%\data\input
set BEFORE=%ROOT%\data\test_data\before_and_after
set SAMPLES=%ROOT%\data\test_data

echo [1/2] Copying gold standard FLAC (with embedded art + padding)...
xcopy /E /Y /I "%BEFORE%\(2020) The Difference [WEB] - Embedded album art and padding" "%INPUT%\(2020) The Difference [WEB] - Embedded album art and padding"

echo.
echo [2/2] Copying sample FLACs to input\Samples...
if not exist "%INPUT%\Samples" mkdir "%INPUT%\Samples"
copy /Y "%SAMPLES%\sample1.flac" "%INPUT%\Samples\"
copy /Y "%SAMPLES%\sample2.flac" "%INPUT%\Samples\"
copy /Y "%SAMPLES%\sample3.flac" "%INPUT%\Samples\"

echo.
echo Done. Input folder is ready - run scripts\run.bat to test.
echo.
cmd /k
