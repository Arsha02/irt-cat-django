import json
from cat.models import Item

# open json
with open("questions.json", "r") as f:
    data = json.load(f)

# clear old items (optional)
Item.objects.all().delete()

# import
for item_id, values in data.items():
    Item.objects.create(
        item_id=item_id.upper(),   # q16 -> Q16
        a=values["a"],
        b=values["b"],
        c=values["c"]
    )

print("Questions imported successfully")

