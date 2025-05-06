from flask import Flask, request, send_file
import pdfplumber
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    filename = secure_filename(file.filename)

    tables = []
    with pdfplumber.open(file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            for table_index, table in enumerate(page.extract_tables(), 1):
                df = pd.DataFrame(table)
                df.insert(0, "Page", page_num)
                df.insert(1, "Table Number", table_index)
                tables.append(df)

    if not tables:
        return 'No tables found.', 400

    final_df = pd.concat(tables, ignore_index=True)
    output_path = f"/tmp/{filename}.xlsx"
    final_df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)