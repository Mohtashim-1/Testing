# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe import msgprint, _
from datetime import datetime
from datetime import timedelta
from datetime import date as dt
import datetime as special
import time
from frappe.utils import cstr, flt,getdate, today, get_time
import calendar
from hrms.hr.utils import get_holidays_for_employee
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.setup.doctype.employee.employee import (
    InactiveEmployeeStatusError
)


class EmployeeAttendance(Document):
    def autoname(self):
        if not self.employee or not self.month:
            frappe.throw("Employee and Month must be set before generating the name.")
        self.name = make_autoname(self.employee + '-' + self.month)

    def validate(self):
        total_early = 0
        total_lates = 0
        total_half_days = 0
        total_hr_worked = timedelta(hours=0, minutes=0, seconds=0)
        total_per_day_h = timedelta(hours=0, minutes=0, seconds=0)
        total_late_hr_worked = timedelta(hours=0, minutes=0, seconds=0)
        total_early_going_hrs= timedelta(hours=0, minutes=0, seconds=0)
        total_late_coming_hours = timedelta(hours=0, minutes=0, seconds=0)
        total_additional_hours = timedelta(hours=0, minutes=0, seconds=0)
        total_early_ot = timedelta(hours=0, minutes=0, seconds=0)
        total_approved_ot = timedelta(hours=0, minutes=0, seconds=0)
        total_approved_early_ot = timedelta(hours=0, minutes=0, seconds=0)
        required_working_hrs = 0.0
        holiday_halfday_ot =0
        holiday_full_day_ot =0
        self.no_of_holiday_night = 0
        self.total_absents = 0
        # self.late_comparision = 0
        self.late_comparision = 0
        extra_ot_amount = 0
        holiday_doc = None
        self.total_public_holidays = 0
        half_day_leave = None
        self.no_of_nights = 0
        total_working_days=0
        self.total_weekly_off = 1
        present_days=0
        accun_holiday=0
        self.total_extra_duty_for_halfday = 0
        self.total_extra_duty_for_fullday = 0
        holidays = []
        hr_settings = frappe.get_single('V HR Settings')
        #try:
        month = self.get_month_no(self.month)
        year = int(self.year)
        _, num_days = calendar.monthrange(year, month)
        first_day = dt(year, month, 1)
        last_day = dt(year, month, num_days)

        if hr_settings.period_from != 1:
            if month == 1:
                temp_month = 12
            else:
                temp_month = month - 1
            first_day = dt(year, temp_month, int(hr_settings.period_from))
            last_day = dt(year, month, int(hr_settings.period_to))
            _, num_days = calendar.monthrange(year, temp_month)
            num_days = num_days - int(hr_settings.period_from) + int(hr_settings.period_to) + 1

        holidays = get_holidays_for_employee(self.employee,first_day,last_day)
        self.total_working_days = num_days -len(holidays)
        self.no_of_sundays = 0
        self.month_days = num_days
        # except:
        #     pass
        holiday_flag = False
        leave_flag = False
        total_holiday_hours = timedelta(hours=0,minutes=0,seconds=0)
        previous = None
        index = 0
        total_seconds1 = 0
        total_seconds2 = 0
        total_seconds3 = 0
        total_seconds_approved_eot = 0
        total_seconds_approved_ot1 = 0
        total_seconds_approved_ot2 = 0
        time_seconds_approved_eot1 = 0

        if self.table1:
            first_date = self.table1[0].date  
            last_date = self.table1[-1].date  

            # Fetch fuel rate
            fuel = frappe.get_list("Fuel Rate", filters={
                "from_date": [">=", first_date],
                "to_date": ["<=", last_date]
            }, fields=['*'])

            if fuel and fuel[0]:
                fuel_allowed = fuel[0].rate_per_litre  
                self.fuel_allowance_rate = fuel_allowed
                if self.fuel_allowance_rate and self.fuel_allowance_limit:
                    self.fuel_allowance_total = self.fuel_allowance_rate * self.fuel_allowance_limit
                else:
                    self.fuel_allowance_total = 0
            else:
                self.fuel_allowance_rate = "0" 

        # Loop through table1 rows
        for data in self.table1:
            # Sum early_ot
            if data.early_ot:
                try:
                    time_parts = [int(part) for part in data.early_ot.split(':')]
                    if len(time_parts) == 3:
                        time_seconds1 = time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
                        total_seconds1 += time_seconds1
                        print(f"Added {time_seconds1} seconds from {data.early_ot}")
                    else:
                        print(f"Invalid time format in early_ot: {data.early_ot}")
                except ValueError:
                    print(f"Error processing time format in early_ot: {data.early_ot}")
            else:
                print(f"early_ot is None or empty for row")

            # Sum estimated_late
            if data.estimated_late:
                try:
                    time_parts1 = [int(part) for part in data.estimated_late.split(':')]
                    if len(time_parts1) == 3:
                        time_seconds2 = time_parts1[0] * 3600 + time_parts1[1] * 60 + time_parts1[2]
                        total_seconds2 += time_seconds2
                        print(f"Added {time_seconds2} seconds from {data.estimated_late}")
                    else:
                        print(f"Invalid time format in estimated_late: {data.estimated_late}")
                except ValueError:
                    print(f"Error processing time format in estimated_late: {data.estimated_late}")
            else:
                print(f"estimated_late is None or empty for row")

            # Sum estimate_early (fixed variable and print statement)
            if data.estimate_early:
                try:
                    time_parts2 = [int(part) for part in data.estimate_early.split(':')]
                    if len(time_parts2) == 3:
                        time_seconds3 = time_parts2[0] * 3600 + time_parts2[1] * 60 + time_parts2[2]
                        total_seconds3 += time_seconds3
                        print(f"Added {time_seconds3} seconds from {data.estimate_early}")
                    else:
                        print(f"Invalid time format in estimate_early: {data.estimate_early}")
                except ValueError:
                    print(f"Error processing time format in estimate_early: {data.estimate_early}")
            else:
                print(f"estimate_early is None or empty for row")
            
            # Sum approved_eot
            if data.approved_eot:
                try:
                    time_parts = [int(part) for part in data.approved_eot.split(':')]
                    if len(time_parts) == 3:
                        time_seconds_approved_eot = time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
                        total_seconds_approved_eot += time_seconds_approved_eot
                        print(f"Added {time_seconds_approved_eot} seconds from {data.approved_eot}")
                    else:
                        print(f"Invalid time format in approved_eot: {data.approved_eot}")
                except ValueError:
                    print(f"Error processing time format in approved_eot: {data.approved_eot}")
            else:
                print(f"approved_eot is None or empty for row")

            # total of late sitting approved 
            if data.approved_ot1:
                try:
                    time_parts3 = [int(parts) for parts in data.approved_ot1.split(':')]
                    if len(time_parts3) == 3:
                        time_seconds_approved_ot1 = time_parts3[0] * 3600 + time_parts3[1] * 60 + time_parts3[2]
                        total_seconds_approved_ot1 += time_seconds_approved_ot1
                    else:
                        print(f"Invalid time format in approved_ot1 : {data.approved_ot1}")
                except ValueError:
                    print(f"Error processing time format in approved_ot1: {data.approved_ot1}")
            else:
                print(f"approved_ot1 is None or empty for row")
            
            # total of approved early ot 

            if data.approved_eot:
                try:
                    time_parts4 = [int(parts) for parts in data.approved_eot.split(':')]
                    if len(time_parts3) == 3:
                        time_seconds_approved_eot1 = time_parts4[0] * 3600 + time_parts4[1] * 60 + time_parts4[2]
                        total_seconds_approved_eot += time_seconds_approved_eot
                    else:
                        print(f"Invalid time format in approved_eot : {data.approved_eot}")
                except ValueError:
                    print(f"Error processing time format in approved_eot: {data.approved_eot}")
            else:
                print(f"approved_eot is None or empty for row")


        # Calculate total hours after loop
        self.early_ot = "{:.2f}".format(total_seconds1 / 3600.0)
        self.late_sitting = "{:.2f}".format(total_seconds2 / 3600.0)
        self.early_sitting = "{:.2f}".format(total_seconds3 / 3600.0)
        self.approved_early_over_time_hour = "{:.2f}".format(total_seconds_approved_eot / 3600.0)

        print(f"Total seconds accumulated for approved_eot: {total_seconds_approved_eot}")

        # total of late sitting and early sitting 
        total_sitting = float(self.late_sitting) + float(self.early_sitting)
        self.total_sitting = "{:.2f}".format(total_sitting)

        # total of approved ot1
        self.approved_late_sitting =  "{:.2f}".format(total_seconds_approved_ot1 / 3600.0)

        # total of approved_eot 
        self.approved_early_sitting = "{:.2f}".format(time_seconds_approved_eot1 / 3600.0)

        # approved total sitting
        approved_total_sitting = float(self.approved_late_sitting) + float(self.approved_early_sitting)
        self.approved_total_sitting = approved_total_sitting

        for data in self.table1:
            first_in_time = timedelta(hours=1,minutes=0,seconds=0)
            first_out_time = timedelta(hours=1,minutes=0,seconds=0)
            data.late_sitting = None
            data.additional_hours = None
            data.late_coming_hours = None
            data.early_going_hours = None
            data.early = 0
            data.absent = 0
            data.weekly_off = 0
            data.total_ot_amount = 0
            tempdate = data.date
            holiday_flag = False
            
            if getdate(data.date) < getdate(frappe.db.get_value("Employee",self.employee,"date_of_joining")):
                data.absent=1
                self.total_absents+=1
                index+=1
                continue
            if frappe.db.get_value("Employee",self.employee,"relieving_date"):
                if getdate(data.date) > getdate(frappe.db.get_value("Employee",self.employee,"relieving_date")):
                    data.absent=1
                    self.total_absents+=1
                    index+=1
                    continue

            if str(getdate(data.date)) in [str(d.holiday_date) for d in holidays]:
                        holiday_flag = True
                        data.public_holiday = 0
                        data.weekly_off = 0
                        for h in holidays:
                            if str(getdate(data.date)) == str(h.holiday_date):
                                if h.public_holiday == 1:
                                    data.public_holiday = 1
                                    self.total_public_holidays += 1
                                break
                        if data.public_holiday == 0: 
                            data.weekly_off = 1
                            self.total_weekly_off += 1
                        if hr_settings.absent_sandwich in ['Absent Before Holiday']:
                            if previous and previous.absent == 1:
                                p_date = previous.date
                                lv = frappe.get_all("Leave Application", filters={"from_date":["<=",p_date],"to_date":[">=",p_date],"employee":self.employee,"status":"Approved"},fields=["*"])
                                if len(lv) > 0:
                                    pass
                                else:
                                    data.absent=1
                                    self.total_absents+=1
                                    index+=1
                                    continue
          
            
            if not holiday_flag:
                total_working_days+=1
            LA = frappe.get_all("Leave Application", filters={"from_date":["<=",tempdate],"to_date":[">=",tempdate],"employee":self.employee,"status":"Approved"},fields=["*"])
            if len(LA) > 0:
                leave_flag = True
                if LA[0].half_day:
                    half_day_leave = 1
                

           
            try:
                total_time = None
                hrs = timedelta(hours=0, minutes=0, seconds=0)
                s_type =None
                day_data = None
                if not data.check_in_1 and data.check_out_1:
                    data.check_in_1 = hr_settings.auto_fetch_check_in
                if not data.check_out_1 and data.check_in_1:
                    data.check_out_1 = hr_settings.auto_fetch_check_out
                
                if str(data.check_in_1) == str(hr_settings.auto_fetch_check_in):
                    data.check_in_1 = None
                if str(data.check_out_1) == str(hr_settings.auto_fetch_check_out):
                    data.check_out_1 = None
                
                # if data.check_in_1 != None and data.check_out_1 == None and data.date < today():
                #     data.check_out_1 = timedelta(hours=int(str(data.check_in_1).split(":")[0]),
                #                               minutes=int(str(data.check_in_1).split(":")[1])+1)
             
                if data.approved_ot1:
                    total_approved_ot+= timedelta(hours=int(str(data.approved_ot1).split(":")[0]),minutes=int(str(data.approved_ot1).split(":")[1]))
                if data.check_in_1 and data.check_out_1 and data.check_in_1 != data.check_out_1:
                    first_in_time = timedelta(hours=int(str(data.check_in_1).split(":")[0]),
                                              minutes=int(str(data.check_in_1).split(":")[1]))
                    first_out_time = timedelta(hours=int(str(data.check_out_1).split(":")[0]),
                                              minutes=int(str(data.check_out_1).split(":")[1]))
                   
                    diff = str(first_out_time - first_in_time)
                    if "day" in diff:
                        diff = diff.split("day, ")[1].split(":")
                        diff = timedelta(hours=float(diff[0]), minutes=float(
                            diff[1]), seconds=float(diff[2]))
                    else:
                        diff = first_out_time - first_in_time
                    total_time = total_time + diff if total_time else diff
                   
                if data.check_in_1 and data.check_in_1 != data.check_out_1:
                    shift = None
                    shift_ass = frappe.get_all("Shift Assignment", filters={'employee': self.employee,
                                                                            'start_date': ["<=", getdate(data.date)],'end_date': [">=", getdate(data.date)]}, fields=["*"])
                    if len(shift_ass) > 0:
                        shift = shift_ass[0].shift_type
                    else:
                        shift_ass = frappe.get_all("Shift Assignment", filters={'employee': self.employee,
                                                                            'start_date': ["<=", getdate(data.date)]}, fields=["*"])
                    if len(shift_ass) > 0:
                        shift = shift_ass[0].shift_type
                    if shift == None:
                        frappe.throw(_("No shift available for this employee{0}").format(self.employee))
                    data.shift = shift
                    shift_doc = frappe.get_doc("Shift Type", shift)
                    s_type = shift_doc.shift_type
                    data.absent = 0

                    #  day of week 
                
                    date1 = data.date
                    print(f"\n\n\n\\\n\n\n{date1}")
                    dateobj = getdate(date1)
                    day_of_week = dateobj.strftime('%A')
                    data.day = day_of_week
                    print(dateobj)
                   
                    day_name = datetime.strptime(
                        str(data.date), '%Y-%m-%d').strftime('%A')

                    in_diff = first_in_time - shift_doc.start_time
                   
                    day_data = None
                    for day in shift_doc.day:
                        if day_name == day.day:
                            day_data = day
                            break

                    if data.weekly_off == 1 or data.public_holiday == 1:
                        #settings required
                        if total_time:
                            total_holiday_hours += total_time
                            
                    if not day_data:
                        data.difference = total_time
                        check_sanwich_after_holiday(self,previous,data,hr_settings,index)
                        previous = data
                        index+=1
                        if data.absent == 0 and data.check_in_1:
                            if holiday_flag:
                                if hr_settings.count_working_on_holiday_in_present_days == 1:
                                    present_days+=1
                                if total_time:
                                    if total_time >= timedelta(hours=hr_settings.holiday_halfday_ot,minutes=00,seconds=0) and \
                                        total_time < timedelta(hours=hr_settings.holiday_full_day_ot,minutes=00,seconds=0):
                                        holiday_halfday_ot = holiday_halfday_ot + 1
                                    elif total_time >= timedelta(hours=hr_settings.holiday_full_day_ot,minutes=00,seconds=0):
                                        holiday_full_day_ot = holiday_full_day_ot + 1
                                    if total_time >= timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0):
                                        data.late_sitting = timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0) + timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0)
                                        total_late_hr_worked += data.late_sitting
                                        #total_holiday_hours += total_time
                                    if (total_time) >= timedelta(hours=hr_settings.threshold_for_additional_hours,minutes=0,seconds=0):
                                            data.additional_hours  =  (total_time) - timedelta(hours=hr_settings.threshold_for_additional_hours,minutes=0,seconds=0)
                                            total_additional_hours = total_additional_hours + data.additional_hours
                                    if data.late_sitting == None:
                                        data.late_sitting = total_time
                                        total_late_hr_worked += data.late_sitting
                            else:
                                present_days+=1
                        
                        continue
                    
                    if day_data.end_time > first_out_time:
                        per_day_h = first_out_time - first_in_time
                    else:
                        per_day_h = day_data.end_time - first_in_time
                    data.per_day_hour = per_day_h
                    if "day" in str(per_day_h):
                        per_day_h = str(per_day_h).split("day, ")[1].split(":")
                        per_day_h = timedelta(hours=float(per_day_h[0]), minutes=float(
                            per_day_h[1]), seconds=float(per_day_h[2]))
                    
                    data.per_day_hour = per_day_h
                    total_per_day_h = total_per_day_h + per_day_h
                    req_working = day_data.end_time - day_data.start_time
                    if "day" in str(req_working):
                        req_working = str(req_working).split("day, ")[1].split(":")
                        req_working = timedelta(hours=float(req_working[0]), minutes=float(
                            req_working[1]), seconds=float(req_working[2]))
                    if half_day_leave:
                        t = (flt(req_working.total_seconds())/3600)/2
                        required_working_hrs= required_working_hrs+t
                    else:
                        required_working_hrs= required_working_hrs+round(
                                            flt(req_working.total_seconds())/3600, 2)
                    half_day_time = day_data.half_day
                    late_mark = day_data.late_mark
                    in_diff = first_in_time - day_data.start_time
                    if not half_day_time:
                        half_day_time = day_data.late_mark
                    if "day" in str(in_diff):
                        in_diff = str(in_diff).split("day, ")[1].split(":")
                        in_diff = timedelta(hours=float(in_diff[0]), minutes=float(
                            in_diff[1]), seconds=float(in_diff[2]))

                    # if first_in_time < day_data.start_time:
                    #     if first_in_time != timedelta(hours=0):
                    #         if day_data.early_overtime_start:
                                # if first_in_time < day_data.early_overtime_start:
                                #     first_in_time = day_data.early_overtime_start
                                # data.early_overtime = day_data.start_time
                                # data.early_overtime = day_data.start_time - first_in_time 
                                # total_early_ot = total_early_ot + (day_data.start_time - first_in_time )
                                # first_in_time = day_data.start_time
                        
                    # if data.late1 == 1:
                    #     data.late = 0
                    # if data.late1 == 1:  # This is the correct way to check for late1 in the child table data
                    #     data.late = 0
                    if first_in_time >= late_mark and first_in_time < half_day_time:
                        data.late = 1
                        if day_data.calculate_late_hours == "Late Mark":
                            data.late_coming_hours = first_in_time - late_mark
                        else:    
                            data.late_coming_hours = first_in_time - day_data.start_time
                    else:
                        data.late = 0
                    if shift_doc.shift_type == "Night":
                        if first_in_time > late_mark:
                            if (first_in_time - late_mark) > timedelta(hours=12,minutes=0,seconds=0):
                                data.late = 0
                            else:
                                data.late = 1
                        elif first_in_time < late_mark:
                            if (late_mark - first_in_time) > timedelta(hours=12,minutes=0,seconds=0):
                                data.late = 1
                            else:
                                data.late = 0

                                

                    if first_in_time >= frappe.db.get_single_value('V HR Settings', 'night_shift_start_time'):
                        self.no_of_nights += 1
                   

                    if first_in_time >= half_day_time and shift_doc.shift_type != "Night":
                        data.half_day = 1
                    else:
                        data.half_day = 0
                    
                    if shift_doc.shift_type == "Night":
                        if first_in_time > half_day_time:
                            if (first_in_time - half_day_time) > timedelta(hours=12,minutes=0,seconds=0):
                                data.half_day = 0
                            else:
                                data.late = 0
                                data.half_day = 1
                        elif first_in_time < half_day_time:
                            if (half_day_time - first_in_time) > timedelta(hours=12,minutes=0,seconds=0):
                                data.half_day = 1
                                data.late = 0
                            else:
                                data.half_day = 0
                    
                    # if data.late1 == 1:  # This is the correct way to check for late1 in the child table data
                    #     data.late = 0
                    
                    
                    if data.check_out_1:
                        out_diff = day_data.end_time - first_out_time
                        if "day" in str(out_diff):
                            out_diff = str(out_diff).split("day, ")[1].split(":")
                            out_diff = timedelta(hours=float(out_diff[0]), minutes=float(
                                out_diff[1]), seconds=float(out_diff[2]))

                        if (out_diff.total_seconds()/60) > 00.00 and (out_diff.total_seconds()/60) <= float(day_data.max_early):
                            if first_out_time < day_data.end_time:
                                data.early = 1
                        elif (out_diff.total_seconds()/60) >= float(day_data.max_early) and (out_diff.total_seconds()/60) < float(day_data.max_half_day):
                            
                            data.half_day = 1
                            data.early = 0
                        elif (out_diff.total_seconds()/60) > 720:
                            tmp  = (out_diff.total_seconds()/60) -720
                            if tmp >= float(day_data.max_early) and tmp < float(day_data.max_half_day) and (total_time < (day_data.end_time - day_data.start_time)):
                                data.half_day = 1
                                data.early = 0 
                        elif (out_diff.total_seconds()/60) > float(day_data.max_half_day) and data.weekly_off==0 and data.public_holiday == 0:
                            if first_out_time < day_data.end_time:
                                data.absent = 1
                        else:
                            data.early = 0
                       
                        out_diff = day_data.over_time_start - first_out_time
                        
                        if "day" in str(out_diff):
                            out_diff = str(out_diff).split("day, ")[1].split(":")
                            out_diff = timedelta(hours=float(out_diff[0]), minutes=float(
                                out_diff[1]), seconds=float(out_diff[2]))
                        
                        ot_start  = day_data.over_time_start if day_data.over_time_start else day_data.end_time
                        if (out_diff.total_seconds()/60) > 720 and first_out_time < ot_start and shift_doc.shift_type!="Night":
                            hrs = timedelta(hours=24, minutes=0,
                                            seconds=0) - out_diff
                            hrs = hrs
                           
                            data.late_sitting = hrs
                        if (out_diff.total_seconds()/60) > 720 and first_out_time > ot_start and shift_doc.shift_type!="Night":
                            hrs = timedelta(hours=24, minutes=0,
                                            seconds=0) - out_diff
                           
                            hrs = hrs
                            data.late_sitting = hrs
                        if first_out_time > ot_start and shift_doc.shift_type == "Night":
                            hrs = timedelta(hours=24, minutes=0,
                                            seconds=0) - out_diff
                            hrs = hrs
                            data.late_sitting = hrs
                        if data.absent == 1 or not data.check_out_1:
                            data.late_sitting = None
                        #setting required
                        if data.late_sitting:
                            new_late_sitting = data.late_sitting
                            if data.late_sitting >= timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0):
                                new_late_sitting = timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0) + timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0)
                            if data.late_sitting >= timedelta(hours=hr_settings.threshold_for_additional_hours,minutes=0,seconds=0):
                                    data.additional_hours  =  data.late_sitting - timedelta(hours=hr_settings.threshold_for_additional_hours,minutes=0,seconds=0)
                                    total_additional_hours = total_additional_hours + data.additional_hours
                            data.late_sitting = new_late_sitting

                        if first_out_time >= timedelta(hours=get_time(hr_settings.night_shift_start_time).hour,minutes=get_time(hr_settings.night_shift_start_time).minute) and holiday_flag:
                            data.holiday_night = 1
                            self.no_of_holiday_night+=1

                else:
                    if data.weekly_off==0 and data.public_holiday == 0:
                        data.absent = 1 
                        data.late = 0
                        data.half_day = 0
                        data.early = 0


                if total_time:
                    total_time_hours = total_time.total_seconds()/3600
                    if total_time_hours >= day_data.minimum_hours_for_present:
                        if day_data.minimum_hours_for_present > 0:
                            data.absent = 0
                            data.half_day = 0
                    elif total_time_hours >= day_data.minimum_hours_for_half_day:
                        if day_data.minimum_hours_for_half_day > 0:
                            data.half_day = 1
                    else:
                        if (day_data.minimum_hours_for_half_day > 0 and day_data.minimum_hours_for_present > 0) \
                             or total_time_hours < day_data.minimum_hours_for_absent :
                            data.absent = 1
                            data.half_day = 0
                            data.early = 0
                            data.late = 0
                if hr_settings.late_and_early_mark:
                    if data.early==1 and data.late == 1:
                        data.half_day = 1
                elif hr_settings.late_mark:
                    if data.late == 1:
                        data.half_day = 1
                elif hr_settings.early_mark:
                    if data.early==1:
                        data.half_day = 1
                if day_data:
                    if day_data.end_time > first_out_time and data.early ==1:
                        data.early_going_hours =  day_data.end_time - first_out_time
                        if day_data.calculate_early_hours == "Exit Grace Period":
                                    data.early_going_hours = data.early_going_hours - timedelta(hours=0,minutes=int(day_data.max_early),seconds=0)
                        #total_early_going_hrs = total_early_going_hrs + data.early_going_hours
                if data.weekly_off==1 or data.public_holiday == 1:
                     data.absent = 0 
                
                if first_in_time:
                    if first_in_time >= timedelta(hours=get_time(hr_settings.night_shift_start_time).hour,minutes=get_time(hr_settings.night_shift_start_time).minute) or s_type == "Night":
                        data.night = 1
                
                # if data.late1 == 1:  # This is the correct way to check for late1 in the child table data
                #         data.late = 0

                if data.early:
                    total_early += 1
                if data.late:
                    total_lates += 1
                    # if data.late_coming_hours:
                    #     total_late_coming_hours = total_late_coming_hours + data.late_coming_hours
                if data.half_day:
                    total_half_days += 1
              
                if data.absent == 1:
                    self.total_absents +=1
                if data.half_day == 1:
                    if data.absent == 1:
                        data.absent = 0
                        self.total_absents -=1
                if data.absent == 0 and data.check_in_1:
                    if holiday_flag:
                        if hr_settings.count_working_on_holiday_in_present_days == 1:
                            present_days+=1
                    else:
                     present_days+=1
                

                if total_time:    
                    total_hr_worked = total_hr_worked + total_time
                    
                
                
                

                # if data.late1 == 1:  # This is the correct way to check for late1 in the child table data
                #         data.late = 0
                if data.late_sitting and data.weekly_off == 0 and data.public_holiday == 0:
                    
                    if day_data.overtime_slabs:
                        OT_slabs = frappe.get_doc("Overtime Slab",day_data.overtime_slabs)
                        prev_hours = None
                        for lb in OT_slabs.hours_slabs:
                            l_hrs = str(lb.actual_hours).split(".")[0]
                            l_mnt = str(lb.actual_hours).split(".")[1]
                            l_mnt  = "."+l_mnt
                            l_mnt = float(l_mnt)*60
                            l_actual_hours = timedelta(hours=int(l_hrs),minutes=int(l_mnt))
                            if data.late_sitting > l_actual_hours:
                                prev_hours = lb.counted_hours
                            elif data.late_sitting == l_actual_hours:
                                prev_hours = lb.counted_hours
                                break
                            else:
                                break
                        if prev_hours:
                            l_hrs = str(prev_hours).split(".")[0]
                            l_mnt = str(prev_hours).split(".")[1]
                            l_mnt  = "."+l_mnt
                            l_mnt = float(l_mnt)*60
                            l_counted_hours = timedelta(hours=int(l_hrs),minutes=int(l_mnt))
                            data.late_sitting = l_counted_hours

                        total_late_hr_worked = total_late_hr_worked + data.late_sitting
                        late_hours = round(
                                    flt((data.late_sitting).total_seconds())/3600, 2)
                       
                        amount = 0
                        for sl in OT_slabs.slabs:
                            if flt(late_hours) <= flt(sl.hours):
                               amount  = sl.amount
                            if flt(sl.hours) > flt(late_hours):
                                break
                            #for case if late sitting hours are greater than all slabs
                            amount  = sl.amount
                            
                        data.total_ot_amount = amount
                        extra_ot_amount+=amount
                    else:
                        total_late_hr_worked = total_late_hr_worked + data.late_sitting

                    data.extra_duty_for_fullday = 0
                    data.extra_duty_for_halfday = 0
                    if (data.late_sitting.total_seconds())/3600 >= hr_settings.working_day_fullday_overtime:
                        data.extra_duty_for_fullday = round((data.late_sitting.total_seconds())/3600,2)
                        self.total_extra_duty_for_fullday +=  data.extra_duty_for_fullday

                    elif (data.late_sitting.total_seconds())/3600 >= hr_settings.working_day_halfday_overtime:
                        data.extra_duty_for_halfday = round((data.late_sitting.total_seconds())/3600,2)
                        self.total_extra_duty_for_halfday += data.extra_duty_for_halfday

                data.difference = total_time  
                if holiday_flag == True and getdate(tempdate) <= getdate(today()):
                    accun_holiday+=1
                if data.extra_absent:
                    self.total_absents+=1
               
                if holiday_flag:
                     self.no_of_sundays+=1
                
                   
                     if total_time:
                                    if total_time >= timedelta(hours=hr_settings.holiday_halfday_ot,minutes=00,seconds=0) and \
                                        total_time < timedelta(hours=hr_settings.holiday_full_day_ot,minutes=00,seconds=0):
                                        holiday_halfday_ot = holiday_halfday_ot + 1
                                    elif total_time >= timedelta(hours=hr_settings.holiday_full_day_ot,minutes=00,seconds=0):
                                        holiday_full_day_ot = holiday_full_day_ot + 1
                                    if total_time >= timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0):
                                        data.late_sitting = timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0) + timedelta(hours=hr_settings.double_overtime_after,minutes=0,seconds=0)
                                        total_late_hr_worked += data.late_sitting
                                        #total_holiday_hours += total_time
                                    if (total_time) >= timedelta(hours=hr_settings.threshold_for_additional_hours,minutes=0,seconds=0):
                                            data.additional_hours  =  (total_time) - timedelta(hours=hr_settings.threshold_for_additional_hours,minutes=0,seconds=0)
                                            total_additional_hours = total_additional_hours + data.additional_hours
                                    if data.late_sitting == None:
                                        data.late_sitting = total_time
                                        total_late_hr_worked += data.late_sitting
                
                

                if data.late1 == 1:  # This is the correct way to check for late1 in the child table data
                        self.late_comparision += 1
                        data.late = 0
                        data.late_coming_hours = None
                        total_lates -= 1
                if data.weekly_off:
                    data.shift_start = None
                    data.shift_end = None
                    data.early_over_time = None
                    # data.approved_ot1 = None
                if data.check_in_1 is None and data.check_out_1 is not None:
                    data.absent = 0
                    
                if data.check_in_1 is not None and data.check_out_1 is None:
                    data.absent = 0
                        
                if data.weekly_off or data.public_holiday:
                    # If either is True, set weekly_off to 0 and weekday to 0
                    data.weekly_off = 0
                    data.weekday = 0
                    data.public_holiday = 0
                else:
                    data.weekday = 1
                    
                if data.weekly_off == 1:
                    data.day_type = "Weekly Off"
                elif data.weekday == 1:
                    data.day_type = "Weekday"
                elif data.public_holiday == 1:
                    data.day_type = "Public Holiday"
                    
                    
            

                    
                # if data.check_in_1:
                #         data.approved_ot1 = "00:00:00" 
                # if data.check_in_1 == None:
                #     data.approved_early_over_time = None
                # if data.check_in_1 == None and data.check_out_1 != None:
                #     data.absent = 0
                # if data.check_in_1 != None and data.check_out_1 == None:
                #     data.absent = 0
                # if data.check_in_1:
                #     data.approved_early_over_time = None
                #     data.early_coming = None
                # if data.check_out_1:
                #     data.approved_early_over_time = None 
                #     data.early_coming = None
                # if data.check_in_1 == None and data.check_out_1 == None:
                #     data.approved_early_over_time = None  
                #     data.early_coming = "00:00:00"
                # if data.check_in_1 == None:
                #     data.approved_early_over_time = None 
                #     data.early_coming = None 
                # if data.shift_start != None and data.check_in_1 == None:
                #     data.early_coming = None
                
                # if data.check_in_1:
                #     # if data.late_sitting:
                #     data.total_ot_hours = "abcd"
                #     print("abddd")

                # if data.day == "Monday":
                #     data.early_ot = "90:90:90"
                shift1 = None

                shift_ass = frappe.get_all("Shift Assignment", 
                                           filters={'employee': self.employee,
                                            'start_date': ["<=", getdate(data.date)],
                                            'status' : 'Active',
                                            # 'start_date': ["<=", '2024-06-01']
                                            }, 
                                            fields=['*'])
                # if data.day == "Monday":
                #     data.early_ot = "90:90:90"
                shift1 = None
            
                if shift_ass:
                    first_shift_ass = shift_ass[0]
                
                    # shift1 = frappe.get_all("Shift Type", filters={"name": shift}, fields=['*'])
                    shift1 = frappe.get_all("Shift Type", filters={"name": shift_ass[0].shift_type}, fields=['*'])
                    if shift1 and len(shift1) > 0:
                        shift_data = shift1[0]
                        # data.early_ot = "90:00:00"
                        child_table_records = frappe.db.sql("""
                        select name, day, start_time, end_time, over_time_slab
                                                            FROM `tabShift Day`
                                                            WHERE parent = %s
                        """,(shift_data['name'],), as_dict=True)
                        
                        

                        
                       
                        
                        if child_table_records and len(child_table_records) > 0:
                            child_table = child_table_records[0]
                            for child_table in child_table_records:
                                if data.day == child_table['day']:
                                    data.shift_in = child_table.start_time
                                    data.shift_out = child_table.end_time
                                    
                                    #  calculating difference b/w shift out and check in 
                                    shift_out_str = data.shift_out  # Example: "18:00:00"
                                    check_out_1_str = data.check_out_1  # Example: "19:30:00"
                                    shift_in_str = data.shift_in
                                    check_in_1_str = data.check_in_1
                                    
                                    # difference1 = timedelta()

                                    # Handle the case where `shift_out_str` is a timedelta
                                    if isinstance(shift_out_str, timedelta):
                                        # Convert timedelta to a time string
                                        shift_out_time = (datetime.min + shift_out_str).time()
                                        shift_out_str = shift_out_time.strftime("%H:%M:%S")
                                        
                                    if isinstance(shift_in_str, timedelta):
                                        shift_in_time = (datetime.min + shift_in_str).time()
                                        shift_in_str = shift_in_time.strftime("%H:%M:%S")
                                    
                                    if isinstance(check_in_1_str, timedelta):
                                        check_in_1_time = (datetime.min + check_in_1_str).time()
                                        check_in_1_str = check_in_1_time.strftime("%H:%M:%S")
                                    
                                    if isinstance(check_out_1_str, timedelta):
                                        check_out_1_time = (datetime.min + check_out_1_time).time()
                                        check_out_1_str = check_out_1_time.strftime("%H:%M:%S")
                                        
                                    # else:
                                    #     shift_in_str = data.shift_in
                                        
                                    # Ensure both are strings and `check_out_1_str` is not None
                                    if isinstance(shift_out_str, str) and isinstance(check_out_1_str, str) and isinstance(shift_in_str, str):
                                        try:
                                            # Convert the string times to datetime objects
                                            shift_out_time = datetime.strptime(shift_out_str, "%H:%M:%S")
                                            check_out_1_time = datetime.strptime(check_out_1_str, "%H:%M:%S")
                                            shift_in_time = datetime.strptime(shift_in_str, "%H:%M:%S")
                                            
                                            difference1 = timedelta()
                                             
                                            if check_out_1_time < shift_out_time and data.over_time_type != "Weekly Off":
                                                check_out_1_time += timedelta(days=1)
                                                difference1 = check_out_1_time - shift_out_time
                                            
                                            if check_out_1_time > shift_out_time:
                                                difference1 = check_out_1_time - shift_out_time
                                            if data.over_time_type == "Weekly Off":
                                                # difference1 = timedelta(hours=10, minutes=10, seconds=10)
                                                difference1 = check_out_1_time - shift_in_time
                                            
                                            # # Get the total difference in seconds and break it down into hours, minutes, and seconds
                                            total_seconds = int(difference1.total_seconds())
                                            hours = total_seconds // 3600
                                            minutes = (total_seconds % 3600) // 60
                                            seconds = total_seconds % 60
                                            
                                            # Format the time difference as HH:MM:SS
                                            difference_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                                            data.difference1 = difference_str  # Assign the formatted difference to the data object
                                            # data.difference1 = difference1
                                        except ValueError as e:
                                            pass
                                            # Log the error in case the string-to-time conversion fails
                                            # frappe.log_error(f"Error converting time: {e}", "Time Conversion Error")
                                    
                                    if isinstance(shift_in_str, str) and isinstance(check_in_1_str, str):
                                        try:
                                            # Parse the time strings into datetime objects
                                            shift_in_time = datetime.strptime(shift_in_str, "%H:%M:%S")
                                            check_in_1_time = datetime.strptime(check_in_1_str, "%H:%M:%S")

                                            # Initialize the time difference
                                            difference1 = timedelta()

                                            # Calculate the difference as CHECK IN - SHIFT IN
                                            if check_in_1_time < shift_in_time:
                                                difference1 = shift_in_time - check_in_1_time
                                            # else:
                                            #     difference1 = None
                                            #     # Optional: If check-in is before the shift, handle that scenario if needed
                                            #     difference1 = shift_in_time - check_in_1_time

                                            # Convert the total difference in seconds and format as HH:MM:SS
                                            if difference1 is not None:
                                                total_seconds = int(difference1.total_seconds())
                                                hours = total_seconds // 3600
                                                minutes = (total_seconds % 3600) // 60
                                                seconds = total_seconds % 60

                                                # Format the time difference as HH:MM:SS
                                                difference_str = f"{hours:02}:{minutes:02}:{seconds:02}"

                                                # Assign the formatted difference to the data object
                                                data.early_difference1 = difference_str

                                        except ValueError as e:
                                            # Handle any value parsing errors here
                                            print(f"Error parsing time strings: {e}")

                                    
                            day_type = data.day_type 

                            over_time_slab_doc = frappe.db.sql("""
                            SELECT 
                                ots.name,
                                otc.from_time,
                                otc.to_time,
                                otc.type,
                                otc.formula,
                                otc.per_hour_calculation,
                                otc.hours_for_full_day_over_time
                            FROM 
                                `tabOver Time Slab` as ots
                            LEFT JOIN 
                                `tabOver Time Slab CT` as otc 
                            ON 
                                otc.parent = ots.name
                            WHERE 
                                otc.type = %s 
                        """, (day_type,), as_dict=True)
                            
                            over_time_slab_doc_1 = frappe.db.sql("""
                            SELECT 
                                ots.name,
                                otc.from_time,
                                otc.to_time,
                                otc.type,
                                otc.formula,
                                otc.per_hour_calculation,
                                otc.hours_for_full_day_over_time
                            FROM 
                                `tabOver Time Slab` as ots
                            LEFT JOIN 
                                `tabEarly Overtime Slab` as otc 
                            ON 
                                otc.parent = ots.name
                            WHERE 
                                otc.type = %s 
                        """, (day_type,), as_dict=True)

                        
                        # Ensure `check_out_1_str` and `shift_out_str` are not None and are strings
                        # Ensure `shift_out_str` and `check_out_1_str` are strings and handle other types
                        shift_in_str_1 = data.shift_in
                        shift_out_str = data.shift_out
                        check_in_1_str = data.check_in_1
                        check_out_1_str = data.check_out_1


                        

                        # Initialize check_out_1_time and shift_out_time
                        time_difference_delta = timedelta(0)
                        check_out_1_time = None
                        shift_out_time = None
                        check_in_1_time = None
                        shift_in_time_1 = None

                        # Convert to string if they are of type datetime.timedelta
                        if isinstance(shift_out_str, timedelta):
                            shift_out_str = str(shift_out_str)
                        if isinstance(check_out_1_str, timedelta):
                            check_out_1_str = str(check_out_1_str)
                        if isinstance(shift_in_str_1, timedelta):
                            shift_in_str_1 = str(shift_in_str_1)
                        if isinstance(check_in_1_str, timedelta):
                            check_in_1_str = str(check_in_1_str)

                        # Check if the strings are valid
                        if isinstance(shift_out_str, str) and isinstance(check_out_1_str, str) and isinstance(data.difference1, str):
                            try:
                                shift_out_time = datetime.strptime(shift_out_str, "%H:%M:%S").time()
                                check_out_1_time = datetime.strptime(check_out_1_str, "%H:%M:%S").time()
                                time_difference = datetime.strptime(data.difference1, "%H:%M:%S").time()
                                time_difference_delta = timedelta(hours=time_difference.hour, minutes=time_difference.minute, seconds=time_difference.second)
                                
                            except ValueError as e:
                                print(f"Error parsing time: {e}")
                        else:
                            print("Error: shift_out_str or check_out_1_str is not a valid string.")
                        


                        if isinstance(shift_in_str_1, str) and isinstance(check_in_1_str, str) and isinstance(data.early_difference1, str):
                            try:
                                shift_in_time_1 = datetime.strptime(shift_in_str_1, "%H:%M:%S").time()
                                check_in_1_time = datetime.strptime(check_in_1_str, "%H:%M:%S").time()
                                time_difference1 = datetime.strptime(data.early_difference1, "%H:%M:%S")
                                time_difference_delta1 = timedelta(hours=time_difference1.hour, minutes=time_difference1.minute, seconds=time_difference1.second)

                            except ValueError as e:
                                print(f"Error parsing time: {e}")
                        
                        # frappe.log_error(f"Check-out time: {check_out_1_time}, Shift out time: {shift_out_time}, Time difference: {time_difference_delta}")
                        
                        if over_time_slab_doc:
                            for record in over_time_slab_doc:
                                data.over_time_type = record.type
                                data.per_hours_calculation = record.per_hour_calculation
                                data.over_time_amount = record.formula
                                threshould = record.hours_for_full_day_over_time

                                if isinstance(record.from_time, timedelta):
                                    record.from_time = (datetime.min + record.from_time).time()

                                if isinstance(record.to_time, timedelta):
                                    record.to_time = (datetime.min + record.to_time).time()
                            
                                if check_out_1_time is not None:
                                    if record.from_time > record.to_time:
                                        # Shift crosses midnight
                                        if check_out_1_time >= record.from_time or check_out_1_time <= record.to_time:
                                            if time_difference_delta >= threshould:
                                                time_difference_multiplied = time_difference_delta * record.per_hour_calculation
                                                time_difference_result = time_difference_multiplied.total_seconds()
                                                final_timedelta = timedelta(seconds=time_difference_result)
                                                data.estimated_late = final_timedelta
                                        else:
                                            if data.over_time_type == "Weekly Off":
                                                if time_difference_delta >= threshould:
                                                    time_difference_multiplied = time_difference_delta * record.per_hour_calculation
                                                    time_difference_result = time_difference_multiplied.total_seconds()
                                                    final_timedelta = timedelta(seconds=time_difference_result)
                                                    time_delta_difference = int(final_timedelta.total_seconds())
                                                    hours = time_delta_difference // 3600
                                                    minutes = (time_delta_difference % 3600) // 60
                                                    seconds = time_delta_difference % 60
                                                    difference_str1 = f"{hours}:{minutes}:{seconds}"
                                                    data.estimated_late = difference_str1
                                                
                                        
                                # frappe.log_error(f"Estimated Late: {data.date} - {data.estimated_late}")
                        if over_time_slab_doc_1:
                            for record_1 in over_time_slab_doc_1:
                                data.over_time_type1 = record_1.type
                                data.early_per_hours_calculation = record_1.per_hour_calculation
                                data.early_over_time_amount = record_1.formula
                                threshould1 = record_1.hours_for_full_day_over_time

                                if isinstance(record_1.from_time, timedelta):
                                    record_1.from_time = (datetime.min + record_1.from_time).time()

                                if isinstance(record_1.to_time, timedelta):
                                    record_1.to_time = (datetime.min + record_1.to_time).time()
                            
                                if data.check_in_1:
                                    if record_1.from_time < record_1.to_time:
                                        # Shift crosses midnight
                                        if check_in_1_time < record_1.to_time:
                                            if time_difference_delta1 > threshould:
                                                time_difference_multiplied = time_difference_delta1 * record_1.per_hour_calculation
                                                time_difference_result = time_difference_multiplied.total_seconds()
                                                final_timedelta = timedelta(seconds=time_difference_result)
                                                time_delta_difference = int(final_timedelta.total_seconds())
                                                hours = time_delta_difference // 3600
                                                minutes = (time_delta_difference % 3600) // 60
                                                seconds = time_delta_difference % 60
                                                difference_str1 = f"{hours}:{minutes}:{seconds}"
                                                data.estimate_early = final_timedelta
                                        else:
                                            if data.over_time_type == "Weekly Off":
                                                if time_difference_delta1 > threshould:
                                                    time_difference_multiplied = time_difference_delta1 * record_1.per_hour_calculation
                                                    time_difference_result = time_difference_multiplied.total_seconds()
                                                    final_timedelta = timedelta(seconds=time_difference_result)
                                                    time_delta_difference = int(final_timedelta.total_seconds())
                                                    hours = time_delta_difference // 3600
                                                    minutes = (time_delta_difference % 3600) // 60
                                                    seconds = time_delta_difference % 60
                                                    difference_str1 = f"{hours}:{minutes}:{seconds}"
                                                    data.estimate_early = difference_str1
                                                    
                                    else:
                                        pass
                                        # Shift crosses midnight
                                        # if check_in_1_time >= record_1.from_time or check_in_1_time <= record_1.to_time:
                                        #     if time_difference_delta1 < threshould:
                                        #         time_difference_multiplied = time_difference_delta1 * record_1.per_hour_calculation
                                        #         time_difference_result = time_difference_multiplied.total_seconds()
                                        #         final_timedelta = timedelta(seconds=time_difference_result)
                                        #         time_delta_difference = int(final_timedelta.total_seconds())
                                        #         hours = time_delta_difference // 3600
                                        #         minutes = (time_delta_difference % 3600) // 60
                                        #         seconds = time_delta_difference % 60
                                        #         difference_str1 = f"{hours}:{minutes}:{seconds}"
                                        #         data.estimate_early = "09:09:09"


                                
                        # if hasattr(data, 'estimated_late'):
                        #     frappe.log_error(f"Final Estimated Late: {data.estimated_late}")
                        # else:
                        #     frappe.log_error("No estimated late time calculated.")

                        # frappe.log_error(f"Record processed: {record}")

                            # Usage Example
                            # day_type = data.day_type  # Assuming day_type is available in your data
                            # overtime_data = get_overtime_slab_data(day_type)

                            # if overtime_data:
                            #     print("Overtime Slab Data for", day_type)
                            #     for slab in overtime_data:
                            #         data.over_time_type = slab.get('type')
                            #         frappe.log(f"No.: {slab.get('name')}")
                            #         # ... Process other data
                            # else:
                            #     frappe.log(f"No overtime slab found for day type: {day_type}")
                            
                            # data.early_ot = over_time_slab_doc
                            # Fetch only necessary columns, add relevant filters
                            
                            # over_time_slab_doc = frappe.db.sql("""
                            #     SELECT ots.name, otc.from_time, otc.to_time, otc.total_hours
                            #     FROM `tabOver Time Slab` AS ots
                            #     LEFT JOIN `tabOver Time Slab CT` AS otc ON otc.parent = ots.name
                            #     WHERE otc.from_time IS NOT NULL AND otc.to_time IS NOT NULL
                            # """, as_dict=True)

                            # # Process logic
                            # time_format = "%H:%M:%S"

                            # # Function to convert timedelta to time
                            # def timedelta_to_time(td):
                            #     if isinstance(td, timedelta):
                            #         # Convert timedelta to total seconds and then to time
                            #         return (datetime.min + td).time()
                            #     return td

                            # # Function to handle time spans that go past midnight
                            # def is_within_time_span(check_time, from_time, to_time):
                            #     if from_time > to_time:  # Time span crosses midnight
                            #         return check_time >= from_time or check_time <= to_time
                            #     else:  # Regular time span
                            #         return from_time <= check_time <= to_time

                            # Iterate through the overtime slabs
                            # for row in over_time_slab_doc.get("Over Time Slab CT"):
                            # for ot in over_time_slab_doc:
                                # if data.weekday == 1:
                                #     data.over_time_type = ot.get("type")
                                # else:
                                #     data.over_time_type = "test"
                                # if data.day_type == "Weekday":
                                #     if ot.type == "Weekday":
                                #         data.over_time_type = "1"
                                # elif data.day_type == "Weekly Off":
                                #     if ot.type == "Weekly Off":
                                #         data.over_time_type = "2"
                                    
                                
                                    
                                # data.early_ot = '3'
                                # Check if it's not a weekly off (i.e., working day)
                                # if data.weekly_off == 0:
                                    # data.early_ot = '2'
                                    # Check if overtime type exists
                                    # if data.weekday == 1:
                                    
                                    
                                    # if data.weekly_off == 1:
                                        # data.early_ot = '1'
                                        # Ensure `data[4].check_out_1`, `ot.from_time`, and `ot.to_time` are non-empty and valid
                                        # if data.check_out_1 and ot.from_time and ot.to_time:
                                            # print("Row Index:", ot.idx)
                                            # print("Type:", ot.type)
                                            # print("From Time:", ot.from_time)
                                            # print("To Time:", ot.to_time)
                                            
                                            # data.over_time_type = ot.type
                                            # data.over_time_amount = ot.formula
                                            # data.per_hours_calculation = ot.per_hour_calculation
                                            # data.early_ot = ot.per_hour_calculation
                                            # if data.late_sitting is not None:
                                                
                                            #     late_sitting_obj = datetime.strptime(data.check_out_1, '%H:%M:%S')
                                            #     # data.estimated_late = late_sitting_obj
                                            #     late_sitting_time_delta = timedelta(hours=late_sitting_obj.hour, minutes=late_sitting_obj.minute, seconds=late_sitting_obj.second)
                                            #     # data.estimated_late = 1
                                            #     expected_late_sitting = late_sitting_time_delta * data.per_hours_calculation
                                            #     data.estimated_late = expected_late_sitting
                                            # else:
                                            #     data.estimated_late = 0
                                    
                                                
                                            
                                            
                            #                 # Convert `data[4].check_out_1` to `datetime.time` if it's a string
                            #                 if isinstance(data.check_out_1, str):
                            #                     data.check_out_1 = datetime.strptime(data.check_out_1, time_format).time()
                            #                     data.early_ot = '6'

                            #                 # # Convert `from_time` and `to_time` to `datetime.time`, handling potential `timedelta`
                            #                 ot.from_time = timedelta_to_time(ot.from_time)
                            #                 ot.to_time = timedelta_to_time(ot.to_time)
                            #                 data.early_ot = ot.per_hour_calculation
                                            
                                            

                                            # # Check if `check_out_1` is within the overtime slab range
                                            # if is_within_time_span(data.check_out_1, ot.from_time, ot.to_time):
                                            #     # data.early_ot = ot.total_hours 
                                            #     # Example time string and float value
                                            #     time_string = data.late_sitting  # Time in HH:MM:SS format
                                            #     multiplier = ot.per_hour_calculation          # Float value to multiply by

                                            #     # Step 1: Convert the time string to a `datetime` object
                                            #     time_format = "%H:%M:%S"
                                            #     time_obj = datetime.strptime(time_string, time_format)

                                            #     # Step 2: Convert the `datetime` object to `timedelta`
                                            #     time_delta = timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)

                                            #     # Step 3: Convert `timedelta` to total seconds
                                            #     total_seconds = time_delta.total_seconds()

                                            #     # Step 4: Multiply the total seconds by the float
                                            #     new_total_seconds = total_seconds * multiplier

                                            #     # Step 5: Convert the result back to `timedelta`
                                            #     new_time_delta = timedelta(seconds=new_total_seconds)

                                            #     # Step 6: Optionally convert `timedelta` back to `HH:MM:SS` format
                                            #     new_time_string = str(new_time_delta)
                                            #     data.early_ot = new_time_string
                                                
                                # else:
                                #     # If it's a weekly off or holiday, set early overtime to 0
                                #     data.early_ot = 0
                            
                            

                            # Execute the SQL query
                            # result = frappe.db.sql(query, (shift_data['name'],), as_dict=True)

                            # data.early_ot = over_time_slab_doc.name
                            

                    
                        def time_to_seconds(time_string):
                            """Helper function to convert time string to seconds."""
                            if time_string is None:
                                raise ValueError("Time string is None")
                            t = datetime.strptime(time_string, "%H:%M:%S").time()
                            return t.hour * 3600 + t.minute * 60 + t.second

                        def get_time_difference(t1, t2):
                            """Calculate time difference in seconds between two time strings."""
                            t1_seconds = time_to_seconds(t1)
                            t2_seconds = time_to_seconds(t2)
                            return timedelta(seconds=t1_seconds - t2_seconds)

                        # Retrieve and verify data values
                        shift_in = data.shift_in
                        check_in_1 = data.check_in_1

                        # Print statements for debugging
                        # print(f"shift_in: {shift_in}")
                        # print(f"check_in_1: {check_in_1}")

                        # Convert shift_in and check_in_1 to time strings if they are timedelta
                        if isinstance(shift_in, timedelta):
                            total_seconds = int(shift_in.total_seconds())
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            shift_in_time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
                        else:
                            shift_in_time_string = shift_in

                        if isinstance(check_in_1, timedelta):
                            total_seconds = int(check_in_1.total_seconds())
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            check_in_1_time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
                        else:
                            check_in_1_time_string = check_in_1

                        # Ensure both time strings are not None
                        if shift_in_time_string is None or check_in_1_time_string is None:
                            data.early_ot = None
                        else:
                            # Convert time strings to datetime objects for comparison
                            shift_in_datetime = datetime.strptime(shift_in_time_string, "%H:%M:%S")
                            check_in_1_datetime = datetime.strptime(check_in_1_time_string, "%H:%M:%S")


                            # Calculate time difference if check_in_1 is earlier than shift_in
                            if check_in_1_datetime < shift_in_datetime:
                                time_difference = get_time_difference(shift_in_time_string, check_in_1_time_string)
                                data.early_ot = time_difference
                            else:
                                data.early_ot = None
                        
                        if data.late_sitting:
                            late_sitting_timedelta = data.late_sitting
                            # late_sitting_timedelta = timedelta(hours=data.late_sitting.hour, minutes=data.late_sitting.minutes, seconds= data.late_sitting.seconds)
                        else:
                            late_sitting_timedelta = timedelta(0)
                        
                        if data.early_ot:
                            if isinstance(data.early_ot, str):
                                early_ot_hours, early_ot_minutes, early_ot_seconds = map(int, data.early_ot.split(':'))
                                early_ot_timedelta = timedelta(hours=early_ot_hours,minutes=early_ot_minutes,seconds=early_ot_seconds)
                            else:
                                early_ot_timedelta = data.early_ot

                        else:
                            early_ot_timedelta = timedelta(0)
                        
                        total_ot_time_delta = late_sitting_timedelta + early_ot_timedelta

                        total_seconds = total_ot_time_delta.total_seconds()
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        data.total_ot_hours = "{:02}:{:02}:{:02}".format(int(hours),int(minutes),int(seconds))

                        if data.approved_ot1:
                            approved_ot1_hours, approved_ot1_minutes, approved_ot1_seconds = map(int, data.approved_ot1.split(':'))

                            # approved_ot1_hours, approved_ot1_minutes, approved_ot1_seconds = map(int, data.approved_ot1(':'))
                            approved_ot1_timedelta = timedelta(hours=approved_ot1_hours, minutes=approved_ot1_minutes, seconds=approved_ot1_seconds)
                            # approved_eot_timedelta = data.total_approved_ot
                            # data.total_approved_ot = approved_ot1_seconds
                        else:
                            approved_ot1_timedelta = timedelta(0) 
                        
                        if data.approved_eot:
                            approved_eot_hours, approved_eot_minutes, approved_eot_seconds = map(int, data.approved_eot.split(':'))
                            approved_eot_timedelta = timedelta(hours=approved_eot_hours, minutes=approved_eot_minutes, seconds=approved_eot_seconds)
                            # data.total_approved_ot = approved_eot_timedelta 
                        else:
                            approved_eot_timedelta = timedelta(0)
                        
                        total_approved_ot_data = approved_ot1_timedelta + approved_eot_timedelta

                        total_seconds = total_approved_ot_data.total_seconds()
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        data.total_approved_ot = "{:02}:{:02}:{:02}".format(int(hours),int(minutes),int(seconds))

                        if self.late_sitting_hours is None:
                            self.late_sitting_hours = 0.0
                        else:
                            self.late_sitting_hours = float(self.late_sitting_hours)

                        late_sitting_hours_float = float(self.late_sitting_hours)

                        # set total overtime in employee attendance   
                        if self.early_ot is None:
                            self.early_ot = 0.0
                        else:
                            self.early_ot = float(self.early_ot)

                        early_ot_float = float(self.early_ot)

                        # else:
                        #     raise ValueError("No Shift Found")    
                        
                        if data.late_sitting:
                            late_sitting_timedelta = data.late_sitting
                            # late_sitting_timedelta = timedelta(hours=data.late_sitting.hour, minutes=data.late_sitting.minutes, seconds= data.late_sitting.seconds)
                        else:
                            late_sitting_timedelta = timedelta(0)
                        
                        # if data.early_ot:
                        #     early_ot_timedelta = data.early_ot
                            # if isinstance(data.early_ot, str):
                            #     early_ot_hours, early_ot_minutes, early_ot_seconds = map(int, data.early_ot.split(':'))
                            #     early_ot_timedelta = timedelta(hours=early_ot_hours,minutes=early_ot_minutes,seconds=early_ot_seconds)
                            # else:
                            #     early_ot_timedelta = data.early_ot

                        # else:
                        #     early_ot_timedelta = timedelta(0)
                        
                        # total_ot_time_delta = late_sitting_timedelta + early_ot_timedelta

                        # total_seconds = total_ot_time_delta.total_seconds()
                        # hours, remainder = divmod(total_seconds, 3600)
                        # minutes, seconds = divmod(remainder, 60)
                        # data.total_ot_hours = "{:02}:{:02}:{:02}".format(int(hours),int(minutes),int(seconds))
                        # set total overtime 
                        if self.late_sitting_hours:
                            self.total_overtime = self.late_sitting_hours
                        else:
                            self.total_overtime = 0
                        if self.early_ot:
                            self.total_overtime = self.early_ot
                        else:
                            self.total_overtime = 0
                        if self.late_sitting_hours and self.early_ot:
                            self.total_overtime = self.early_ot + self.late_sitting_hours

                        # set approved overtime le

                        if self.approved_ot:
                            self.approved_overtime_le = float(self.approved_ot)
                        else:
                            self.approved_overtime_le = 0
                        if self.approved_early_over_time_hour:
                            self.approved_overtime_le = float(self.approved_early_over_time_hour)
                        else:
                            self.approved_early_over_time_hour = 0
                        if self.approved_ot and self.approved_early_over_time_hour:
                            approved_overtime_le = float(self.approved_ot) + float(self.approved_early_over_time_hour)
                            self.approved_overtime_le = "{:.2f}".format(approved_overtime_le)

                        else:
                            self.approved_overtime_le = 0
                
                else:
                    raise ValueError(f"No Shift Found for these employee: {self.employee}")
                
                
                

                # if data.check_in_1:

                    # late_sitting_time = data.late_sitting if data.late_sitting else timedelta(0)
                    # early_over_time = data.early_over_time if data.early_over_time else timedelta(0)    

                    # total_ot_time_delta = late_sitting_time + early_over_time

                    # total_seconds = total_ot_time_delta.total_seconds()

                    # hours, remainder = divmod(total_seconds, 3600)
                    # minutes, seconds = divmod(remainder, 60)
                    # data.total_ot_hours = "{:02}:{:02}:{:02}".format(int(hours),int(minutes), int(seconds))
                    # pass
                    # late_sitting_time = datetime.strptime(data.late_sitting)
                    # early_over_time = datetime.strptime(data.early_over_time)
                    # total_ot_delta = (late_sitting_time - datetime(1900,1,1)) + (early_over_time - datetime(1900,1,1))
                    # data.total_ot_hours = str(total_ot_delta)
                    # if '.' in data.total_ot_hours:
                    #     data.total_ot_hours = data.total_ot_hours.split('.')[0]
                    
                    # print(data.total_ot_hours)

                # if data.late_sitting:
                #     data.total_ot_hours
                # if data.early_over_time:
                #     data.total_ot_hours
                # if data.late_sitting and data.early_over_time:
                #     data.total_ot_hours = data.late_sitting + data.early_over_time                

                
                # if data.check_in_1:
                #     time_format = "%H:%M:%S"
                    
                #     # Parse the strings into datetime objects
                #     check_in_1_time = datetime.strptime(data.check_in_1, time_format)
                #     shift_in_time = datetime.strptime(data.shift_in, time_format)
                    
                #     # Calculate the difference
                #     early_ot_timedelta = shift_in_time - check_in_1_time
                    
                #     # Convert the difference back to hh:mm:ss format
                #     early_ot_time = str(early_ot_timedelta)
                    
                #     # If the timedelta includes days, remove them
                #     if len(early_ot_time) > 8:
                #         early_ot_time = early_ot_time[-8:]
                        
                #     data.early_ot = early_ot_time

                # if data.check_in_1:
                #     time_format = "%H:%M:%S"
                #     check_in_1_time = datetime.strptime(data.check_in_1, time_format)
                #     shift_in_time = datetime.strptime(data.shift_in, time_format)
                #     early_ot_timedelta = shift_in_time - check_in_1_time
                #     early_ot_time = str(early_ot_timedelta)
                #     data.early_ot = early_ot_time

                # if data.check_in_1 == None:
                #     data.approved_early_over_time = "00:00:00"
                # if data.check_in_1:
                #     data.approved_early_over_time = "00:00:00"
                #     # data.early_over_time = data.check_in_1 - start_time_formatted
                #     check_in_datetime = datetime.strptime(data.check_in_1, '%H:%M:%S')
                #     check_in_time = check_in_datetime.time()
                #     check_in_time_delta = timedelta(hours=check_in_time.hour, minutes=check_in_time.minute, seconds=check_in_time.second)
                #     shift_start_time = data.shift_start
                #     shift_start_time_delta = timedelta(hours=shift_start_time.hour, minutes=shift_start_time.minute, seconds=shift_start_time.second)
                #     if check_in_time_delta < shift_start_time_delta:
                #         result_delta = shift_start_time_delta - check_in_time_delta
                #         result_time = (datetime.min + result_delta).time()
                #         data.early_over_time = result_time

                #     else:
                #         data.early_over_time = None
                    
                    # result_delta = check_in_time_delta - shift_start_time_delta
                    # result_time = (datetime.min + result_delta).time()
                    # data.early_over_time = result_time
                    # data.check = result_time

                

                if day_data and not holiday_flag:
                    if day_data.late_slab and data.late_coming_hours:
                        lsm = frappe.get_doc("Late Slab", day_data.late_slab)
                        if data.late_coming_hours > timedelta(hours=0,minutes=int(lsm.late_slab_minutes)):
                            data.late_coming_hours = data.late_coming_hours - timedelta(hours=0,minutes=int(lsm.late_slab_minutes))
                            prev_hours = None
                            for lb in lsm.late_details:
                                l_hrs = str(lb.actual_hours).split(".")[0]
                                l_mnt = str(lb.actual_hours).split(".")[1]
                                l_mnt  = "."+l_mnt
                                l_mnt = float(l_mnt)*60
                                l_actual_hours = timedelta(hours=int(l_hrs),minutes=int(l_mnt))
                                
                                if data.late_coming_hours > l_actual_hours:
                                    prev_hours = lb.counted_hours
                                elif data.late_coming_hours == l_actual_hours:
                                    prev_hours = lb.counted_hours
                                    break
                                else:
                                    break
                            if prev_hours:
                                l_hrs = str(prev_hours).split(".")[0]
                                l_mnt = str(prev_hours).split(".")[1]
                                l_mnt  = "."+l_mnt
                                l_mnt = float(l_mnt)*60
                                l_counted_hours = timedelta(hours=int(l_hrs),minutes=int(l_mnt))
                                data.late_coming_hours = l_counted_hours
                            total_late_coming_hours = total_late_coming_hours + data.late_coming_hours
                    else:
                        if data.late_coming_hours:
                            total_late_coming_hours = total_late_coming_hours + data.late_coming_hours
                    if day_data.early_slab and data.early_going_hours:
                        esm = frappe.get_doc("Early Slab", day_data.early_slab)
                        if data.early_going_hours > timedelta(hours=0,minutes=int(esm.early_slab_minutes)):
                            data.early_going_hours = data.early_going_hours - timedelta(hours=0,minutes=int(esm.early_slab_minutes))
                            prev_hours = None
                            for lb in esm.early_details:
                                l_hrs = str(lb.actual_hours).split(".")[0]
                                l_mnt = str(lb.actual_hours).split(".")[1]
                                l_mnt  = "."+l_mnt
                                l_mnt = float(l_mnt)*60
                                l_actual_hours = timedelta(hours=int(l_hrs),minutes=int(l_mnt))
                                if data.early_going_hours > l_actual_hours:
                                    prev_hours = lb.counted_hours
                                elif data.early_going_hours == l_actual_hours:
                                    prev_hours = lb.counted_hours
                                    break
                                else:
                                    break
                            if prev_hours:
                                l_hrs = str(prev_hours).split(".")[0]
                                l_mnt = str(prev_hours).split(".")[1]
                                l_mnt  = "."+l_mnt
                                l_mnt = float(l_mnt)*60
                                l_counted_hours = timedelta(hours=int(l_hrs),minutes=int(l_mnt))
                                data.early_going_hours = l_counted_hours
                            total_early_going_hrs = total_early_going_hrs + data.early_going_hours
                    else:
                        if data.early_going_hours:
                            total_early_going_hrs = total_early_going_hrs + data.early_going_hours
                    
                
                if holiday_flag:
                    if data.early_going_hours and total_early_going_hrs!= timedelta(hours=0, minutes=0, seconds=0):
                            total_early_going_hrs = total_early_going_hrs - data.early_going_hours
                            data.early_going_hours = None
                    if data.late_coming_hours and total_late_coming_hours != timedelta(hours=0, minutes=0, seconds=0):
                            total_late_coming_hours = total_late_coming_hours - data.late_coming_hours
                            data.late_coming_hours = None

                    if data.early:
                        total_early -= 1
                        data.early = 0
                    if data.late1 == 1:  
                        total_lates -= 1
                    if data.late:
                        total_lates -= 1
                        data.late = 0
                
                # if data.check_out_1 is None:
                #     log = frappe.get_all(
                #         'Attendance Logs',
                #         filters={'attendance_date': "2024-08-31", 'type': 'Check Out'},  # Ensure correct date format
                #         fields=['attendance_time']
                #     )
                    
                #     if log:  # Check if log is not empty
                #         data.check_out_1 = log[0].attendance_time

                # if data.check_out_1 is None or data.check_out_1 is not None or data.check_in_1 is not None:
                    
                #     formatted_date = frappe.utils.formatdate(data.check_in_1, "yyyy-mm-dd")
                    
                #     log = frappe.db.sql("""
                #         SELECT attendance_time 
                #         FROM `tabAttendance Logs`
                #         WHERE attendance_date = %s
                #         AND `type` = 'Check Out'
                #     """, (formatted_date,))  # Ensure the date format is 'YYYY-MM-DD'


                #     if log:  # Check if log is not empty
                #         data.check_out_1 = log[0][0]  # Since frappe.db.sql returns a list of tuples
                
                
                check_sanwich_after_holiday(self,previous,data,hr_settings,index)
               
                previous = data
                index+=1

                half_day_leave = False
                holiday_flag = False
               
            except:
                frappe.log_error(frappe.get_traceback(),"Attendance")
                previous = data
             

        self.hours_worked = round(
            flt((total_hr_worked-total_late_hr_worked).total_seconds())/3600, 2)
        self.late_sitting_hours = round(
            flt(total_late_hr_worked.total_seconds())/3600, 2)
        self.holiday_halfday_ot = holiday_halfday_ot
        self.holiday_full_day_ot = holiday_full_day_ot
        self.over_time = self.late_sitting_hours
        # self.difference = round(
        #     (flt(self.hours_worked)-flt(required_working_hrs)), 2)
        if self.over_time >= 1:
            self.over_time = round(self.over_time)
        else:
            self.over_time = 0.0
        self.difference = round(
            flt(total_late_coming_hours.total_seconds())/3600, 2)
        self.approved_ot = round(
            flt(total_approved_ot.total_seconds())/3600, 2)
        
        self.extra_hours = round(
            flt(total_additional_hours.total_seconds())/3600, 2)
        self.extra_ot_amount = extra_ot_amount
        self.total_lates = total_lates
        self.total_early_goings = total_early
        self.total_half_days = total_half_days
        self.total_early_going_hours = total_early_going_hrs
        self.holiday_hour = round(flt(total_holiday_hours.total_seconds())/3600, 2)
        self.early_over_time = round(flt(total_early_ot.total_seconds())/3600, 2)
        t_lat = 0
        t_earl = 0
        if hr_settings.maximum_lates_for_absent > 0:
            t_lat = int(total_lates/hr_settings.maximum_lates_for_absent) if total_lates >= hr_settings.maximum_lates_for_absent else 0
        self.lates_for_absent = t_lat

        if hr_settings.maximum_early_for_absent > 0:
            t_earl = int(total_early/hr_settings.maximum_early_for_absent) if total_early >= hr_settings.maximum_early_for_absent else 0
        self.early_for_absents = t_earl
       
        self.short_hours = self.difference
       
        self.total_working_hours = round(required_working_hrs,2)
        self.total_difference_hours = round(self.total_working_hours - self.hours_worked,2)
        self.late_plus_early_hours_ = total_late_coming_hours + self.total_early_going_hours
        self.present_days = present_days 
        lfh = 0
        if hr_settings.maximum_lates_for_halfday > 0:
            lfh = int(total_lates/hr_settings.maximum_lates_for_halfday) if total_lates >= hr_settings.maximum_lates_for_halfday else 0
        self.lates_for_halfday = round(lfh/2,1)

        efh = 0
        if hr_settings.maximum_early_for_halfday > 0:
            efh = int(total_early/hr_settings.maximum_early_for_halfday) if total_early >= hr_settings.maximum_early_for_halfday else 0
        self.early_for_halfday = round(efh/2,1)
        self.total_early_going_hours = round(flt(total_early_going_hrs.total_seconds())/3600, 2)

    def get_month_no(self, month):
        dict_={
            "January":1,
            "February":2,
            "March":3,
            "April":4,
            "May":5,
            "June":6,
            "July":7,
            "August":8,
            "September":9,
            "October":10,
            "November":11,
            "December":12
        }
        return dict_[month]
    

                

def check_sanwich_after_holiday(self, previous,data,hr_settings,index):
    ab_index = []
    ab_index_process = False
    if data.absent == 1:
        for num in reversed(range(index)) :
            if self.table1[num].weekly_off ==1 or self.table1[num].public_holiday==1:
                ab_index.append(num)
            else:
                if hr_settings.absent_sandwich == 'Absent After Holiday':
                    ab_index_process = True
                    break
                elif hr_settings.absent_sandwich == 'Absent Before and After Holiday' and self.table1[num].absent == 1:
                        ab_index_process = True
                        break
                break
            
            
    
    if ab_index_process == True:
        for ind in ab_index:
                if self.table1[ind].absent != 1:
                    self.table1[ind].absent = 1
                    self.no_of_sundays-=1
                    if self.table1[ind].difference:
                        if self.table1[ind].difference >= timedelta(hours=hr_settings.holiday_halfday_ot,minutes=00,seconds=0) and \
                            self.table1[ind].difference < timedelta(hours=hr_settings.holiday_full_day_ot,minutes=00,seconds=0):
                           self.holiday_halfday_ot = self.holiday_halfday_ot - 1
                        elif self.table1[ind].difference >= timedelta(hours=hr_settings.holiday_full_day_ot,minutes=00,seconds=0):
                            if self.holiday_full_day_ot and self.holiday_full_day_ot != "":
                                self.holiday_full_day_ot = float(self.holiday_full_day_ot or 0) - 1
                    self.total_absents += 1



def get_holidays_for_employee(
	employee, start_date, end_date, raise_exception=True, only_non_weekly=False
):
	"""Get Holidays for a given employee

	`employee` (str)
	`start_date` (str or datetime)
	`end_date` (str or datetime)
	`raise_exception` (bool)
	`only_non_weekly` (bool)

	return: list of dicts with `holiday_date` and `description`
	"""
	holiday_list = get_holiday_list_for_employee(employee, raise_exception=raise_exception)

	if not holiday_list:
		return []

	filters = {"parent": holiday_list, "holiday_date": ("between", [start_date, end_date])}

	if only_non_weekly:
		filters["weekly_off"] = False

	holidays = frappe.get_all("Holiday", fields=["description","public_holiday", "holiday_date"], filters=filters)

	return holidays