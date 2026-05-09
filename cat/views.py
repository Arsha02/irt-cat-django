import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Item
from .engine import next_item, mle, se


@csrf_exempt
def test(request):
    s = request.session
    # Initialize the test if it's new
    if 'res' not in s:
        s['res'], s['theta'], s['count'], s['log'] = {}, 0.0, 0, ""

    # Load questions from Database
    items = Item.objects.all()
    BANK = {i.item_id.lower(): {'a': i.a, 'b': i.b, 'c': i.c} for i in items}

    # Handle the user's answer
    if request.method == "POST":
        q_id = request.POST.get('q_id', '').lower()
        ans = request.POST.get('ans')

        if ans in ['0', '1'] and q_id in BANK:
            if q_id not in s['res']:
                s['res'][q_id] = int(ans)
                s['theta'] = mle(s['res'], BANK)
                curr_se = se(s['theta'], s['res'].keys(), BANK)
                s['count'] += 1

                # Add to the history log
                s['log'] += (f"ID: {q_id.upper()} | Ans: {ans} | Theta: {round(s['theta'], 2)}\n")
                s.modified = True

    # End the test after 10 questions
    if s['count'] >= 10:
        return HttpResponse(f"""
            <body style="font-family:monospace; background:#000; color:#fff;">
                <pre>{s['log']}</pre>
                <p>TEST FINISHED. Final Theta: {round(s['theta'], 2)}</p>
                <a href="/reset/" style="color:#fff;">Restart Test</a>
            </body>
        """)

    # Get the next question
    next_q_id = next_item(s['theta'], BANK, list(s['res'].keys()))
    q_obj = Item.objects.filter(item_id__iexact=next_q_id).first()

    # Display the current screen
    return HttpResponse(f"""
        <body style="font-family:monospace; background:#000; color:#fff; padding:20px;">
            <pre>{s['log']}</pre>
            <p>Question: {q_obj.question_text}</p>
            <form method="POST">
                <input type="hidden" name="q_id" value="{next_q_id}">
                Answer (1/0): <input type="text" name="ans" autofocus maxlength="1" 
                                     style="background:#000; color:#fff; border:none; border-bottom:1px solid #fff;">
            </form>
        </body>
    """)


def reset_test(request):
    request.session.flush()
    return redirect('/test/')
