import json
from cat.models import Item

with open('question_bank_100.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for x in data:
    Item.objects.update_or_create(
        item_id=x['id'],
        defaults={
            'question_text': x['question'],
            'options': x['options'],
            'correct_option': x['correct'],
            'a': x['discrimination_a'],
            'b': x['difficulty_b'],
            'c': x['guessing_c']
        }
    )

print("Successfully imported all 100 questions into the DB!")
