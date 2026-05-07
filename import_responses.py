import pandas as pd
from cat.models import Response

FILE = r"C:\Users\arsha\Downloads\responses_100.csv"

try:
    df = pd.read_csv(FILE)
except:
    try:
        df = pd.read_csv(FILE, sep="\t")
    except:
        df = pd.read_excel(FILE)

print("Loaded:", df.shape)
print(df.head())

student_col = df.columns[0]

Response.objects.all().delete()

count = 0

for _, row in df.iterrows():
    student_id = str(row[student_col])
    answers = {}

    for col in df.columns[1:]:
        val = row[col]

        if pd.isna(val):
            val = 0

        answers[col.lower()] = int(val)

    Response.objects.create(
        student=student_id,
        responses=answers
    )

    count += 1

print("Imported students:", count)