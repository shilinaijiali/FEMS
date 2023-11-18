from django.http import JsonResponse
from CMSapp.models import TypeDefinition, ConsumableType


def get_version_list(request):
    select_id = request.GET.get('select_id')   # 传回来的是ConsumableType表中的id
    name = ConsumableType.objects.filter(id=select_id).first().name
    if name:
        qs = TypeDefinition.objects.filter(typegroup__ConsumableType__name=name, typegroup__name='{}Version'.format(name))
        choices = [{'value': obj.pk, 'label': str(obj)} for obj in qs]
        return JsonResponse(choices, safe=False)
    else:
        return JsonResponse([], safe=False)


def get_tooltype_list(request):
    select_id = request.GET.get('select_id')  # 传回来的是ConsumableType表中的id
    name = ConsumableType.objects.filter(id=select_id).first().name
    if name:
        qs = TypeDefinition.objects.filter(typegroup__ConsumableType__name=name, typegroup__name='{}Type'.format(name))
        choices = [{'value': obj.pk, 'label': str(obj)} for obj in qs]
        return JsonResponse(choices, safe=False)
    else:
        return JsonResponse([], safe=False)


def get_model_list(request):
    select_id = request.GET.get('select_id')  # 传回来的是ConsumableType表中的id
    name = ConsumableType.objects.filter(id=select_id).first().name
    if name:
        qs = TypeDefinition.objects.filter(typegroup__ConsumableType__name=name, typegroup__name='{}Model'.format(name))
        choices = [{'value': obj.pk, 'label': str(obj)} for obj in qs]
        return JsonResponse(choices, safe=False)
    else:
        return JsonResponse([], safe=False)
