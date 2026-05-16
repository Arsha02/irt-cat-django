from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Item
from .serializers import ItemSerializer
from .engine import next_item, estimate_theta

MAX_ITEMS = 10


def get_bank():
    return {str(i.item_id): {'a': i.a, 'b': i.b, 'c': i.c} for i in Item.objects.all()}


@api_view(['GET', 'POST'])
def test_api(request):
    s = request.session
    if 'res' not in s:
        s['res'], s['theta'], s['count'], s['done'], s['current_q'] = {
        }, 0.0, 0, False, None

    if s['done']:
        return Response({"status": "completed", "final_score": round(s['theta'], 2)})

    BANK = get_bank()

    if request.method == "POST":
        q_id = str(request.data.get('q_id', '')).strip()
        ans = str(request.data.get('ans', '')).strip().upper()

        if not q_id or not ans:
            return Response({"error": "Fields required"}, status=status.HTTP_400_BAD_REQUEST)

        if s['current_q'] and q_id != s['current_q']:
            return Response({"error": f"Answer active question: {s['current_q']}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Item.objects.get(item_id=q_id)
            s['res'][q_id] = 1 if ans == item.correct_option.upper() else 0
            s['theta'] = estimate_theta(s['res'], BANK)
            s['count'] += 1
            s.modified = True
        except Item.DoesNotExist:
            return Response({"error": "Invalid q_id"}, status=status.HTTP_400_BAD_REQUEST)

    if s['count'] >= MAX_ITEMS:
        s['done'] = True
        s.modified = True
        return Response({"status": "completed", "final_score": round(s['theta'], 2), "total_items": MAX_ITEMS})

    next_id = s['current_q'] if request.method == "GET" and s['current_q'] else next_item(
        s['theta'], BANK, list(s['res'].keys()))
    if not next_id:
        s['done'], s.modified = True, True
        return Response({"status": "completed", "final_score": round(s['theta'], 2)})

    s['current_q'], s.modified = next_id, True
    return Response({"status": "ongoing", "progress": s['count'] + 1, "question": ItemSerializer(Item.objects.get(item_id=next_id)).data})


@api_view(['POST'])
def reset_test(request):
    request.session.flush()
    return Response({"status": "reset"})
