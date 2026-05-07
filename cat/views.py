from django.http import HttpResponse
from .models import Item, Response
from .engine import next_item, mle, se


def bank():
    return {
        i.item_id.lower(): {"a": i.a, "b": i.b, "c": i.c}
        for i in Item.objects.all()
    }


def run(student, b):
    theta, ans, resp, out = 0, [], {}, ""

    for i in range(30):

        q = next_item(theta, b, ans)
        if not q:
            break

        s = int(student.responses[q])
        ans.append(q)
        resp[q] = s

        old = theta
        theta = mle(resp, b)
        err = se(theta, ans, b)

        out += f"{i+1}. {q} {'C' if s else 'W'} {old}->{theta} SE:{err}\n"

        # stop only when estimate is precise
        if err < 0.35:
            out += "Ability estimated confidently\n"
            break

    return out + f"\nFinal:{theta}  Questions:{len(ans)}"


def student(request, student_id):
    s = Response.objects.get(student=str(student_id))
    return HttpResponse(run(s, bank()), content_type="text/plain")


def all_students(request):
    out = ""
    b = bank()

    for s in Response.objects.all():
        out += f"Student {s.student}\n"
        out += run(s, b) + "\n\n"

    return HttpResponse(out, content_type="text/plain")
