help_str='''
A script to determine previous payouts to create the historical_payments file 

By Sohrab Towfighi BASc MD 2025

Licence: GPL v3.0

'''
from pySched import get_payment, evaluate_soln_payment
import pdb 
import argparse 
import os 
import pandas 

def load_schedule(path):
    loaded_schedule = pandas.read_excel(path)
    loaded_schedule = loaded_schedule.values
    dates = loaded_schedule[:,0]
    names_array = loaded_schedule[:,1:3]
    return names_array, dates

# REPLACE THE NAMES WITH REAL NAMES OF GROUP MEMBERS  
full_names = ["Barney Gumble", "Rolls Royce" , "Homer Simpson", "Lisa Simpson",
                "Bart Simpson", "Maggie Simpson", "Nelson J", "Suis Bronchus", "Morgan Freeman",
                "JD Vance", "Paul McCartney", "Baby Yoda", "Freeman Lorban"] 
#                
                
full_names.sort()
historical_payments_dict = dict()
for name in full_names:
    historical_payments_dict[name] = 0

if __name__ == '__main__':        
    parser = argparse.ArgumentParser(prog='pyEvalSched.py', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument("-t", help="An absolute filepath to the xlsx file.", required=True)
    arguments = parser.parse_args()
    template = arguments.t
    names_array, dates = load_schedule(template)

    payments = evaluate_soln_payment(names_array, [], full_names, dates, historical_payments_dict)
    for i in range(0,len(full_names)):
        name = full_names[i]
        payment = payments[i]
        print(name, payment)
        
    
    

