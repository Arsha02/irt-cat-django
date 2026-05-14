from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Item
from .serializers import ItemSerializer
from .engine import next_item, mle


@api_view(['GET', 'POST'])
def test_api(request):
    s = request.session

    # 1. Initialize Assessment Session
    if 'res' not in s:
        s['res'], s['theta'], s['count'] = {}, 0.0, 0
        s.modified = True

    # 2. Map Database to Engine Bank Format
    items = Item.objects.all()
    BANK = {i.item_id: {'a': i.a, 'b': i.b, 'c': i.c} for i in items}

    # 3. Handle Answer Submission (POST)
    if request.method == "POST":
        q_id = request.data.get('q_id')
        ans = request.data.get('ans')  # Expects 0 or 1

        if q_id in BANK and ans in [0, 1, "0", "1"]:
            s['res'][q_id] = int(ans)
            s['theta'] = mle(s['res'], BANK)  # Update Ability Score
            s['count'] += 1
            s.modified = True
            return Response({"message": "Answer saved", "progress": s['count']})
        return Response({"error": "Invalid Input"}, status=status.HTTP_400_BAD_REQUEST)

    # 4. Finish Assessment after 10 questions
    if s['count'] >= 10:
        return Response({
            "status": "completed",
            "final_ability_score": s['theta'],
            "total_items": s['count']
        })

    # 5. Fetch Next Adaptive Question (GET)
    next_id = next_item(s['theta'], BANK, list(s['res'].keys()))
    if not next_id:
        return Response({"error": "Bank exhausted"}, status=status.HTTP_404_NOT_FOUND)

    item_obj = Item.objects.get(item_id=next_id)
    serializer = ItemSerializer(item_obj)  # Use serializer for clean JSON

    return Response({
        "status": "ongoing",
        "progress": s['count'],
        # Returns {'item_id': 'q45', 'question_text': '...'}
        "question": serializer.data
    })


@api_view(['GET'])
def reset_test(request):
    request.session.flush()
    return Response({"message": "Assessment Reset Successfully"})
