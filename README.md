# pySched
A code used to schedule radiology residents for contrast reaction coverage. You run it in powershell.

# example usage
python .\pyEvalSched.py -t "C:\Users\sohra\Downloads\pySched\template\AllShiftsTillBlock11.xlsx"

the above script generates data useful to create the historical_payments.csv

To get the help manual page, use
python .\pySched.py -h 


Example 
python .\pySched.py -t "C:\Users\sohra\Downloads\pySched\template\template_call_schedule.xlsx" -f "C:\Users\sohra\Downloads\pySched\roster" -z 10000 -a 1 -n "C:\Users\sohra\Downloads\pySched\template\historical_payments.csv" -o ./output.xlsx
