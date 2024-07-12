Start-Job -ScriptBlock { python main.py }
Start-Job -ScriptBlock { python main.py }

Get-Job | Wait-Job

# How to run:
# ./runScipts.ps1