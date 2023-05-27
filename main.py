from flask import Flask, request, jsonify
import sqlite3
import pandas as pd


app = Flask(__name__)
app.json.sort_keys = False

#Reading File
f=pd.read_excel('testfile.xls')
a='API WELL  NUMBER'

#Creating DataFrame
df=pd.DataFrame(f,columns=[a,'OIL','GAS','BRINE'])
#print(df)

#Grouping and finding sum based on 'API WELL NUMBER'
df2=df.groupby(a).sum()
#print(df2)

#SQLite Connection and Table Creation
conn=sqlite3.connect('inerg.db',check_same_thread=False)
create_sql='CREATE TABLE IF NOT EXISTS interview(number INTEGER UNIQUE,oil INTEGER,gas INTEGER,brine INTEGER)'
cursor=conn.cursor()
cursor.execute(create_sql)
for row in df2.itertuples():
    insert_sql="INSERT OR REPLACE INTO interview VALUES("+str(row[0])+","+str(row[1])+","+str(row[2])+","+str(row[3])+")"
    cursor.execute(insert_sql)
conn.commit()

#Endpoint for retrieving well data
@app.route('/data', methods=['GET'])
def get_annual_data():
    well_id = request.args.get('well')
    if not well_id:
        return jsonify({'error': 'Well ID is required.'}), 400

    try:
    #SQLite query for well data
        cursor=conn.cursor()
        query = "SELECT oil, gas, brine FROM interview WHERE number = "+str(well_id)+""
        cursor.execute(query)
        result = cursor.fetchone()


        if not result:
            return jsonify({'error': 'No data found for the provided well ID.'}), 404

        #Return data as JSON
        data = {
            'oil': result[0],
            'gas': result[1],
            'brine': result[2]
        }
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8080)
