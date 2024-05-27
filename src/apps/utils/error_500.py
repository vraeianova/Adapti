from django.shortcuts import render


def handler500(request, exception=None):

    return render(request, "errors/500.html", {}, status=500)
