# pySched
A code used to schedule radiology residents for contrast reaction coverage

# example usage
python .\pyEvalSched.py -t "C:\Users\sohra\Downloads\pySched\template\AllShiftsTillBlock11.xlsx"

Baby Yoda 13820

Barney Gumble 23815

Bart Simpson 46705

Freeman Lorban 7485
Homer Simpson 0
JD Vance 19025
Lisa Simpson 0
Maggie Simpson 0
Morgan Freeman 23735
Nelson J 16770
Paul McCartney 2185
Rolls Royce 0
Suis Bronchus 23195

You use the above numbers to create the historical_payments.csv

python .\pySched.py -h 

python .\pySched.py -t "C:\Users\sohra\Downloads\pySched\template\template_call_schedule.xlsx" -f "C:\Users\sohra\Downloads\pySched\roster" -z 10000 -a 1 -n "C:\Users\sohra\Downloads\pySched\template\historical_payments.csv" -o ./output.xlsx
