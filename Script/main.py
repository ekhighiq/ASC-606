#Importing Required Libraries
from taipy.gui import Gui, navigate
import taipy.gui.builder as tgb
import pandas as pd
from pathlib import Path
import os
import json
from datetime import datetime
import re

# ----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------Defining Functions-----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def get_filtered_data(company):
    return df[df["Customer_Name"] == company]

def format_date(value, out_format="%d-%b-%y"):
    try:
        # Try parsing in common formats (add more if needed)
        date = pd.to_datetime(value, errors='coerce')
        if pd.isnull(date):
            return "NA"
        return date.strftime(out_format)
    except:
        return "NA"

def parse_json_column(cell_value):
    try:
        parsed = json.loads(cell_value)
        if isinstance(parsed, list) and all(isinstance(item, dict) for item in parsed):
            return pd.DataFrame(parsed)
        else:
            return pd.DataFrame([{"Error": "Invalid format"}])
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])
    
def format_currency(value):
    try:
        if isinstance(value, str):
            # Remove any non-digit, non-dot, non-comma, non-minus characters
            value = re.sub(r"[^\d\.-]", "", value)
        num = float(value)
        return f"${num:,.2f}"
    except:
        return "NA"
    
def show_column_as_table(state, column_name):
    tables = []
    for _, row in state.filtered_df.iterrows():
        cell = row[column_name]
        parsed = parse_json_column(cell)
        tables.append(parsed)
    if tables:
        state.display_df = pd.concat(tables, ignore_index=True)
    else:
        state.display_df = pd.DataFrame([{"Info": "No data available"}])

def show_products_service(state):
    show_column_as_table(state, "Products_and_Services")

def show_license_details(state):
    show_column_as_table(state, "Type_of_License")

def show_performance_obligations(state):
    show_column_as_table(state, "Performance_Obligations")

def show_variable_considerations(state):
    show_column_as_table(state, "Variable_Consideration")

def show_payment_schedules(state):
    show_column_as_table(state, "Payment_Schedules")
    
def update_data(state):
    state.filtered_df = get_filtered_data(state.selected_company)
    
    row = df[df["Customer_Name"] == state.selected_company].iloc[0]
    
    state.ctr_term = row["Contract_Term"]
    state.tot_ctr_val = format_currency(row["Total_Contract_Value"])
    state.ctr_cre_dt = format_date(row["Contract_Creation_Date"])
    state.rev_str_dt = format_date(row["Revenue_Start_Date"])
    state.rev_end_dt = format_date(row["Revenue_End_Date"])
    state.all_tra_prc = format_currency(row["Allocated_Transaction_Price"])
    state.bill_freq = row["Billing_Frequency_and_Amount"]
    state.sta_sell_price = row["Standalone_Selling_Price"]
    state.ctr_mods = row["Contract_Modifications"]
    state.ren_det = row["Renewal_Details"]
    
    try:
        contract_dates = json.loads(row["Contract_Effective_Date"])
        if isinstance(contract_dates, list) and len(contract_dates) > 0:
            state.ctr_eff_dt = format_date(contract_dates[0].get("Contract Effective Date", "N/A"))
            state.ctr_sign_dt = format_date(contract_dates[0].get("Contract Signing Date", "N/A"))
        else:
            state.ctr_eff_dt = "Invalid Format"
            state.ctr_sign_dt = "Invalid Format"
    except Exception as e:
        state.ctr_eff_dt = f"Error: {e}"
        state.ctr_sign_dt = f"Error: {e}"
    
    show_products_service(state)

# ----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------Variable Selection-----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

current_dir = Path.cwd()
# data_path = current_dir.parents[1] / 'ASC-606' /'Source_Data'
data_path = current_dir.parents[1] / 'Source_Data'
datafile = os.path.join(data_path, "ai_hub_output.csv" )
df = pd.read_csv(datafile)
df = df.astype("object")
df.fillna("NA", inplace=True)

company_list = sorted(df["Customer_Name"].dropna().unique())
selected_company = "Evertz Microsystems, Ltd." #company_list[0]

filtered_df = get_filtered_data(selected_company)

display_df = parse_json_column(filtered_df["Products_and_Services"].iloc[0])

ctr_term = df[df["Customer_Name"] == selected_company]["Contract_Term"].iloc[0]
tot_ctr_val = format_currency(df[df["Customer_Name"] == selected_company]["Total_Contract_Value"].iloc[0])
ctr_cre_dt = format_date(df[df["Customer_Name"] == selected_company]["Contract_Creation_Date"].iloc[0])
rev_str_dt = format_date(df[df["Customer_Name"] == selected_company]["Revenue_Start_Date"].iloc[0])
rev_end_dt = format_date(df[df["Customer_Name"] == selected_company]["Revenue_End_Date"].iloc[0])
all_tra_prc = format_currency(df[df["Customer_Name"] == selected_company]["Allocated_Transaction_Price"].iloc[0])
bill_freq = df[df["Customer_Name"] == selected_company]["Billing_Frequency_and_Amount"].iloc[0]
sta_sell_price = df[df["Customer_Name"] == selected_company]["Standalone_Selling_Price"].iloc[0]
ctr_mods = df[df["Customer_Name"] == selected_company]["Contract_Modifications"].iloc[0]
ren_det = df[df["Customer_Name"] == selected_company]["Renewal_Details"].iloc[0]

contract_dates_json = df[df["Customer_Name"] == selected_company]["Contract_Effective_Date"].iloc[0]

try:
    contract_dates = json.loads(contract_dates_json)
    if isinstance(contract_dates, list) and len(contract_dates) > 0:
        ctr_eff_dt = format_date(contract_dates[0].get("Contract Effective Date", "N/A"))
        ctr_sign_dt = format_date(contract_dates[0].get("Contract Signing Date", "N/A"))
    else:
        ctr_eff_dt = "Invalid Format"
        ctr_sign_dt = "Invalid Format"
except Exception as e:
    ctr_eff_dt = f"Error: {e}"
    ctr_sign_dt = f"Error: {e}"

# ----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------Filter Panel--------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def filter_panel():
    with tgb.layout("1"):
        with tgb.part():
            tgb.selector(value="{selected_company}", lov=company_list, dropdown=True, label="Select Company", on_change=update_data)
            tgb.html('br')
        with tgb.part():
            tgb.text("Contract Term")
            tgb.text("{ctr_term}")
            tgb.html('br')
        with tgb.part():
            tgb.text("Total Contract Value")
            tgb.text("{tot_ctr_val}")
            tgb.html('br')
        with tgb.part():
            tgb.text("Contract Creation Date")
            tgb.text("{ctr_cre_dt}")
            tgb.html('br')
        with tgb.part():
            with tgb.layout("1 1"):
                tgb.text("Contract Effective Date")
                tgb.text("Contract Signing Date")
                tgb.text("{ctr_eff_dt}")
                tgb.text("{ctr_sign_dt}")
            tgb.html('br')
        with tgb.part():
            with tgb.layout("1 1"):
                tgb.text("Revenue Start Date")
                tgb.text("Revenue End Date")
                tgb.text("{rev_str_dt}")
                tgb.text("{rev_end_dt}")
            tgb.html('br')
        with tgb.part():
            tgb.text("Allocated Transaction Price")
            tgb.text("{all_tra_prc}")
            tgb.html('br')
        with tgb.part():
            tgb.text("Billing Frequency and Amount")
            tgb.text("{bill_freq}")
            tgb.html('br')

# ----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------Dashboard Data--------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
 
with tgb.Page() as data_page:
            with tgb.layout("1 4"):
                with tgb.part("card"):
                    filter_panel()
                with tgb.part():
                    with tgb.layout("1 1 1 1 1"):
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Product and Services", on_action="show_products_service", class_name="buttons")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Type of License", on_action="show_license_details", class_name="buttons")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Performance Obligations", on_action="show_performance_obligations", class_name="buttons")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Variable Consideration", on_action="show_variable_considerations", class_name="buttons")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Payment Schedules", on_action="show_payment_schedules", class_name="buttons")
                    
                    with tgb.part("card"):
                        tgb.table("{display_df}", rebuild=True)    
                    tgb.html("br")   
                    
                    with tgb.layout("1 1 1"):
                        with tgb.part("card"):
                            tgb.text("Standalone Selling Price")
                            tgb.text("{sta_sell_price}")
                        with tgb.part("card"):
                            tgb.text("Contract Modifications")
                            tgb.text("{ctr_mods}")
                        with tgb.part("card"):
                            tgb.text("Renewal Details")
                            tgb.text("{ren_det}")
                    
                        
pages = {
        "Data": data_page,
    }

if __name__ == "__main__":
    gui = Gui(pages=pages, css_file="style.css")
    gui.run(host="0.0.0.0", port=5003, use_reloader=False, dark_mode=False, title="ASC 606 Dashboard")