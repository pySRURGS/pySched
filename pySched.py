help_str='''
A script to automate scheduling of residents 

By Sohrab Towfighi BASc MD 2025

Licence: GPL v3.0

The template file is assumed to be a submission excel file for someone who is 
available for all the shifts.
'''

import csv
import pandas
import argparse
import pdb
import sys
import os
import numpy as np
import random 
import time
from prettytable import PrettyTable

random.seed(time.time())

def is_date_on_weekend(mydate):
    if mydate.weekday() >= 5: 
        return True
    else:
        return False
        
def load_call_request(path):
    loaded_schedule = pandas.read_excel(path)    
    loaded_schedule = loaded_schedule.values
    first_name = loaded_schedule[0,1].strip()
    if loaded_schedule[0,0] != 'First Name:':
        print("Error encountered when dealing with " + path)
        raise Exception("The text 'First Name:' is not at the 2nd row as expected")
    last_name = loaded_schedule[1,1].strip()
    if loaded_schedule[1,0] != 'Last Name:':
        print("Error encountered when dealing with " + path)
        raise Exception("The text 'Last Name:' is not at the 3rd row as expected")
    full_name = first_name + ' ' + last_name
    num_rows_in_xlsx_to_skip = 9
    loaded_schedule = loaded_schedule[num_rows_in_xlsx_to_skip:,:]
    first_name = loaded_schedule[0][1]
    date_str = loaded_schedule[0][0]
    dates = loaded_schedule[1:-1,0]
    end_of_blk_str = loaded_schedule[-1][0]
    loaded_schedule = loaded_schedule[1:-1,1:]
    if date_str == "Date" and end_of_blk_str == 'END OF BLOCK':
        pass
    else:
        print("############################################")
        print("Error encountered when dealing with " + path)
        print("############################################")
        raise Exception("The structure of the excel spreadsheet has been modified such that the 'Date' string and/or the 'END OF BLOCK' string are no longer in the expected location.")
    return loaded_schedule, full_name, dates


def format_datetime(mydate):
    return mydate.strftime("%B %d, %Y")

    
def get_availability_BCCA(schedule):    
    twos = schedule == 2
    return twos
    
    
def create_the_list_of_available_workers(template, list_of_availabilities):
    shifts_needing_to_be_filled = np.copy(get_availability_BCCA(template))
    shifts_needing_to_be_filled = shifts_needing_to_be_filled.astype('object')
    # iterate through the available workers and wherever there is True, change it 
    # to a list
    for i in range(0,shifts_needing_to_be_filled.shape[0]):
        for j in range(0,shifts_needing_to_be_filled.shape[1]):
            if shifts_needing_to_be_filled[i][j] == True:
                shifts_needing_to_be_filled[i][j] = []
            else: 
                shifts_needing_to_be_filled[i][j] = "N/A"
    # iterate through the shifts needing to be filled and wherever there is 
    # list, change it to a list containing the names of all available workers
    for i in range(0, shifts_needing_to_be_filled.shape[0]):
        for j in range(0, shifts_needing_to_be_filled.shape[1]):
            if isinstance(shifts_needing_to_be_filled[i][j], list):
                for z in list_of_availabilities:
                    availability = z[0]
                    full_name = z[1]
                    if availability[i][j] == True:
                        shifts_needing_to_be_filled[i][j].append(full_name)
    available_workers = shifts_needing_to_be_filled
    return available_workers

    
def randomly_choose_a_solution(template, available_workers, dates):
    soln = np.copy(template)
    cp_aw = np.copy(available_workers)
    template_availability = get_availability_BCCA(template)
    for day in range(0, template_availability.shape[0]):
        for shift in range(0, template_availability.shape[1]):
            if isinstance(cp_aw[day][shift], list):
                pass
            else:
                continue
            num_available = len(cp_aw[day][shift])            
            if num_available == 0:                
                date = dates[day]
                if shift == 0:
                    shift_type = "MRI"
                elif shift == 1:
                    shift_type = "CT"
                else: 
                    raise Exception("Invalid shift")                
                raise Exception("No one is available to work on day corresponding to " + str(date) + " " + str(shift))
            which_random = random.randint(0, num_available-1)
            person_selected = cp_aw[day][shift][which_random]
            soln[day][shift] = person_selected
            # if the person selected for CT is the same as MR/PET, repeat the 
            # process until you pick someone else
            if shift == 1: # if we are considering the CT shift
                check_no_double_ups = False
                iter = 0
                already_assigned = []
                for i in range(0, shift):
                    already_assigned.append(soln[day][i])    
                while check_no_double_ups == False:     
                    if soln[day][shift] in already_assigned: # if there is a double up 
                        which_random = random.randint(0, num_available-1)
                        person_selected = cp_aw[day][shift][which_random]
                        soln[day][shift] = person_selected
                    else:
                        check_no_double_ups = True # no double up, therefore can break 
                    iter = iter + 1 
                    if iter == 100: # sometimes we are forced to double up
                        check_no_double_ups = True
                        
            if shift == 2: # if we are considering BCCH MRI shift
                check_no_double_ups = False
                iter = 0
                already_assigned = []
                for i in range(0, shift):
                    already_assigned.append(soln[day][i])  
                while check_no_double_ups == False:
                    if soln[day][shift] in already_assigned: # if there is a double up 
                        which_random = random.randint(0, num_available-1)
                        person_selected = cp_aw[day][shift][which_random]
                        soln[day][shift] = person_selected
                    else:
                        check_no_double_ups = True # no double up, therefore can break 
                    iter = iter + 1 
                    if iter == 100: # sometimes we are forced to double up, but this is not possible for BCCH given different facility 
                        raise Exception("No one is available to work on day corresponding to " + str(date) + " " + str(shift))
    return soln

def get_payment(soln, name, dates, historical_payments_dict):
    # this function figures out how much a person gets paid over the schedule 
    payment = 0 
    for day in range(0, soln.shape[0]):
        for shift in range(0, soln.shape[1]):
            if name == soln[day][shift]:
                weekday_code = dates[day].weekday()
                if weekday_code < 5: # weekday
                    if shift == 0: # MRI
                        payment = payment + 340                        
                    elif shift == 1: # CT 
                        if soln[day][0] == name: 
                            payment = payment + 100 # if doubling up on MR and CT weekday
                        else:
                            payment = payment + 320 
                    elif shift == 2: # BCCH MRI
                        payment = payment + 270
                    else:
                        raise Exception("Invalid shift type: " + str(shift))                    
                else:
                    # weekend
                    if shift == 0: # MRI
                        if weekday_code == 5: # Saturday
                            payment = payment + 845
                        elif weekday_code == 6: # Sunday
                            payment = payment + 780
                    elif shift == 1: # CT
                        if soln[day][0] == name: 
                            payment = payment + 200
                        else:
                            payment = payment + 480                        
                    else:
                        raise Exception("Invalid shift type: " + str(shift))
    try:
        payment = payment + historical_payments_dict[name]
    except Exception as A:
        print(A)
        pdb.set_trace()
    return payment

def evaluate_soln_payment(soln, availabilities, names, dates, historical_payments_dict):
    payments = []
    for full_name in names:
        payment = get_payment(soln, full_name, dates, historical_payments_dict)                
        payments.append(payment)
    return payments    

def get_duration(soln, name, dates):
    duration = 0
    # The following code weights shifts according to their duration
    for day in range(0, soln.shape[0]):
        for shift in range(0, soln.shape[1]):
            if name == soln[day][shift]:
                if dates[day].weekday() < 5:
                    duration = duration + 5
                else:
                    # weekend
                    if shift == 0: # MRI
                        duration = duration + 13
                    elif shift == 1: # CT
                        duration = duration + 8
                    else:
                        raise Exception("Invalid shift type: " + str(shift))
    return duration

def evaluate_soln_duration(soln, availabilities, names, dates):
    durations = []
    for full_name in names:
        duration = get_duration(soln, full_name, dates)
        durations.append(duration)
    return durations

def get_num_shifts(soln, name):
    bool_count = (soln == name)        
    num_shifts = np.sum(bool_count)
    return num_shifts
    
def evaluate_soln_num_shifts(soln, availabilities, names, dates):
    list_num_shifts = []
    for full_name in names:
        num_shifts = get_num_shifts(soln, full_name)
        list_num_shifts.append(num_shifts)
    return list_num_shifts

def get_soln_offered_shift_to_available_shifts(soln, list_availabilities, name, dates):
    bool_count = (soln == name)        
    num_shifts = get_num_shifts(soln, name)
    num_shifts_available = 0
    # The following code calculates the number of shifts the resident offered
    name_iter = "N/A"
    for i in range(0, len(list_availabilities)):
        if name == list_availabilities[i][1]:            
            name_iter = i
            break
    if name_iter == "N/A":
        num_shifts_available = 0
        return num_shifts, num_shifts_available
    bool_count = list_availabilities[name_iter][0]
    num_shifts_available = np.sum(bool_count)
    return num_shifts, num_shifts_available

def evaluate_soln_offered_shift_to_available_shifts(soln, list_availabilities, names, dates):
    offered_shift_to_available_shifts = []
    for full_name in names: 
        num_shifts, num_shifts_available = get_soln_offered_shift_to_available_shifts(soln, list_availabilities, full_name, dates)
        offered_shift_to_available_shifts.append(num_shifts/num_shifts_available)     
    return offered_shift_to_available_shifts
    
def evaluate_soln(soln, availabilities, names, dates, historical_payments_dict, 
                  list_availabilities, report=False, mode="payment"):
    '''
    This function is the goal function which we seek to minimize
    If set to offered_shift_to_available_shifts, it will give preferential treatment 
    to residents providing larger volume of coverage. 
    If set to num_shifts, it will give equal preference to all residents. 
    
    availabilities and list_availabilities have the same data, but in a different format, 
    for convenience of passing this info around.
    
    mode is in ["payment", "duration", "num_shifts", "offered_shift_to_available_shifts"]
    '''
    if mode not in ["payment", "duration", "num_shifts", "offered_shift_to_available_shifts"]:
        raise Exception("Invalid mode: " + str(mode))
    if mode == 'payment':
        metric = evaluate_soln_payment(soln, availabilities, names, dates, historical_payments_dict)
    elif mode == 'duration':
        metric = evaluate_soln_duration(soln, availabilities, names, dates)
    elif mode == 'num_shifts':
        metric = evaluate_soln_num_shifts(soln, availabilities, names, dates)
    elif mode == 'offered_shift_to_available_shifts':
        metric = evaluate_soln_offered_shift_to_available_shifts(soln, availabilities, names, dates)
    
    if report == True:
        payments = evaluate_soln_payment(soln, availabilities, names, dates, historical_payments_dict)
        durations = evaluate_soln_duration(soln, availabilities, names, dates)
        list_num_shifts = evaluate_soln_num_shifts(soln, availabilities, names, dates)
        offered_shift_to_available_shifts = evaluate_soln_offered_shift_to_available_shifts(soln, 
                                                                           list_availabilities, names, dates)        
        #t = PrettyTable(['Name', 'prior payments ($)', 'payment ($)', 'hours', 'shifts', 'ratio shifts to availability'])
        t = PrettyTable(['Name', 'prior payments ($)', 'this payment ($)', 'hours', 'shifts', 'ratio shifts to availability'])
        for i in range(0,len(names)):
            full_name = names[i]
            prior_payment = int(historical_payments_dict[full_name])
            payment = payments[i] - prior_payment
            duration = durations[i]
            num_shifts = list_num_shifts[i]
            offered_shift_to_available = '{0:.2f}'.format(offered_shift_to_available_shifts[i])
            t.add_row([full_name, prior_payment, payment, duration, num_shifts, offered_shift_to_available])
            #t.add_row([full_name, payment, duration, num_shifts, offered_shift_to_available])
        for key,value in historical_payments_dict.items():
            if key not in names:
                prior_payment = int(historical_payments_dict[key])
                payment = get_payment(soln, key, dates, historical_payments_dict) - prior_payment
                duration = get_duration(soln, key, dates)
                num_shifts = get_num_shifts(soln, key)
                _, offered_shift_to_available = get_soln_offered_shift_to_available_shifts(soln, availabilities, 
                                                                                        key, dates)
                t.add_row([key, prior_payment, payment, duration, num_shifts, offered_shift_to_available])
                #t.add_row([key, payment, duration, num_shifts, offered_shift_to_available])
        print(t)
        t.del_column('hours')
        t.del_column('shifts')
        t.del_column('ratio shifts to availability')
        print(t.get_csv_string(sortby='Name'))        
    return np.std(metric)

def csv_to_dict(filepath):
    reader = csv.reader(open(filepath, 'r'))
    d = {}
    for row in reader:
       k, v = row
       v = v.strip()
       v = int(v)
       d[k] = v
    return d
    
def generate_schedule(template_filepath, folder, output, historical_payments, num_iters=5000, max_runtime_seconds=60):    
    template, _, dates = load_call_request(template_filepath)
    # load all the call submission requests 
    list_of_call_requests = []
    list_of_availabilities = []
    call_request_filenames = os.listdir(folder)
    names = []
    historical_payments_dict = csv_to_dict(historical_payments)
    for file in call_request_filenames:
        try:
            submitted_availability, full_name, _ = load_call_request(os.path.join(folder, file))
        except ValueError:        
            print(file)
            pdb.set_trace()
        names.append(full_name)
        formatted_availability = get_availability_BCCA(submitted_availability)        
        list_of_availabilities.append([formatted_availability, full_name])
    available_workers = create_the_list_of_available_workers(template, list_of_availabilities)
    best_soln = randomly_choose_a_solution(template, available_workers, dates)
    best_metric = evaluate_soln(best_soln, available_workers, names, dates, historical_payments_dict,
                                list_of_availabilities)
    print("The value of the metric being minimized:")
    base_time = time.time()
    iterations_completed = 0
    for i in range(0, num_iters):
        soln = randomly_choose_a_solution(template, available_workers, dates)
        metric = evaluate_soln(soln, available_workers, names, dates, historical_payments_dict, 
                               list_of_availabilities)
        run_time = time.time() - base_time        
        if metric < best_metric:
            best_metric = metric
            best_soln = np.copy(soln)
            print("Iteration count, Metric being optimized: " + str(i) + ', ' + str(best_metric))
        if max_runtime_seconds < run_time:
            break
        iterations_completed = i
    print("Finished " + str(iterations_completed ) + " iterations. Compiling metrics:")
    print("Best value of the metric: " + str(best_metric))
    evaluate_soln(best_soln, available_workers, names, dates, historical_payments_dict, list_of_availabilities, True)
    best_soln = best_soln.tolist()
    for i in range(0,len(best_soln)):
        best_soln[i].insert(0, dates[i].strftime('%A-%Y-%m-%d'))
    df = pandas.DataFrame(best_soln)
    df.to_excel(index=False, header=None, excel_writer = output)
    

if __name__ == '__main__':        
    parser = argparse.ArgumentParser(prog='pySched.py', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument("-t", help="An absolute filepath to the template xlsx file.", required=True)
    required.add_argument("-f", help="An absolute path to the directory where all the filled in call request forms reside.", required=True)
    required.add_argument("-z", help="An integer specifying the number of iterations to perform.", required=True)
    required.add_argument("-a", help="An integer denoting maximum runtime in minutes. This time value overrules number of iterations.", required=True)
    required.add_argument("-n", help="An absolute filepath to the historical payments csv file.", required=True)
    required.add_argument("-o", help="An absolute filepath to the output xlsx file.", required=True)
    if len(sys.argv) == 0:
        parser.print_usage()
        sys.exit(1)    
    arguments = parser.parse_args()
    template = arguments.t
    num_iters = int(arguments.z)
    max_runtime_seconds = int(arguments.a)*60
    folder = arguments.f
    output = arguments.o
    historical_payments = arguments.n
    generate_schedule(template, folder, output, historical_payments, num_iters, max_runtime_seconds)