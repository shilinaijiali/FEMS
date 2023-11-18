from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import gettext, activate
from django.views import View

from CMSapp import models
from CMSapp.common.clsResponse import ResMsg, ViewRes
from CMSapp.common.tools import tool

reply = ResMsg()


class get_sn_list_by_all_type(View):
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            arg = request.POST['arg']
            arg_type = request.POST['type']
            if arg_type == 'status':
                sn_list = list(models.Consumable.objects.filter(status=arg).values_list('sn', flat=True))
                if arg == 'all':
                    sn_list = list(models.Consumable.objects.all().values_list('sn', flat=True))
            else:
                con = Q()
                con.children.append(('{}__name'.format(arg_type), arg))
                sn_list = list(models.Consumable.objects.filter(con).values_list('sn', flat=True))
                if arg == 'all':
                    sn_list = list(models.Consumable.objects.all().values_list('sn', flat=True))
            return JsonResponse(reply.info('', {'sn_list': sn_list}))
        except Exception as e:
            return JsonResponse(reply.error(e))


class get_sn_list_by_mul_condition(View):
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            sn = request.POST['sn']
            tooltype = request.POST['tooltype']
            version = request.POST['version']
            status = request.POST['status']
            model = request.POST['model']
            ConsumableType = request.POST['ConsumableType']
            # 组装查询条件con
            con = Q()
            if sn:
                con.children.append(('sn', sn))
            if tooltype != 'all':
                con.children.append(('tooltype__name', tooltype))
            if version != 'all':
                con.children.append(('version__name', version))
            if status != 'all':
                con.children.append(('status', status))
            if model != 'all':
                con.children.append(('model__name', model))
            if ConsumableType != 'all':
                con.children.append(('ConsumableType__name', ConsumableType))
            sn_list = list(models.Consumable.objects.filter(con).values_list('sn', flat=True))
            return JsonResponse(reply.info('', {'sn_list': sn_list}))
        except Exception as e:
            return JsonResponse(reply.error(e))


class get_all_type_by_ConsumableType(View):
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            ConsumableType = request.POST['ConsumableType']
            TD_objs = models.TypeDefinition.objects.filter()
            version_objs = TD_objs.filter(typegroup__name__endswith='Type')
            type_objs = TD_objs.filter(typegroup__name__endswith='Version')
            model_objs = TD_objs.filter(typegroup__name__endswith='Model')
            if ConsumableType != 'all':
                version_objs = TD_objs.filter(typegroup__name='{}Version'.format(ConsumableType))
                type_objs = TD_objs.filter(typegroup__name='{}Type'.format(ConsumableType))
                model_objs = TD_objs.filter(typegroup__name='{}Model'.format(ConsumableType))
            version_list = list(version_objs.values_list('name', flat=True))
            type_list = list(type_objs.values_list('name', flat=True))
            model_list = list(model_objs.values_list('name', flat=True))
            return JsonResponse(reply.info('', {'version_list': version_list, 'type_list': type_list, 'model_list': model_list}))
        except Exception as e:
            return JsonResponse(reply.error(e))


class get_ConsumableList_by_ConsumableType(View):
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            ConsumableType = request.POST['ConsumableType']
            ConsumableList = []
            Consumable_objs = models.Consumable.objects.all()
            if ConsumableType != 'all':
                Consumable_objs = models.Consumable.objects.filter(ConsumableType__name=ConsumableType).order_by('-updatetime')
            TD_objs = models.TypeDefinition.objects
            CT_objs = models.ConsumableType.objects
            for i in Consumable_objs:
                li = [
                    '', i.sn, gettext(CT_objs.filter(id=i.ConsumableType_id).first().name), TD_objs.filter(id=i.version_id).first().name,
                    TD_objs.filter(id=i.tooltype_id).first().name, TD_objs.filter(id=i.model_id).first().name,
                    gettext(i.status), i.usefullife, i.ratedlife, i.location, i.position
                ]
                ConsumableList.append(li)
            return JsonResponse(reply.info('', {'ConsumableList': ConsumableList}))
        except Exception as e:
            return JsonResponse(reply.error(e))


class get_ConsumableList_by_Other(View):
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            ConsumableType = request.POST['ConsumableType']
            ToolType = request.POST['ToolType']
            Version = request.POST['Version']
            Model = request.POST['Model']
            Status = request.POST['Status']
            ConsumableList = []
            # 组装查询条件con
            con = Q()
            if ConsumableType != 'all':
                con.children.append(('ConsumableType__name', ConsumableType))
            if ToolType != 'all':
                con.children.append(('tooltype__name', ToolType))
            if Version != 'all':
                con.children.append(('version__name', Version))
            if Model != 'all':
                con.children.append(('model__name', Model))
            if Status != 'all':
                con.children.append(('status', Status))
            consumable_objs = models.Consumable.objects.filter(con).order_by('-updatetime')
            TD_objs = models.TypeDefinition.objects
            CT_objs = models.ConsumableType.objects
            for i in consumable_objs:
                li = [
                    '', i.sn, gettext(CT_objs.filter(id=i.ConsumableType_id).first().name), TD_objs.filter(id=i.version_id).first().name,
                    TD_objs.filter(id=i.tooltype_id).first().name, TD_objs.filter(id=i.model_id).first().name,
                    gettext(i.status), i.usefullife, i.ratedlife, i.location, i.position
                ]
                ConsumableList.append(li)
            return JsonResponse(reply.info('', {'ConsumableList': ConsumableList}))
        except Exception as e:
            return JsonResponse(reply.error(e))


class get_all_consumable_list(View):
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            consumable_list = list(models.Consumable.objects.values_list('sn', flat=True))
            return JsonResponse(reply.info('', {'consumable_list': consumable_list}))
        except Exception as e:
            return JsonResponse(reply.error(e))
