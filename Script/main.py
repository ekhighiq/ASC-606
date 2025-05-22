#Importing Required Libraries
from taipy.gui import Gui, navigate
import taipy.gui.builder as tgb
import pandas as pd
from pathlib import Path
import os
import json
from datetime import datetime
import re

# ------------------------ Defining Functions ----------------------

def get_filtered_data(company):
    return df[df["Customer_Name"] == company]

def format_date(value, out_format="%d-%b-%y"):
    try:
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
            value = re.sub(r"[^\d\.-]", "", value)
        num = float(value)
        return f"${num:,.2f}"
    except:
        return "NA"

def format_contract_term(term):
    if not isinstance(term, str):
        return "NA"

    term = term.lower()

    # Try to extract a number (either digit or word)
    digit_match = re.search(r"(\d+)", term)

    number = int(digit_match.group(1))

    # Determine unit (month/year)
    if "month" in term:
        unit = "Months"
    elif "year" in term:
        unit = "Years"
    else:
        unit = "Units"

    return f"{number} {unit}" if number else "NA"

def clean_asterisks(text):
    if isinstance(text, str):
        return re.sub(r"\*\*", "", text)
    return text
    
def set_button_classes(state, active_button):
    base = "buttons"
    btns = [
        "products_class", "license_class", "performance_class", "variable_class",
        "payment_class", "std_sell_price", "contract_mod", "renewal_details"
    ]
    for btn in btns:
        setattr(state, btn, f"{base} active" if btn == active_button else base)

def show_column_as_table(state, column_name):
    tables = []
    for _, row in state.filtered_df.iterrows():
        cell = row[column_name]
        parsed = parse_json_column(cell)
        tables.append(parsed)
    state.display_df = pd.concat(tables, ignore_index=True) if tables else pd.DataFrame([{"Info": "No data available"}])

def show_single_value(state, label, value):
    state.display_df = pd.DataFrame([{label: value}])

# ------------------------ Button Action Functions ----------------------

def show_products_service(state):
    set_button_classes(state, "products_class")
    show_column_as_table(state, "Products_and_Services")

def show_license_details(state):
    set_button_classes(state, "license_class")
    show_column_as_table(state, "Type_of_License")

def show_performance_obligations(state):
    set_button_classes(state, "performance_class")
    show_column_as_table(state, "Performance_Obligations")

def show_variable_considerations(state):
    set_button_classes(state, "variable_class")
    show_column_as_table(state, "Variable_Consideration")

def show_payment_schedules(state):
    set_button_classes(state, "payment_class")
    show_column_as_table(state, "Payment_Schedules")

def show_standalone_price(state):
    set_button_classes(state, "std_sell_price")
    show_single_value(state, "Standalone Selling Price", state.sta_sell_price)

def show_contract_modifications(state):
    set_button_classes(state, "contract_mod")
    show_single_value(state, "Contract Modifications", state.ctr_mods)

def show_renewal_details(state):
    set_button_classes(state, "renewal_details")
    show_single_value(state, "Renewal Details", state.ren_det)

# ------------------------ State Update Function ----------------------
    
def update_data(state):
    state.filtered_df = get_filtered_data(state.selected_company)
    
    state.row = df[df["Customer_Name"] == state.selected_company].iloc[0]
    
    state.ctr_term = format_contract_term(state.row["Contract_Term"])
    state.tot_ctr_val = format_currency(state.row["Total_Contract_Value"])
    state.ctr_cre_dt = format_date(state.row["Contract_Creation_Date"])
    state.rev_str_dt = format_date(state.row["Revenue_Start_Date"])
    state.rev_end_dt = format_date(state.row["Revenue_End_Date"])
    state.all_tra_prc = format_currency(state.row["Allocated_Transaction_Price"])
    state.bill_freq = state.row["Billing_Frequency_and_Amount"]
    state.sta_sell_price = clean_asterisks(state.row["Standalone_Selling_Price"])
    state.ctr_mods = clean_asterisks(state.row["Contract_Modifications"])
    state.ren_det = clean_asterisks(state.row["Renewal_Details"])
    
    try:
        contract_dates = json.loads(state.row["Contract_Effective_Date"])
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

# ------------------------ Data Initialization ----------------------

current_dir = Path.cwd()
# data_path = current_dir.parents[1] / 'ASC-606' /'Source_Data'
data_path = Path("Source_Data")
datafile = os.path.join(data_path, "ai_hub_output.csv" )
df = pd.read_csv(datafile)
df = df.astype("object")
df.fillna("NA", inplace=True)

# logo_path = current_dir.parents[1] / 'ASC-606' /'Logos'
logo_path = Path("Logos")
logo_1 = os.path.join(logo_path, "HighIQ_Logo.jpg" )
logo_2 = os.path.join(logo_path, "InstaBase_Logo.jpg" )

company_list = sorted(df["Customer_Name"].dropna().unique())
selected_company = company_list[0]

filtered_df = get_filtered_data(selected_company)

display_df = parse_json_column(filtered_df["Products_and_Services"].iloc[0])

row = df[df["Customer_Name"] == selected_company]

ctr_term = format_contract_term(row["Contract_Term"].iloc[0])
tot_ctr_val = format_currency(row["Total_Contract_Value"].iloc[0])
ctr_cre_dt = format_date(row["Contract_Creation_Date"].iloc[0])
rev_str_dt = format_date(row["Revenue_Start_Date"].iloc[0])
rev_end_dt = format_date(row["Revenue_End_Date"].iloc[0])
all_tra_prc = format_currency(row["Allocated_Transaction_Price"].iloc[0])
bill_freq = row["Billing_Frequency_and_Amount"].iloc[0]
sta_sell_price = clean_asterisks(row["Standalone_Selling_Price"].iloc[0])
ctr_mods = clean_asterisks(row["Contract_Modifications"].iloc[0])
ren_det = clean_asterisks(row["Renewal_Details"].iloc[0])

contract_dates_json = row["Contract_Effective_Date"].iloc[0]

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
    
products_class = "buttons active"
license_class = "buttons"
performance_class = "buttons"
variable_class = "buttons"
payment_class = "buttons"
std_sell_price = "buttons"
contract_mod = "buttons"
renewal_details = "buttons"

# ------------------------ UI Definitions ----------------------

# ------------------------ Filter Panel ----------------------

def filter_panel():
    with tgb.layout("1"):
        with tgb.part():
            with tgb.layout('1 1'):
                tgb.image('{logo_1}', class_name="logo1")
                tgb.image('{logo_2}', class_name="logo2")
            tgb.html('br')
        with tgb.part():    
            tgb.selector(value="{selected_company}", 
                         lov=company_list, 
                         dropdown=True, 
                        #  label="Select Company",                          
                         on_change=update_data)
            tgb.html('br')
        with tgb.part():
            tgb.text("**Contract Term**", mode='md')
            tgb.text("{ctr_term}")
            tgb.html('br')
        with tgb.part():
            tgb.text("**Total Contract Value**", mode='md')
            tgb.text("{tot_ctr_val}")
            tgb.html('br')
        with tgb.part():
            tgb.text("**Contract Creation Date**", mode='md')
            tgb.text("{ctr_cre_dt}")
            tgb.html('br')
        with tgb.part():
            with tgb.layout("1 1"):
                tgb.text("**Contract Effective Date**", mode='md')
                tgb.text("**Contract Signing Date**", mode='md')
                tgb.text("{ctr_eff_dt}")
                tgb.text("{ctr_sign_dt}")
            tgb.html('br')
        with tgb.part():
            with tgb.layout("1 1"):
                tgb.text("**Revenue Start Date**", mode='md')
                tgb.text("**Revenue End Date**", mode='md')
                tgb.text("{rev_str_dt}")
                tgb.text("{rev_end_dt}")
            tgb.html('br')
        with tgb.part():
            tgb.text("**Allocated Transaction Price**", mode='md')
            tgb.text("{all_tra_prc}")
            tgb.html('br')
        with tgb.part():
            tgb.text("**Billing Frequency and Amount**", mode='md')
            tgb.text("{bill_freq}")
            tgb.html('br')

# ------------------------ Main Dashboard ----------------------
 
with tgb.Page() as data_page:
            with tgb.layout("1 4"):
                with tgb.part("card"):
                    filter_panel()
                with tgb.part('card'):
                    with tgb.layout("1 1 1 1 1 1 1 1"):
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Product and Services", 
                            on_action=show_products_service, 
                            class_name="{products_class}")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Type of License", 
                            on_action=show_license_details, 
                            class_name="{license_class}")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Performance Obligations", 
                            on_action=show_performance_obligations, 
                            class_name="{performance_class}")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Variable Consideration", 
                            on_action=show_variable_considerations, 
                            class_name="{variable_class}")
                        with tgb.part(class_name="data_buttons"):
                            tgb.button("Payment Schedules", 
                            on_action=show_payment_schedules, 
                            class_name="{payment_class}")
                        with tgb.part():
                            tgb.button("Standalone Selling Price", 
                            on_action=show_standalone_price, 
                            class_name="{std_sell_price}")
                        with tgb.part():
                            tgb.button("Contract Modifications", 
                            on_action=show_contract_modifications, 
                            class_name="{contract_mod}")
                        with tgb.part():
                            tgb.button("Renewal Details", 
                            on_action=show_renewal_details, 
                            class_name="{renewal_details}") 
                    tgb.html("br")
                    
                    with tgb.part():
                        tgb.table("{display_df}", 
                                  rebuild=True, 
                                  show_all= True,)    
                    tgb.html("br")  
                                          
pages = {
        "Data": data_page,
    }

if __name__ == "__main__":
    gui = Gui(pages=pages, css_file="style.css")
    gui.run(host="0.0.0.0", 
            port=5003, 
            use_reloader=False, 
            dark_mode=False, 
            title="ASC 606 Dashboard")