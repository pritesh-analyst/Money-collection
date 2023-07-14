
import pandas as pd
import streamlit as st
import pickle

def getmoney(date1, checkbox_states):
    sheet_id = "1NikKhqY7u3AGsm9Fpk9UaqNFyzmyojuz8-iqUGh295g"
    sheet_data = "Form Responses 1"

    gsheet_data = "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}".format(sheet_id, sheet_data)

    url = gsheet_data.replace(" ", "")
    df = pd.read_csv(url, on_bad_lines='skip')
    df = df.iloc[:, :24].fillna('')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Battery In Voltage'] = pd.to_numeric(df['Battery In Voltage'])
    df['Battery Out Voltage'] = pd.to_numeric(df['Battery Out Voltage'])
    df['Amount '] = pd.to_numeric(df['Amount '])
    df['Parking amount ?'] = pd.to_numeric(df['Parking amount ?'])
    df['Pick and drop amount ?'] = pd.to_numeric(df['Pick and drop amount ?'])

    data = pd.DataFrame({
        'Timestamp': df['Timestamp'],
        'Customer name': df['Customer name'],
        'Battery_in': df['Battery In'],
        'Battery_in_volt': df['Battery In Voltage'],
        'Battery_out': df['Battery Out'],
        'Battery_Out_volt': df['Battery Out Voltage'],
        'Amount': df['Amount '],
        'Security_amt': df['Security Amount'],
        'Penalty_amt': df['Penalty Amount '],
        'Supervisor': df['Shift supervisor'],
        'Plan': df['Is there any plan?'],
        'Battery_submit?': df['Is the customer submitting or collecting battery?'],
        'Center': df['Center'],
        'Mode of payment': df['Mode of payment'],
        'Parking': df['Parking amount ?'],
        'Pick_and_drop': df['Pick and drop amount ?']
    })

    data['Date'] = pd.to_datetime(data['Timestamp'].dt.date)
    filtered_data = data[data['Date'] == pd.Timestamp(date1)]

    dict_for_money = {'Date': [], 'Cash': [], 'Online': [], 'Cash and online': [], 'Parking': [], 'Pick_and_drop': [], 'Supervisor': []}

    dates = filtered_data['Date'].unique()

    for date in dates:
        cash = filtered_data.loc[(filtered_data['Mode of payment'] == 'Cash') & (filtered_data['Date'] == date)]
        online = filtered_data.loc[(filtered_data['Mode of payment'] == 'Bharat pe') & (filtered_data['Date'] == date)]
        cash_and_online = filtered_data.loc[(filtered_data['Mode of payment'] == 'Cash + Bharat pe') & (filtered_data['Date'] == date)]

        supervisors = filtered_data.loc[filtered_data['Date'] == date, 'Supervisor']

        for supervisor in supervisors:
            dict_for_money['Date'].append(date)
            dict_for_money['Cash'].append(cash.loc[cash['Supervisor'] == supervisor, 'Amount'].sum())
            dict_for_money['Online'].append(online.loc[online['Supervisor'] == supervisor, 'Amount'].sum())
            dict_for_money['Cash and online'].append(cash_and_online.loc[cash_and_online['Supervisor'] == supervisor, 'Amount'].sum())
            dict_for_money['Parking'].append(filtered_data.loc[(filtered_data['Date'] == date) & (filtered_data['Supervisor'] == supervisor), 'Parking'].sum())
            dict_for_money['Pick_and_drop'].append(filtered_data.loc[(filtered_data['Date'] == date) & (filtered_data['Supervisor'] == supervisor), 'Pick_and_drop'].sum())
            dict_for_money['Supervisor'].append(supervisor)

    money_collection = pd.DataFrame(dict_for_money).drop_duplicates().reset_index(drop=True)
    money_collection['Received'] = False

    for index, row in money_collection.iterrows():
        key = f"{row['Supervisor']}_{row['Date'].date()}"
        received = st.checkbox(f"Have you received the money from: {row['Supervisor']}?", key=key, value=checkbox_states.get(key, False))
        checkbox_states[key] = received
        if received:
            money_collection.at[index, 'Received'] = True

    money_collection['Total'] = money_collection['Cash'] + money_collection['Online'] + money_collection['Cash and online'] + money_collection['Parking'] + money_collection['Pick_and_drop']

    return money_collection


def main():
    st.set_page_config(page_title="Model for Money collection", layout="wide")
    st.title('Money Collection Dashboard')

    date1 = st.sidebar.date_input("Select a date")

    checkbox_states = {}  # Initialize checkbox_states as an empty dictionary

    try:
        # Load checkbox states from file if it exists
        with open("checkbox_states.pkl", "rb") as f:
            checkbox_states = pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError):
        pass

    result = getmoney(date1, checkbox_states)
    st.write(result)

    # Update checkbox states based on user input
    # for index, row in result.iterrows():
    #     key = f"{row['Supervisor']}_{row['Date'].date()}"
    #     received = st.checkbox(f"Have you received the money from: {row['Supervisor']}?", value=checkbox_states.get(key, False))
    #     checkbox_states[key] = received

    # Save checkbox states to file
    with open("checkbox_states.pkl", "wb") as f:
        pickle.dump(checkbox_states, f)

if __name__ == '__main__':
    main()
