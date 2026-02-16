from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS #Allow the HTML file to talk to Python

app = Flask(__name__)
CORS(app)

@app.route('/calculate', methods=['POST'])
def calculate():
    try: 
        data = request.json
        #global pan, ay, income, s_income, ltcg_income, stcg_income, ag_income
        #global itr, extended_due_date_val, order, refund, refund_amt, tds, tcs, advtax
        #global total_tax, self_ass_tax, self_ass_date, amt_pay_refund

        # Extracting inputs from Frontend
        # Use global for simplicity to keep your existing logic mostly intact
        pan = data.get('pan', '')
        name = data.get('name', '')
        ay = data.get('ay', '')
        income = float(data.get('income', 0))
        s_income = float(data.get('s_income', 0))
        ltcg_income = float(data.get('ltcg_income', 0))
        stcg_income = float(data.get('stcg_income', 0))
        ag_income = float(data.get('ag_income', 0))
        itr_d = data.get('itr_date', '') # Expecting DD/MM/YYYY
        order_d = data.get('order_date', '')
        refund_d = data.get('refund_date', '')
        refund_amt = float(data.get('refund_amt', 0))
        tds = float(data.get('tds', 0))
        tcs = float(data.get('tcs', 0))
        advtax = float(data.get('advtax', 0))
        interest_234c = float(data.get('interest_234c', 0))
        self_ass_tax = float(data.get('self_ass_tax', 0))
        self_ass_d = data.get('self_ass_date', '')
        taxorder = float(data.get('Tax as per Order', 0))
        
        #income = float(income_t.replace('₹', '').replace(',', '').strip())

        # --- DATE HELPER (Converting HTML date to your DD/MM/YYYY logic) ---
        def format_date(d):
            if not d: return ""
            return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")

        itr = format_date(itr_d)
        order = format_date(order_d)
        refund = format_date(refund_d)
        self_ass_date = format_date(self_ass_d)
           
        #Original Due date for ITR Filling
        def orginal_due_date():
            status = pan[3]
            if int(ay[0:4])<2023:
                if status == "P" or status == "B" or status == "A" or status == "H":
                    return f"{'31/07/'}{ay[0:4]}"
                return f"{'30/09/'}{ay[0:4]}"
            else:
                if status == "P" or status == "B" or status == "A" or status == "H":
                    return f"{'31/07/'}{ay[0:4]}"
                return f"{'30/10/'}{ay[0:4]}"
            
        #Extended Due date for ITR Filling    
        def extended_due_date():
            status = pan[3]
            if ay == "2015-16":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "31/08/2015"
                    return "30/09/2015"
            elif ay == "2016-17":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "05/08/2016"
                    return "17/10/2016"
            elif ay == "2017-18":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "31/10/2017"
                    return "07/11/2017"
            elif ay == "2018-19":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "31/08/2018"
                    return "31/10/2018"
            elif ay == "2019-20":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "31/08/2019"
                    return "30/09/2019"
            elif ay == "2020-21":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "10/01/2021"
                    return "15/02/2021"
            elif ay == "2021-22":
                    return "15/03/2022"
            elif ay == "2022-23":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "31/07/2022"
                    return "07/11/2022"
            elif ay == "2023-24":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "31/07/2023"
                    return "31/10/2023"
            elif ay == "2024-25":
                    if status == "P" or status == "B" or status == "A" or status == "H":
                        return "31/07/2024"
                    return "31/10/2024"
        
        # It calculates the months for interest calculation
        def diff_month(d1, d2):
            if not d1 or not d2: return 0
            d1_obj = datetime.strptime(d1, "%d/%m/%Y").date()
            d2_obj = datetime.strptime(d2, "%d/%m/%Y").date()
            if d1_obj > d2_obj:
                return (d1_obj.year - d2_obj.year) * 12 + d1_obj.month - d2_obj.month
            return 0

        #It defines the whether credit of tds to be given or not to the assessee in the calcuation of interest
        def net_tax():
            if refund_amt<(tds*1/2):
                n_tax = total_tax - tds - tcs - advtax
                return n_tax
            else:
                n_tax = total_tax - tcs - advtax
                return n_tax

        #It Calculates the interest u/s 234a to be lavied
        def interest_234a():
            # calculation of interest u/s 234a
            #e1 = datetime.strftime(extended_due_date(), "%d/%m/%Y").date()
            if net_tax()>0:
                month_a = diff_month (itr, extended_due_date())
                int_234a = round(net_tax()*month_a*1/100)
                return int_234a
            return 0

        #It Calculates the interest u/s 234b to be lavied
        def interest_234b():
            # calculation of interest u/s 234b
            due_date_234b = f"{'31/03/'}{ay[0:4]}"
            #due_date_234b = datetime.strftime(f"{'31/03/'}{ay[0:4]}", "%d/%m/%Y").date()
            month_b = diff_month(order, due_date_234b)
            if net_tax()>0:
                if self_ass_tax>0 :
                    month_b1 = diff_month(self_ass_date, due_date_234b)
                    month_b2 = diff_month(order, self_ass_date)
                    if (net_tax()-self_ass_tax)>0:
                        int_234b = round(net_tax()*month_b1*1/100 + (net_tax()-self_ass_tax)*month_b2*1/100)
                        return int_234b
                    int_234b = round(net_tax()*month_b1*1/100)
                    return int_234b
                int_234b = round(net_tax()*month_b*1/100)
                return int_234b
            return 0

        # It calculates the interest u/s 234d to be lavied
        def interest_234d ():
            if refund_amt>0:
                month_d = diff_month(order, refund)
                int_234d = round(refund_amt*month_d*1/200)
                return int_234d
            return 0

        #It calculates the interest u/s 244a to be given
        def interest_244a():
            due_date_234b = f"{'31/03/'}{ay[0:4]}"
            #due_date_234b = datetime.strftime(f"{'31/03/'}{ay[0:4]}", "%d/%m/%Y").date()
            month_244a = diff_month(order, due_date_234b)
            if amt_pay_refund<-10000:
                int_244a = round(amt_pay_refund*month_244a*1/200)
                return int_244a
            return 0

        #It calculates the penalty u/s 234f to lavied
        def penalty_234f():
            status = pan[3]
            #o1 = datetime.strftime(orginal_due_date(), "%d/%m/%Y").date()
            month_f = diff_month (itr, orginal_due_date())
            if total_tax>10000:
                if status == "P" or status == "B" or status == "A" or status == "H":
                    if month_f<5:
                        return 0
                    elif 5<month_f<8:
                        return 1000
                    return 10000
                else:
                    if month_f<3:
                        return 0
                    elif month_f<6:
                        return 1000
                return 10000
            return 0

        #Calculation of normal tax on agrregate income
        def normal_tax(normal_income):
            status = pan[3]
            #normal_income = int(income)-int(s_income)-int(ltcg_income)-int(stcg_income)+int(ag_income)
            if status == "P" or status == "B" or status == "A" or status == "H":
                if ay == "2015-16" or ay == "2016-17" or ay == "2017-18":
                    if normal_income<250000:
                        return 0
                    elif 250000<normal_income<500000:
                        return round((normal_income-250000)/10)
                    elif 500000<normal_income<1000000:
                        return 25000+round((normal_income-500000)/5)
                    else:
                        return 125000+round((normal_income-1000000)*3/10)
                elif int(ay[0:4])>2017:
                    if normal_income<250000:
                        return 0
                    elif 250000<normal_income<500000:
                        return round((normal_income-250000)/20)
                    elif 500000<normal_income<1000000:
                        return 12500+round((normal_income-500000)/5)
                    else:
                        return 112500+round((normal_income-1000000)*3/10)
            else:
                return round(normal_income*3/10)
            
        # Calculation of tax u/s 115BBE (Special rate)
        def special_tax():
            if int(ay[0:4])<2017:
                return round(s_income*3/10)
            return round(s_income*3/5)

        #Calculation of capital gain tax
        def capital_tax():
            ltcg_tax = round(ltcg_income/5)
            stcg_tax = round(stcg_income*3/20)
            return ltcg_tax+stcg_tax

        #Calculation of rebate for agricultural income
        def rebate():
            if ag_income>0:
                agtax_income = 250000+ag_income
                return normal_tax(agtax_income)
            return 0

        #Calculation of rebate under section 87A
        def rebate_87a():
            status = pan[3]
            if ay == "2019-20":
                if income<350000 and status == "P":
                    return min(2500,total_tax)
                return 0
            if int(ay[0:4])>2019:
                if income<500000 and status == "P":
                    return min(12500,total_tax)
                return 0
            return 0

        #Calculation of Surcharge on special income
        def special_surcharge ():
            if s_income>0 and int(ay[0:4])>2016:
                return round(special_tax()/4)
            return 0

        #Calculation of normal surcharge
        def normal_surcharge():
            status = pan[3] 
            if status == "P" or status == "B" or status == "A" or status == "H":
                if ay == "2015-16":
                    if total_tax>0 and income>10000000:
                        return round(total_tax/10)
                    else:
                        return 0
                if ay == "2016-17":
                    if total_tax>0 and income>10000000:
                        return round(total_tax*12/100)
                    else:
                        return 0
                if ay == "2017-18":
                    if (total_tax-special_tax())>0 and income>10000000:
                        return round((total_tax-special_tax())*15/100)
                    else:
                        return 0
                if ay == "2018-19" or ay == "2019-20":
                    if (total_tax-special_tax())>0:
                        if income<5000000:
                            return 0
                        if 5000000<income<10000000:
                            return round((total_tax-special_tax())/10)
                        else:
                            return round((total_tax-special_tax())*15/100)
                    else:
                        return 0
                if int(ay[0:4])>2019:
                    if (total_tax-special_tax())>0:
                        if income<=5000000:
                            return 0
                        if 5000000<income<=10000000:
                            return round((total_tax-special_tax())/10)
                        elif 10000000<income<=20000000:
                            return round((total_tax-special_tax())*15/100)
                        elif 20000000<income<=50000000 and (total_tax-special_tax()-capital_tax())>0:
                            return round((total_tax-special_tax()-capital_tax())/4)+round(capital_tax()*15/100)
                        elif income>50000000 and (total_tax-special_tax()-capital_tax())>0:
                            return round((total_tax-special_tax()-capital_tax())*37/100) + round(capital_tax()*15/100)
                    else:
                        return 0
            elif status == "C" or status == "F" or status == "T":
                if (ay == "2015-16" or ay == "2016-17") and (total_tax-special_tax())>0:
                    if income<=10000000:
                        return 0
                    elif 10000000<income<100000000:
                        return round((total_tax-special_tax())/20)
                    else:
                        return round ((total_tax-special_tax())/10)
                if int(ay[0:4])>2016 and (total_tax-special_tax())>0:
                    if income<10000000:
                        return 0
                    elif 10000000<income<100000000:
                        return round((total_tax-special_tax())*7/100)
                    else:
                        return round ((total_tax-special_tax())*12/100)
                else:
                    return 0
                
        #Calculation of Health and Education cess
        def cess():
            if int(ay[0:4])<2019:
                return round((total_tax+special_surcharge()+normal_surcharge())*3/100)
            else:
                return round((total_tax+special_surcharge()+normal_surcharge())*4/100)

        #Output to be displayed to user

        #Define variables
        normal_income = income - s_income - ltcg_income - stcg_income + ag_income
        total_tax = normal_tax(normal_income) + special_tax() + capital_tax() - rebate() - rebate_87a()
        gross_tax = total_tax + special_surcharge() + normal_surcharge() + cess()
        taxes_paid = tds + tcs + advtax + self_ass_tax
        total_interest = interest_234a() + interest_234b() + interest_234c + interest_234d() + penalty_234f()
        amt_pay_refund = gross_tax - taxes_paid + total_interest
        total = amt_pay_refund + interest_244a()
        final_demand = total + refund_amt
        tax_effect = final_demand - taxorder

        def number_month ():
            due_date_234b = f"{'31/03/'}{ay[0:4]}"
            if self_ass_tax>0:
                month = f"{diff_month(self_ass_date, due_date_234b)}{'+'}{diff_month(order,self_ass_date)}"
                return month
            else: 
                month = diff_month(order, due_date_234b)
                return month

        due_date_234b = f"{'31/03/'}{ay[0:4]}"

        results = f""" Computation of Income Tax
            Name of the Assessee: {name} 
            PAN: {pan}
            A.Y.: {ay}
            Date of order: {order} 
            Total income: {income}
            Special Income to be taxable u/s 115BBE: {s_income}
            Capital Gain: 1. LTCG: {ltcg_income}
                          2. STCG: {stcg_income}
            Agriculture Income: {ag_income}
            Aggregate income: {normal_income}
            Tax on Normal Income: {normal_tax(normal_income)}
            Tax on special income to be taxabel u/s 115BBE: {special_tax()}
            Tax on special income other 115BBE: {capital_tax()}
            Rebate on Agriculture Income: {rebate()}
            Rebate u/s 87A if any: {rebate_87a()}
            Total Tax: {total_tax}
            Surcharge on special income (115BBE): {special_surcharge()}
            Surcharge on other income: {normal_surcharge()}
            Health and Education cess: {cess()}
            Gross Tax: {gross_tax}
            Taxes paid: 
                1.TDS: {tds}
                2.TCS1: {tcs}
                3.Advance Tax: {advtax}
                4.Self Assessment Tax: {self_ass_tax}
                Total Taxes Paid: {taxes_paid}
            Interest: 
                1. 234A: {interest_234a()} No. of Months: {diff_month(itr, extended_due_date())}
                2. 234B: {interest_234b()} No. of Months: {number_month()}
                3. 234C: {interest_234c}
                4. 234D: {interest_234d()} No. of Months: {diff_month(order, refund)}
                5. 234F: {penalty_234f}
                Total Interest: {total_interest}
            Total amount payable/refundable: {amt_pay_refund}
            Interest u/s 244a: {interest_244a()} No. of Months: {diff_month(order, due_date_234b)}
            Total : {total}
            Refund already issued: {refund_amt}
            Final Tax : {final_demand}
            Tax as per Order: {taxorder}
            Tax effect: {tax_effect}
            """

        #return jsonify({"answer" : results})
    
        # CSS for a professional report look
        style = """
        <style>
            .tax-report { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; color: #333; margin: 20px 0; border: 1px solid #ccc; }
            .tax-report th { background-color: #2c3e50; color: white; padding: 12px; text-align: left; text-transform: uppercase; letter-spacing: 1px; }
            .tax-report td { padding: 10px; border-bottom: 1px solid #eee; }
            .tax-report tr:nth-child(even) { background-color: #f9f9f9; }
            .tax-report .section-header { background-color: #ecf0f1; font-weight: bold; color: #2c3e50; }
            .tax-report .total-row { background-color: #e8f4fd; font-weight: bold; border-top: 2px solid #2c3e50; border-bottom: 2px solid #2c3e50; }
            .tax-report .highlight { color: #d35400; font-weight: bold; }
            .tax-report .refund { color: #27ae60; font-weight: bold; }
        </style>
        """

        # HTML Table Construction
        table_html = f"""
        {style}
        <table class="tax-report">
            <thead>
                <tr><th colspan="2">Computation of Income Tax</th></tr>
            </thead>
            <tbody>
                <tr class="section-header"><td colspan="3">Assessee Details</td></tr>
                <tr><td><b>Name</b></td><td>{name}</td></tr>
                <tr><td><b>PAN</b></td><td>{pan}</td></tr>
                <tr><td><b>A.Y.</b></td><td>{ay}</td></tr>
                <tr><td><b>Regular Assessment Order Date</b></td><td>{order}</td></tr>
                
                <tr class="section-header"><td colspan="3">Income Breakdown</td></tr>
                <tr><td>Total Income</td><td>{income}</td></tr>
                <tr><td>Special Income (u/s 115BBE)</td><td>{s_income}</td></tr>
                <tr><td>Capital Gains ((a)LTCG / (b)STCG)</td><td>(a){ltcg_income} / (b){stcg_income}</td></tr>
                <tr><td>Agriculture Income</td><td>{ag_income}</td></tr>
                <tr><td>Aggregate Income</td><td>{normal_income}</td></tr>
                
                <tr class="section-header"><td colspan="3">Tax Computation</td></tr>
                <tr><td>Tax on Normal Income</td><td>{normal_tax(normal_income)}</td></tr>
                <tr><td>Tax on Special Income (115BBE)</td><td>{special_tax()}</td></tr>
                <tr><td>Tax on Capital Gain</td><td>{capital_tax()}</td></tr>
                <tr><td>Rebate on Agriculture Income</td><td>{rebate()}</td></tr>
                <tr class="total-row"><td><b>Total Tax Liability</b></td><td>{total_tax}</td></tr>
                <tr><td>Rebate u/s 87A</td><td>{rebate_87a()}</td></tr>                
                <tr><td>25% Surcharge on Special Income</td><td>{special_surcharge()}</td></tr>
                <tr><td>Surcharge on normal income</td><td>{normal_surcharge()}</td></tr>
                <tr><td>Health and Education Cess</td><td>{cess()}</td></tr>
                <tr class="total-row"><td><b>Gross Tax Payable</b></td><td>{gross_tax}</td></tr>

                <tr class="section-header"><td colspan="3">Taxes Paid & Interest</td></tr>
                <tr><td>Taxe Deducted at Source (TDS)</td><td>{tds}</td></tr>
                <tr><td>Taxe Collected at Source (TCS)</td><td>{tcs}</td></tr>
                <tr><td>Advance Tax Paid</td><td>{advtax}</td></tr>
                <tr><td>Self Assessment Tax Paid</td><td>{self_ass_tax}</td></tr>
                <tr><td>Total Taxes Paid</td><td>{taxes_paid}</td></tr>
                <tr><td>Interest u/s 234A</td><td>{interest_234a()}</td></tr>
                <tr><td>Interest u/s 234B</td><td>{interest_234b()}</td></tr>
                <tr><td>Interest u/s 234C</td><td>{interest_234c}</td></tr>
                <tr><td>Interest u/s 234D</td><td>{interest_234d()}</td></tr>
                <tr><td>Interest u/s 234F</td><td>{penalty_234f()}</td></tr>
                <tr><td>Total Interest</td><td>{total_interest}</td></tr>
                
                <tr class="section-header"><td colspan="3">Tax Payable/Refundable</td></tr>
                <tr><td>Total amount payable/refundable</td><td>{amt_pay_refund}</td></tr>
                <tr><td>Interest u/s 244A</td><td>{interest_244a()}</td></tr>
                <tr><td>Total Tax</td><td>{total}</td></tr>
                <tr><td>Refund Already Issued</td><td>{refund_amt}</td></tr>
                <tr><td>Final Tax</td><td>{final_demand}</td></tr>
                <tr><td>Tax as per Order</td><td>{taxorder}</td></tr>
                <tr><td>Tax Effect</td><td>{tax_effect}</td></tr>

                <tr class="total-row">
                    <td><b>Final Amount Payable / <span class="refund">Refund</span></b></td>
                    <td class="{"refund" if "Refund" in str(amt_pay_refund) else "highlight"}">{amt_pay_refund}</td>
                </tr>
            </tbody>
        </table>
        """

        return jsonify({"answer": table_html})
    

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5001)
