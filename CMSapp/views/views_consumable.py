# -*- coding: utf-8 -*-

import json
import logging
import re
from datetime import datetime

import pandas
import pandas as pd
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import activate, gettext
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from CMS import settings
from CMSapp import models
from CMSapp.common import msg as Msg, tools
from CMSapp.common.clsResponse import ResMsg, ViewRes
from CMSapp.common.tools import tool
from CMSapp.common import trans

mylog = logging.getLogger('CMS')
default_lang = settings.DEFAULT_LANG

reply = ResMsg()


class ConsumableQuery(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_name = 'Consumable Query'

    @csrf_exempt
    def get(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        ConsumableType = models.ConsumableType.objects.filter().values_list('name', flat=True)
        ToolType = models.TypeDefinition.objects.filter(typegroup__name__endswith='Type').values_list('name', flat=True)
        VersionType = models.TypeDefinition.objects.filter(typegroup__name__endswith='Version').values_list('name', flat=True)
        StatusType = ['Stock', 'Using', 'Scrapping', 'Scraped', ]
        Model_list = models.TypeDefinition.objects.filter(typegroup__name__endswith='Model').values_list('name', flat=True)
        # head_list = ['', ] + [gettext(i.name) for i in models.Consumable._meta.get_fields()][5: -8]  # 获取Consumable数据表中全部字段(包含了外键关系)
        head_list = ['', ] + [
            gettext('sn'), gettext('ConsumableType'), gettext('entertime'), gettext('version'), gettext('tooltype'), gettext('model'), gettext('status'), gettext('usefullife'),
            gettext('ratedlife'), gettext('location'), gettext('position'), gettext('createtime'), gettext('updateuser'), gettext('updatetime'),
            gettext('comment')
        ]
        size_head_list = [gettext('TestPoint'), gettext('StandardValue'), gettext('ErrorRange'), gettext('MeasuredValue')]
        width_head_list = [gettext('Point'), gettext('Value')]
        angle_head_list = [gettext('Angle'), gettext('Value')]
        spacing_head_list = [
            gettext('Arg'), gettext('StandardValue'), gettext('ErrorRange'), gettext('Arg1'),
            gettext('MeasuredValue1'), gettext('Arg2'), gettext('MeasuredValue2')
        ]
        tension_head_list = [gettext('Point'), gettext('StandardValue'), gettext('ErrorRange'), gettext('MeasuredValue')]
        return render(request, 'ConsumableQuery.html', {
            'title_name': gettext(self.title_name),
            'ConsumableType': ConsumableType,
            'ToolType': ToolType,
            'head_list': head_list,
            'VersionType': VersionType,
            'StatusType': StatusType,
            'Model_list': Model_list,
            'size_head_list': size_head_list,
            'width_head_list': width_head_list,
            'angle_head_list': angle_head_list,
            'spacing_head_list': spacing_head_list,
            'tension_head_list': tension_head_list,
        })

    @csrf_exempt
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            sn = request.POST['sn']
            tooltype = request.POST['tooltype']
            version = request.POST['version']
            status = request.POST['status']
            model = request.POST['model']
            ConsumableType = request.POST['ConsumableType']
            size_list = width_list = angle_list = spacing_list = tension_list = []
            if models.Consumable.objects.filter(sn=sn).first():
                size_list = [[i.TestPoint, i.StandardValue, i.ErrorRange, i.MeasuredValue] for i in models.DimensionalRecord.objects.filter(sn=sn)]
                width_list = [[i.Point, i.Value] for i in models.BladeWidth.objects.filter(sn=sn)]
                angle_list = [[i.Angle, i.Value] for i in models.BladeAngle.objects.filter(sn=sn)]
                spacing_list = [[i.Arg, i.StandardValue, i.ErrorRange, i.Arg1, i.MeasuredValue1, i.Arg2, i.MeasuredValue2]
                                for i in models.Spacing.objects.filter(sn=sn)]
                tension_list = [[i.Point, i.StandardValue, i.ErrorRange, i.MeasuredValue] for i in models.Tension.objects.filter(sn=sn)]
            # 组装查询条件con
            con = Q()
            # con.children.append(('sn__contains', sn))  # name__contains 模糊查询
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
            mould_objs = models.Consumable.objects.filter(con).order_by('-updatetime')
            mould_list = []
            typedefintion_objs = models.TypeDefinition.objects

            if mould_objs:
                for i in mould_objs:
                    li = [
                        i.sn, gettext(models.ConsumableType.objects.filter(id=i.ConsumableType_id).first().name), i.entertime,
                        typedefintion_objs.filter(id=i.version_id).first().name, typedefintion_objs.filter(id=i.tooltype_id).first().name,
                        typedefintion_objs.filter(id=i.model_id).first().name, gettext(i.status), i.usefullife, i.ratedlife, i.location,
                        i.position, i.createtime, i.updateuser, i.updatetime, i.comment
                    ]
                    mould_list.append(li)
            msg = Msg.Language(lang).main().Common.C02.format(gettext(self.title_name), user)
            data = {
                'mould_list': mould_list,
                'size_list': size_list,
                'width_list': width_list,
                'angle_list': angle_list,
                'spacing_list': spacing_list,
                'tension_list': tension_list,
            }
            return JsonResponse(reply.info(msg, data), safe=False)
        except Exception as e:
            return JsonResponse(reply.error(e), safe=False)


class export_excel(View):
    @csrf_exempt
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            sn_list = json.loads(request.POST['sn_list'])
            cosumable_obj = models.Consumable.objects.filter(sn__in=sn_list)
            # 卡控只能导出一种耗材类型的数据
            if len(cosumable_obj.values_list('ConsumableType__name', flat=True).distinct()) != 1:
                msg = Msg.Language(lang).main().Excel.E07.format(user)
                return JsonResponse(reply.warn(msg))
            excel_list = []
            con_objs = cosumable_obj.values('sn', 'ConsumableType__name', 'entertime', 'version__name', 'tooltype__name', 'model__name', 'status',
                                            'usefullife', 'ratedlife', 'location', 'position', 'createtime', 'updateuser', 'updatetime', 'comment')
            # 遍历所有耗材，依次放进列表中构造数组
            # 网板导出
            if models.ConsumableType.objects.filter(id=cosumable_obj.first().ConsumableType_id).first().name == 'Screen':
                header = [gettext('sn'), gettext('ConsumableType'), gettext('entertime'), gettext('version'), gettext('tooltype'), gettext('model'),
                          gettext('status'), gettext('usefullife'), gettext('ratedlife'), gettext('location'), gettext('position'), gettext('createtime'),
                          gettext('updateuser'), gettext('updatetime'), gettext('comment'), gettext('XStandardValue'), gettext('XMeasuredValue1'),
                          gettext('XMeasuredValue2'), gettext('YStandardValue'), gettext('YMeasuredValue1'), gettext('YMeasuredValue2'),
                          gettext('ZStandardValue'), gettext('ZMeasuredValue1'), gettext('ZMeasuredValue2'), gettext('TMeasuredValue1'),
                          gettext('TMeasuredValue2'), gettext('TMeasuredValue3'), gettext('TMeasuredValue4'), gettext('TMeasuredValue5'),
                          gettext('TMeasuredValue6'), gettext('TMeasuredValue7'), gettext('TMeasuredValue8'), gettext('TMeasuredValue9'), ]
                for con in con_objs:
                    c_list = []
                    for fields in ['sn', 'ConsumableType__name', 'entertime', 'version__name', 'tooltype__name', 'model__name', 'status',
                                   'usefullife', 'ratedlife', 'location', 'position', 'createtime', 'updateuser', 'updatetime', 'comment']:
                        # 翻译耗材类型和耗材状态
                        if fields in ['ConsumableType__name', 'status']:
                            c_list.append(gettext(con[fields]))
                        else:
                            c_list.append(con[fields])
                    s_objs = models.Spacing.objects.filter(sn_id=con['sn']).values('StandardValue', 'MeasuredValue1', 'MeasuredValue2')
                    for s in s_objs:
                        for fields in ['StandardValue', 'MeasuredValue1', 'MeasuredValue2']:
                            c_list.append(s[fields])
                    t_objs = models.Tension.objects.filter(sn_id=con['sn']).values_list('MeasuredValue', flat=True)
                    for t in t_objs:
                        c_list.append(t)
                    excel_list.append(c_list)
            # 刀模导出
            else:
                for con in con_objs:
                    c_list = []
                    for fields in ['sn', 'ConsumableType__name', 'entertime', 'version__name', 'tooltype__name', 'model__name', 'status',
                                   'usefullife', 'ratedlife', 'location', 'position', 'createtime', 'updateuser', 'updatetime', 'comment']:
                        # 翻译耗材类型和耗材状态
                        if fields in ['ConsumableType__name', 'status']:
                            c_list.append(gettext(con[fields]))
                        else:
                            c_list.append(con[fields])
                    DR_objs = models.DimensionalRecord.objects.filter(sn_id=con['sn']).values_list('MeasuredValue', flat=True)
                    for DR in DR_objs:
                        c_list.append(DR)
                    BW_objs = models.BladeWidth.objects.filter(sn_id=con['sn']).values_list('Value', flat=True)
                    for BW in BW_objs:
                        c_list.append(BW)
                    BA_objs = models.BladeAngle.objects.filter(sn_id=con['sn']).values_list('Value', flat=True)
                    for BA in BA_objs:
                        c_list.append(BA)
                    excel_list.append(c_list)
                header = [gettext('sn'), gettext('ConsumableType'), gettext('entertime'), gettext('version'), gettext('tooltype'), gettext('model'),
                          gettext('status'), gettext('usefullife'), gettext('ratedlife'), gettext('location'), gettext('position'), gettext('createtime'),
                          gettext('updateuser'), gettext('updatetime'), gettext('comment')]
                # 获取excel_list中的最大行长度
                max_row_length = max(len(row) for row in excel_list)
                # 根据最大行长度生成缺失的列名
                missing_columns = ['Columns{}'.format(i) for i in range(len(header), max_row_length)]
                # 将缺失的列名添加到header列表
                header += missing_columns
            # 创建一个DataFrame对象,传递给DataFrame的数据必须是一个二维结构(如列表、NumPy数组等),其中每个子列表或子数组表示一行数据
            df = pd.DataFrame(excel_list, columns=header)
            # 将DataFrame写入Excel文件
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="consumable.xlsx"'
            df.to_excel(response, index=False)
            return response
        except Exception as e:
            return JsonResponse(reply.error(e))


class ScreenUsageInfo(View):
    @csrf_exempt
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            sn = request.POST['sn']
            # 获取input_list [model, version, tooltype, ratedlife, remaininglife, status]
            Consumable_objs = models.Consumable.objects.filter(sn=sn).first()
            if not Consumable_objs:
                msg = Msg.Language(lang).main().Common.C01.format('Consumable', sn, user)
                return JsonResponse(reply.warn(msg), safe=False)
            ConsumableType = models.ConsumableType.objects.filter(id=Consumable_objs.ConsumableType_id).first().name
            model = models.TypeDefinition.objects.filter(id=Consumable_objs.model_id).first().name
            version = models.TypeDefinition.objects.filter(id=Consumable_objs.version_id).first().name
            tooltype = models.TypeDefinition.objects.filter(id=Consumable_objs.tooltype_id).first().name
            ratedlife = Consumable_objs.ratedlife
            usefullife = Consumable_objs.usefullife
            remaininglife = int(ratedlife) - int(usefullife) if int(ratedlife) - int(usefullife) >= 0 else 0
            status = Consumable_objs.status
            input_list = [gettext(ConsumableType), model, version, tooltype, gettext(status), ratedlife, remaininglife, usefullife]
            usehistory_list = []
            # 获取使用历史记录
            UseHistory_objs = models.ScreenUseHistory.objects.filter(sn=sn).order_by('-updatetime')
            if UseHistory_objs:
                for i in UseHistory_objs:
                    i.EmulsionShedding = 'OK' if i.EmulsionShedding else 'NG'
                    i.MeshPlugging = 'OK' if i.MeshPlugging else 'NG'
                    if i.Clean is not None:
                        i.Clean = 'Y' if i.Clean else 'N'
                    usehistory_list.append([
                        i.CheckTime, i.X1, i.X2, i.Y1, i.Y2, i.Z1, i.Z2, i.P1, i.P2, i.P3, i.P4, i.P5, i.P6, i.P7, i.P8, i.P9,
                        i.EmulsionShedding, i.MeshPlugging, i.CheckOperator, i.PrintingNumber, i.Print_Operator,
                        i.AddUpPrint, i.Add_Operator, i.Clean, i.Clean_Operator
                    ])
            data = {'usehistory_list': usehistory_list, 'input_list': input_list}
            return JsonResponse(reply.info('', data), safe=False)
        except Exception as e:
            return JsonResponse(reply.error(e), safe=False)


class ScreenCheck(View):
    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        sid = transaction.savepoint()
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            CheckTime = request.POST['CheckTime']
            sn = request.POST['sn']
            Consumable_objs = models.Consumable.objects.filter(sn=sn)
            li = json.loads(request.POST['list'])
            # 定义正则匹配规则，用于判断数据是否为字符串数字
            pattern = r'^\d+(\.\d+)?$'
            # return re.match(pattern, s) is not None
            for item in li[0: 15]:
                # 判断是否为数字
                if re.match(pattern, item) is None:
                    msg = Msg.Language(lang).main().Verify.V01.format(item, user)
                    return JsonResponse(reply.warn(msg))
            cur_time = datetime.now()
            if int(str(cur_time).replace('-', '')[0:8]) < int(str(CheckTime).replace('-', '')[0:8]):
                msg = Msg.Language(lang).main().Common.C04.format(user)
                return JsonResponse(reply.warn(msg), safe=False)
            # 卡控点检时候数据的输入,数据为0不进行卡控
            if float(li[0]) != 0:
                StandardValue_li = models.Spacing.objects.filter(sn_id=sn).values_list('StandardValue', flat=True)
                ErrorRange_li = models.Spacing.objects.filter(sn_id=sn).values_list('ErrorRange', flat=True)
                j = 0
                for i in range(6):
                    if i in [2, 4]:
                        j += 1
                    if not float(StandardValue_li[j]) - float(ErrorRange_li[j]) <= float(li[i]) <= float(StandardValue_li[j]) + float(ErrorRange_li[j]):
                        msg = Msg.Language(lang).main().Excel.E06.format(li[i], user)
                        return JsonResponse(reply.warn(msg))
                P_li = [li[6], li[7], li[8], li[9], li[10], li[11], li[12], li[13], li[14]]
                if not all(22 <= float(i) <= 26 for i in P_li):
                    first_out_of_range = next((i for i in P_li if not 22 <= float(i) <= 26), None)
                    msg = Msg.Language(lang).main().Excel.E06.format(first_out_of_range, user)
                    return JsonResponse(reply.warn(msg))
            li[15] = True if li[15] == 'true' else False
            li[16] = True if li[16] == 'true' else False
            Screen_dic = {
                'sn': sn,
                'CheckTime': CheckTime,
                'X1': li[0],
                'X2': li[1],
                'Y1': li[2],
                'Y2': li[3],
                'Z1': li[4],
                'Z2': li[5],
                'P1': li[6],
                'P2': li[7],
                'P3': li[8],
                'P4': li[9],
                'P5': li[10],
                'P6': li[11],
                'P7': li[12],
                'P8': li[13],
                'P9': li[14],
                'EmulsionShedding': li[15],
                'MeshPlugging': li[16],
                'CheckOperator': li[17],
                'PrintingNumber': None,
                'Print_Operator': '',
                'AddUpPrint': None,
                'Add_Operator': '',
                'Clean': None,
                'Clean_Operator': '',
                'updatetime': datetime.now(),
                'updateuser': user,
            }
            models.ScreenUseHistory.objects.create(**Screen_dic)
            scrap_msg = ''
            # 当点检后网板不合格自动进行报废
            if not li[15] and li[16]:
                models.Consumable.objects.filter(sn=sn).update(
                    EmulsionShedding=li[15],
                    MeshPlugging=li[16],
                    inscrapping=True,
                    status='Scrapping',
                )
                dic = {
                    'sn': sn,
                    'ConsumableType': 'Screen',
                    'model': Consumable_objs.first().model,
                    'version': Consumable_objs.first().version,
                    'tooltype': Consumable_objs.first().tooltype,
                    'status': 'Scrapping',
                    'inscrapping': True,
                    'usefullife': Consumable_objs.first().usefullife,
                    'ratedlife': Consumable_objs.first().ratedlife,
                    'location': Consumable_objs.first().location,
                    'entertime': Consumable_objs.first().entertime,
                    'updateuser': user,
                    'updatetime': datetime.now(),
                    'comment': '',
                }
                # 表C_Scrap中记录报废sn
                models.C_Scrap.objects.create(**dic)
                scrap_msg = Msg.Language(lang).main().Consumable.M01.format(sn, user)
            transaction.savepoint_commit(sid)
            msg = Msg.Language(lang).main().Common.C02.format(gettext('Spot Check'), user) if not scrap_msg else scrap_msg
            return JsonResponse(reply.info(msg))
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return JsonResponse(reply.error(e))


class ScreenUsage(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_name = 'Screen Usage'

    @csrf_exempt
    def get(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        # 获取表中所有字段
        # head_list = [gettext(i.name) for i in models.ScreenUseHistory._meta.get_fields()]
        head_list = ['', ] + [
            gettext('CheckTime'), 'X1', 'X2', 'Y1', 'Y2', 'Z1', 'Z2', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9',
            gettext('No MeshPlugging'), gettext('No EmulsionShedding'), gettext('CheckOperator'), gettext('PrintingNumber'),
            gettext('Print_Operator'), gettext('AddUpPrint'), gettext('Add_Operator'), gettext('Clean'), gettext('Clean_Operator'),
        ]
        consumable_list = models.Consumable.objects.values_list('sn', flat=True)
        modal_headList = [
            'X1', 'X2', 'Y1', 'Y2', 'Z1', 'Z2', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9',
            gettext('No MeshPlugging'), gettext('No EmulsionShedding'), gettext('CheckOperator'),
        ]
        return render(request, 'ScreenUsage.html', {
            'title_name': gettext(self.title_name),
            'head_list': head_list,
            'consumable_list': consumable_list,
            'modal_headList': modal_headList,
        })

    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        sid = transaction.savepoint()
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            data_list = json.loads(request.POST['data_list'])
            screen_list = json.loads(request.POST['screen_list'])
            # timezone = pytz.timezone('Asia/Shanghai')  # 指定时区为上海
            # 将字符串解析为 datetime 对象(去掉毫秒部分)
            CheckTime = datetime.strptime(screen_list[0][0][:-4], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            updateuser = request.user.username
            verify = tools.Verify(updateuser, lang)
            updatetime = datetime.now()
            cur_time = datetime.now().date()
            cur_time = str(cur_time).replace('-', '')
            sn = data_list[0]
            usetime = data_list[1]
            use_time = str(usetime).replace('-', '')
            PrintingNumber = data_list[2]
            Print_Operator = data_list[3]
            Add_Operator = data_list[4]
            Clean = data_list[5]
            Clean_Operator = data_list[6]
            Consumable_objs = models.Consumable.objects.filter(sn=sn).first()
            if not Consumable_objs:
                msg = Msg.Language(lang).main().Common.C01.format('Consumable', sn, updateuser)
                return JsonResponse(reply.warn(msg))
            usefullife = Consumable_objs.usefullife
            ratedlife = Consumable_objs.ratedlife
            remaininglife = int(ratedlife) - int(usefullife)
            status = Consumable_objs.status
            # 刀模状态不能为库存
            if status == 'Stock':
                msg = Msg.Language(lang).main().Consumable.M04.format(sn, updateuser)
                return JsonResponse(reply.warn(msg))
            # 从数据库抓取数据判断当前刀模状态是否为报废状态
            if status in ['Scrapping', 'Scraped']:
                msg = Msg.Language(lang).main().Consumable.M01.format(sn, updateuser)
                return JsonResponse(reply.warn(msg))
            # 判断PrintingNumber是否为数字
            if verify.is_digits(PrintingNumber):
                return JsonResponse(reply.warn(verify.info), safe=False)
            remaininglife = int(remaininglife) - int(PrintingNumber)
            AddUpPrint = int(ratedlife) - int(remaininglife)
            scrap_msg = ''
            # 使用时间和当前时间进行比较，若超过当前时间则报错
            if int(use_time) > int(cur_time):
                msg = Msg.Language(lang).main().Common.C03.format(updateuser)
                return JsonResponse(reply.warn(msg), safe=False)
            if remaininglife <= 0:
                # 当剩余寿命为0时，对此刀模进行自动报废操作
                status = 'Scrapping'
                models.Consumable.objects.filter(sn=sn).update(status=status, inscrapping=True)
                AddUpPrint = int(Consumable_objs.usefullife) + int(PrintingNumber)
                remaininglife = 0
                dic = {
                    'sn': sn,
                    'ConsumableType': 'Screen',
                    'model': Consumable_objs.model,
                    'version': Consumable_objs.version,
                    'tooltype': Consumable_objs.tooltype,
                    'status': status,
                    'inscrapping': True,
                    'usefullife': AddUpPrint,
                    'ratedlife': Consumable_objs.ratedlife,
                    'location': Consumable_objs.location,
                    'entertime': Consumable_objs.entertime,
                    'updateuser': updateuser,
                    'updatetime': datetime.now(),
                    'comment': '',
                }
                # 表C_Scrap中记录报废sn
                models.C_Scrap.objects.create(**dic)
                scrap_msg = Msg.Language(lang).main().Consumable.M01.format(sn, updateuser)
            usehistory_list = []
            # 补全网板使用历史记录
            Clean = True if Clean == 'Y' else False
            SUH_obj = models.ScreenUseHistory.objects.filter(
                sn=sn, CheckTime__startswith=CheckTime, CheckOperator=screen_list[0][-7], Clean_Operator=screen_list[0][-1],
            ).order_by('-updatetime').first()
            if SUH_obj:
                SUH_obj.PrintingNumber = PrintingNumber
                SUH_obj.Print_Operator = Print_Operator
                SUH_obj.AddUpPrint = AddUpPrint
                SUH_obj.Add_Operator = Add_Operator
                SUH_obj.Clean = Clean
                SUH_obj.Clean_Operator = Clean_Operator
                SUH_obj.updateuser = updateuser
                SUH_obj.updatetime = updatetime
                SUH_obj.save()
            # 更新网板使用寿命, Consumable表中usefullife字段
            models.Consumable.objects.filter(sn=sn).update(usefullife=AddUpPrint)
            # 遍历此网板所有使用历史记录显示在前端
            UseHistory_objs = models.ScreenUseHistory.objects.filter(sn=sn).order_by('-updatetime')
            # 事务提交
            transaction.savepoint_commit(sid)
            for i in UseHistory_objs:
                i.EmulsionShedding = 'OK' if i.EmulsionShedding else 'NG'
                i.MeshPlugging = 'OK' if i.MeshPlugging else 'NG'
                if i.Clean is not None:
                    i.Clean = 'Y' if i.Clean else 'N'
                usehistory_list.append([
                    i.CheckTime, i.X1, i.X2, i.Y1, i.Y2, i.Z1, i.Z2, i.P1, i.P2, i.P3, i.P4, i.P5, i.P6, i.P7, i.P8, i.P9,
                    i.EmulsionShedding, i.MeshPlugging, i.CheckOperator, i.PrintingNumber, i.Print_Operator,
                    i.AddUpPrint, i.Add_Operator, i.Clean, i.Clean_Operator
                ])
            data = {'usehistory_list': usehistory_list, 'remaininglife': int(remaininglife), 'AddUpPrint': int(AddUpPrint), 'status': status}
            msg = Msg.Language(lang).main().Common.C02.format(gettext(self.title_name), updateuser) if not scrap_msg else scrap_msg
            return JsonResponse(reply.info(msg, data), safe=False)
        except Exception as e:
            # 事务回滚
            transaction.savepoint_rollback(sid)
            return JsonResponse(reply.error(e), safe=False)


class StockOperation(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_name = 'Stock Operation'

    @csrf_exempt
    def get(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        # 获取表中所有字段
        head_list = [gettext(i.name) for i in models.ReceiveReturnHistory._meta.get_fields()]
        ConsumableType = models.ConsumableType.objects.values_list('name', flat=True)
        consumable_list = ['', ] + [
            gettext('sn'), gettext('ConsumableType'), gettext('version'), gettext('tooltype'), gettext('model'),
            gettext('status'), gettext('usefullife'), gettext('ratedlife'), gettext('location'), gettext('position')
        ]
        ToolType = models.TypeDefinition.objects.filter(typegroup__name__endswith='Type').values_list('name', flat=True)
        VersionType = models.TypeDefinition.objects.filter(typegroup__name__endswith='Version').values_list('name', flat=True)
        StatusType = ['Stock', 'Using', 'Scrapping', 'Scraped', ]
        Model_list = models.TypeDefinition.objects.filter(typegroup__name__endswith='Model').values_list('name', flat=True)
        return render(request, 'StockOperation.html', {
            'title_name': gettext(self.title_name),
            'head_list': head_list,
            'ConsumableType': ConsumableType,
            'consumable_list': consumable_list,
            'ToolType': ToolType,
            'VersionType': VersionType,
            'StatusType': StatusType,
            'Model_list': Model_list,
        })

    @csrf_exempt
    @transaction.atomic  # 事务提交和事务回滚
    def post(self, request):
        sid = transaction.savepoint()
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            data = request.POST
            sn = data['sn']
            location = data['location']
            manager = data['manager']
            operator = data['operator']
            operationtype = data['operationtype']
            operationtime = data['operationtime']
            comment = data['comment']
            data_list = []
            # 验证此刀模是否存在
            Consumable_objs = models.Consumable.objects.filter(sn=sn)
            if not Consumable_objs:
                msg = Msg.Language(lang).main().Common.C01.format('Consumable', sn, user)
                return JsonResponse(reply.warn(msg))
            if operationtype == 'receive':
                # 如果存储位置和刀模不符合，则不能进行领取
                if Consumable_objs.first().location != location:
                    msg = Msg.Language(lang).main().Consumable.M05.format(sn, location, user)
                    return JsonResponse(reply.warn(msg))
                # 状态不为库存，不能获取
                if Consumable_objs.filter(status='Stock', inscrapping=False).first():
                    Consumable_objs.update(status='Using', location='', updatetime=datetime.now())
                else:
                    msg = Msg.Language(lang).main().Consumable.M02.format(sn, user)
                    return JsonResponse(reply.warn(msg))
            else:
                # 状态不为使用中或报废中，不能归还
                if Consumable_objs.filter(Q(status='Using') | Q(status='Scrapping')).first():
                    Consumable_objs.update(status='Stock', location=location, updatetime=datetime.now())
                else:
                    msg = Msg.Language(lang).main().Consumable.M03.format(sn, user)
                    return JsonResponse(reply.warn(msg))
            models.ReceiveReturnHistory.objects.create(
                sn=sn,
                location=location,
                manager=manager,
                operator=operator,
                operationtype=operationtype,
                operationtime=operationtime,
                updateuser=user,
                updatetime=datetime.now(),
                comment=comment,
            )
            stock_objs = models.ReceiveReturnHistory.objects.filter(sn=sn).order_by('-updatetime')
            # 事务提交
            transaction.savepoint_commit(sid)
            for i in stock_objs:
                data_list.append([i.sn, i.location, i.manager, i.operator, gettext(i.operationtype), i.operationtime, i.updateuser, i.updatetime, i.comment, ])
            msg = Msg.Language(lang).main().Common.C02.format(gettext(operationtype), user)
            data = {'data_list': data_list}
            return JsonResponse(reply.info(msg, data), safe=False)
        except Exception as e:
            # 事务回滚
            transaction.savepoint_rollback(sid)
            return JsonResponse(reply.error(e))


class StockInfo(View):
    @csrf_exempt
    def post(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        user = request.user.username
        sn = request.POST['sn']
        data_list = []
        stock_objs = models.ReceiveReturnHistory.objects.filter(sn=sn).order_by('-updatetime')
        if not stock_objs:
            msg = Msg.Language(lang).main().Common.C01.format('ReceiveReturnHistory', sn, user)
            return JsonResponse(reply.warn(msg), safe=False)
        for i in stock_objs:
            data_list.append([
                i.sn, i.location, i.manager, i.operator, gettext(i.operationtype), i.operationtime, i.updateuser, i.updatetime, i.comment,
            ])
        msg = Msg.Language(lang).main().Common.C02.format(gettext('Query'), user)
        data = {'data_list': data_list}
        return JsonResponse(reply.info(msg, data), safe=False)


class ForcedScrap(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_name = 'Forced Scrap'

    @csrf_exempt
    def get(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        head_list = [gettext(i.name) for i in models.C_Scrap._meta.get_fields()]
        ConsumableType = models.ConsumableType.objects.values_list('name', flat=True)
        mould_list = models.Consumable.objects.filter(status='Stock').values_list('sn', flat=True)
        return render(request, 'ForcedScrap.html', {
            'title_name': gettext(self.title_name),
            'head_list': head_list,
            'mould_list': mould_list,
            'ConsumableType': ConsumableType,
        })

    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        sid = transaction.savepoint()
        try:
            ViewRes().RequestInfo(request)
            user = request.user.username
            lang = tool.get_session_lang(request)
            activate(lang)
            sn = request.POST['sn']
            comment = request.POST['comment']
            Consumable_objs = models.Consumable.objects.filter(sn=sn)
            if not Consumable_objs:
                msg = Msg.Language(lang).main().Common.C01.format('Consumable', sn, user)
                return JsonResponse(reply.warn(msg))
            if Consumable_objs.first().status != 'Stock':
                msg = Msg.Language(lang).main().Consumable.M06.format(sn, user)
                return JsonResponse(reply.warn(msg))
            status = 'Scrapping'
            Consumable_objs.update(
                status=status,
                updateuser=user,
                comment=comment,
                updatetime=datetime.now(),
                inscrapping=True,
            )
            dic = {
                'sn': sn,
                'ConsumableType': models.ConsumableType.objects.filter(id=Consumable_objs.first().ConsumableType_id).first().name,
                'model': Consumable_objs.first().model,
                'version': Consumable_objs.first().version,
                'tooltype': Consumable_objs.first().tooltype,
                'status': status,
                'inscrapping': True,
                'usefullife': Consumable_objs.first().usefullife,
                'ratedlife': Consumable_objs.first().ratedlife,
                'location': Consumable_objs.first().location,
                'entertime': Consumable_objs.first().entertime,
                'updateuser': user,
                'updatetime': datetime.now(),
                'comment': '',
            }
            dic.setdefault('comment', comment)
            # 表C_Scrap中记录报废sn
            models.C_Scrap.objects.create(**dic)
            transaction.savepoint_commit(sid)
            msg = Msg.Language(lang).main().Common.C02.format(gettext(self.title_name), user)
            data_list = []
            C_Scrap_objs = models.C_Scrap.objects.filter(sn=sn)
            if C_Scrap_objs:
                for i in C_Scrap_objs:
                    data_list.append([
                        i.sn, i.ConsumableType, i.model, i.version, i.tooltype, gettext(i.status), gettext(str(i.inscrapping)),
                        i.usefullife, i.ratedlife, i.location, i.entertime, i.updateuser, i.updatetime, i.comment
                    ])
            return JsonResponse(reply.info(msg, {'data_list': data_list}))
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return JsonResponse(reply.error(e))


class ScrapInfo(View):
    @csrf_exempt
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            sn = request.POST['sn']
            Consumable_objs = models.Consumable.objects.filter(sn=sn)
            readonly_list = []
            t_objs = models.TypeDefinition.objects
            if Consumable_objs:
                for i in Consumable_objs:
                    readonly_list.append([
                        t_objs.filter(id=i.model_id).first().name, t_objs.filter(id=i.version_id).first().name,
                        t_objs.filter(id=i.tooltype_id).first().name, gettext(i.status), gettext(str(i.inscrapping)), i.ratedlife, i.usefullife,
                    ])
            return JsonResponse(reply.info('', {'readonly_list': readonly_list}))
        except Exception as e:
            return JsonResponse(reply.error(e))


class ConfirmScrap(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_name = 'Confirm Scrap'

    @csrf_exempt
    def get(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        head_list = [gettext(i.name) for i in models.C_Scrap._meta.get_fields()]
        ConsumableType = models.ConsumableType.objects.values_list('name', flat=True)
        return render(request, 'ConfirmScrap.html', {
            # 'mould_list': mould_list,
            'head_list': head_list,
            'ConsumableType': ConsumableType,
            'title_name': gettext(self.title_name),
        })

    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        sid = transaction.savepoint()
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            data = request.POST
            scrap_list = json.loads(data['scrap_list'])
            ConsumableType = data['ConsumableType']
            sn_list = []
            for i in scrap_list:
                sn_list.append(i[0])
            models.Consumable.objects.filter(sn__in=sn_list).update(status='Scraped', updateuser=user, updatetime=datetime.now())
            models.C_Scrap.objects.filter(sn__in=sn_list).update(status='Scraped', updateuser=user, updatetime=datetime.now())
            transaction.savepoint_commit(sid)
            C_Scrap_objs = models.C_Scrap.objects.filter(ConsumableType='ConsumableType', status='Scrapping').order_by('-updatetime')
            mould_list = []
            if C_Scrap_objs:
                for i in C_Scrap_objs:
                    mould_list.append([
                        i.sn, i.ConsumableType, i.model, i.version, i.tooltype, i.status, i.inscrapping, i.usefullife,
                        i.ratedlife, i.location, i.entertime, i.updateuser, i.updatetime, i.comment
                    ])
            msg = Msg.Language(lang).main().Common.C02.format(gettext(self.title_name), user)
            return JsonResponse(reply.info(msg, {'mould_list': mould_list}))
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return JsonResponse(reply.error(e))


class get_C_Scrap_list(View):
    @csrf_exempt
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            ConsumableType = request.POST['ConsumableType']
            C_Scrap_objs = models.C_Scrap.objects.filter(ConsumableType=ConsumableType, status='Scrapping').order_by('-updatetime')
            sn_list = []
            for i in C_Scrap_objs:
                sn_list.append([
                    i.sn, i.ConsumableType, i.model, i.version, i.tooltype, i.status, i.inscrapping, i.usefullife,
                    i.ratedlife, i.location, i.entertime, i.updateuser, i.updatetime, i.comment,
                ])
            return JsonResponse(reply.info('', {'sn_list': sn_list}))
        except Exception as e:
            return JsonResponse(reply.error(e))


class MoudlsUsage(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_name = 'Moulds Usage'

    @csrf_exempt
    def get(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        # 获取表中所有字段
        head_list = [gettext(i.name) for i in models.MouldsUseHistory._meta.get_fields()]
        consumable_list = models.Consumable.objects.values_list('sn', flat=True)
        return render(request, 'MouldsUsage.html', {
            'title_name': gettext(self.title_name),
            'head_list': head_list,
            'consumable_list': consumable_list,
        })

    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        sid = transaction.savepoint()
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            data_list = json.loads(request.POST['data_list'])
            updateuser = request.user.username
            verify = tools.Verify(updateuser, lang)
            updatetime = datetime.now()
            cur_time = datetime.now().date()
            cur_time = str(cur_time).replace('-', '')
            sn = data_list[0]
            usetime = data_list[1]
            use_time = str(usetime).replace('-', '')
            usenumber = data_list[2]
            position = data_list[3]
            comment = data_list[4]
            operator = data_list[8]
            model = data_list[9]
            version = data_list[10]
            tooltype = data_list[11]
            Consumable_objs = models.Consumable.objects.filter(sn=sn).first()
            if not Consumable_objs:
                msg = Msg.Language(lang).main().Common.C01.format('Consumable', sn, updateuser)
                return JsonResponse(reply.warn(msg))
            usefullife = Consumable_objs.usefullife
            ratedlife = data_list[6]
            remaininglife = int(ratedlife) - int(usefullife)
            status = Consumable_objs.status
            # 刀模状态不能为库存
            if status == 'Stock':
                msg = Msg.Language(lang).main().Consumable.M04.format(sn, updateuser)
                return JsonResponse(reply.warn(msg))
            # 从数据库抓取数据判断当前刀模状态是否为报废状态
            if status in ['Scrapping', 'Scraped']:
                msg = Msg.Language(lang).main().Consumable.M01.format(sn, updateuser)
                return JsonResponse(reply.warn(msg))
            # 判断usenumber是否为数字
            if verify.is_digits(usenumber):
                return JsonResponse(reply.warn(verify.info), safe=False)
            remaininglife = int(remaininglife) - int(usenumber)
            usefullife = int(ratedlife) - int(remaininglife)
            scrap_msg = ''
            # 使用时间和当前时间进行比较，若超过当前时间则报错
            if int(use_time) > int(cur_time):
                msg = Msg.Language(lang).main().Common.C03.format(updateuser)
                return JsonResponse(reply.warn(msg), safe=False)
            if remaininglife <= 0:
                # 当剩余寿命为0时，对此刀模进行自动报废操作
                status = 'Scrapping'
                models.Consumable.objects.filter(sn=sn).update(status=status, inscrapping=True)
                usefullife = int(Consumable_objs.usefullife) + int(usenumber)
                remaininglife = 0
                dic = {
                    'sn': sn,
                    'ConsumableType': 'Moulds',
                    'model': Consumable_objs.model,
                    'version': Consumable_objs.version,
                    'tooltype': Consumable_objs.tooltype,
                    'status': status,
                    'inscrapping': True,
                    'usefullife': usefullife,
                    'ratedlife': Consumable_objs.ratedlife,
                    'location': Consumable_objs.location,
                    'entertime': Consumable_objs.entertime,
                    'updateuser': updateuser,
                    'updatetime': datetime.now(),
                    'comment': '',
                }
                # 表C_Scrap中记录报废sn
                models.C_Scrap.objects.create(**dic)
                scrap_msg = Msg.Language(lang).main().Consumable.M01.format(sn, updateuser)
            mouldsusehistory_list = []
            # 对刀模使用新建历史记录
            models.MouldsUseHistory.objects.create(
                sn=sn,
                model=model,
                version=version,
                tooltype=tooltype,
                status=status,
                usetime=usetime,
                usenumber=usenumber,
                position=position,
                updatetime=updatetime,
                updateuser=operator,
                comment=comment,
            )
            # 更新刀模使用寿命, Consumable表中usefullife字段
            models.Consumable.objects.filter(sn=sn).update(usefullife=usefullife)
            # 遍历此刀模所有使用历史记录显示在前端
            MouldsUseHistory_objs = models.MouldsUseHistory.objects.filter(sn=sn).order_by('-updatetime')
            # 事务提交
            transaction.savepoint_commit(sid)
            for i in MouldsUseHistory_objs:
                mouldsusehistory_list.append([i.sn, i.model, i.version, i.tooltype, i.status, i.usetime, i.usenumber, i.position, i.updatetime, i.updateuser, i.comment])
            data = {'mouldsusehistory_list': mouldsusehistory_list, 'remaininglife': int(remaininglife), 'status': status}
            msg = Msg.Language(lang).main().Common.C02.format(gettext(self.title_name), updateuser) if not scrap_msg else scrap_msg
            return JsonResponse(reply.info(msg, data), safe=False)
        except Exception as e:
            # 事务回滚
            transaction.savepoint_rollback(sid)
            return JsonResponse(reply.error(e), safe=False)


class MouldsUsageInfo(View):
    @csrf_exempt
    def post(self, request):
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            sn = request.POST['sn']
            # 获取input_list [model, version, tooltype, ratedlife, remaininglife, status]
            Consumable_objs = models.Consumable.objects.filter(sn=sn).first()
            if not Consumable_objs:
                msg = Msg.Language(lang).main().Common.C01.format('Consumable', sn, user)
                return JsonResponse(reply.warn(msg), safe=False)
            ConsumableType = models.ConsumableType.objects.filter(id=Consumable_objs.ConsumableType_id).first().name
            model = models.TypeDefinition.objects.filter(id=Consumable_objs.model_id).first().name
            version = models.TypeDefinition.objects.filter(id=Consumable_objs.version_id).first().name
            tooltype = models.TypeDefinition.objects.filter(id=Consumable_objs.tooltype_id).first().name
            ratedlife = Consumable_objs.ratedlife
            usefullife = Consumable_objs.usefullife
            remaininglife = int(ratedlife) - int(usefullife)
            status = Consumable_objs.status
            user_objs = User.objects.filter(username=user).first()
            operator = user_objs.first_name if user_objs.first_name else user
            input_list = [gettext(ConsumableType), model, version, tooltype, ratedlife, remaininglife, gettext(status), operator]
            usehistory_list = []
            # 获取使用历史记录
            UseHistory_objs = models.MouldsUseHistory.objects.filter(sn=sn).order_by('-updatetime')
            for i in UseHistory_objs:
                usehistory_list.append([i.sn, i.model, i.status, i.version, i.tooltype, i.usetime, i.usenumber, i.position, i.updatetime, i.updateuser, i.comment])
            data = {'usehistory_list': usehistory_list, 'input_list': input_list}
            return JsonResponse(reply.info('', data), safe=False)
        except Exception as e:
            return JsonResponse(reply.error(e), safe=False)


class create_consumable_by_excel(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_name = 'Create Consumable'

    @csrf_exempt
    def get(self, request):
        ViewRes().RequestInfo(request)
        lang = tool.get_session_lang(request)
        activate(lang)
        return render(request, 'CreateConsumable.html', {
            'title_name': gettext(self.title_name),
        })

    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        sid = transaction.savepoint()
        try:
            ViewRes().RequestInfo(request)
            lang = tool.get_session_lang(request)
            activate(lang)
            user = request.user.username
            # Excel表格式
            # screen_head_list = ['耗材編號', '耗材類型', '進廠時間', '版本類型', '類別', '機種', '狀態', '使用壽命', '額定壽命', '存儲位置', '使用位置',
            #                   '創建時間', '操作用戶', '操作時間', '備註', 'X標準值', 'X實測值1', 'X實測值2', 'Y標準值', 'Y標準值1', 'Y標準值2',
            #                   'Z標準值', 'Z標準值1', 'Z標準值2', '張力實測值1', '張力實測值2', '張力實測值3', '張力實測值4', '張力實測值5',
            #                   '張力實測值6', '張力實測值7', '張力實測值8', '張力實測值9']
            file = request.FILES.get('file')
            # 读取Excel文件为DataFrame对象
            df = pandas.read_excel(file)
            # 获取表头
            # headers = list(df.columns)
            # 获取Consumable表中所有sn
            sn_list = list(models.Consumable.objects.values_list('sn', flat=True))
            # 获取TypeDefinition表中所有name
            td_list = list(models.TypeDefinition.objects.values_list('name', flat=True))
            # 获取ConsumableType表中所有name
            ct_list = list(models.ConsumableType.objects.values_list('name', flat=True))
            # 上传excel文档需满足标准文档格式即可，不限语言
            # 获取除表头以外的所有行的数据
            data = df.values.tolist()[0:]
            TD_objs = models.TypeDefinition.objects.filter()
            CT_objs = models.ConsumableType.objects.filter()
            C_objs = []
            S_objs = []
            T_objs = []
            # 遍历excel表中每一行数据
            for i in data:
                # 翻译赋值为英文方便存入数据库
                i[1] = trans.Consumable.consumable_dic[i[1]]
                i[6] = trans.Status.status_dic[i[6]]
                # 将时间字符串转换为时间格式，如果转换后的值为 NaT，则说明时间字符串不是合法的时间格式
                i[2] = pandas.to_datetime(i[2])
                # 将 Excel 中的数据转换为数值类型，如果转换后的值为 NaN，则说明数据不是合法的数值类型
                i[7] = pandas.to_numeric(i[7])
                i[8] = pandas.to_numeric(i[8])
                # 如果为空值则赋值为''
                i[14] = '' if pandas.isna(i[14]) else i[14]
                if i[2] == 'NaT':
                    msg = Msg.Language(lang).main().Excel.E02.format(user)
                    return JsonResponse(reply.warn(msg))
                if datetime.now() <= i[2]:
                    msg = Msg.Language(lang).main().Excel.E03.format(user)
                    return JsonResponse(reply.warn(msg))
                if i[7] == 'NaN' or i[8] == 'NaN':
                    msg = Msg.Language(lang).main().Excel.E02.format(user)
                    return JsonResponse(reply.warn(msg))
                if i[7] not in range(0, i[8] + 1) or i[8] <= 0:
                    msg = Msg.Language(lang).main().Excel.E04.format(user)
                    return JsonResponse(reply.warn(msg))
                # 对Excel文档中的数据进行卡控，数据或格式不正确则报错
                if i[0].strip() in sn_list:
                    msg = Msg.Language(lang).main().Excel.E01.format(i[0], 'Consumable', user)
                    return JsonResponse(reply.warn(msg))
                if i[1] not in ct_list:
                    msg = Msg.Language(lang).main().Common.C01.format('ConsumableType', i[1], user)
                    return JsonResponse(reply.warn(msg))
                if i[3] not in td_list:
                    msg = Msg.Language(lang).main().Common.C01.format('TypeDefinition', i[3], user)
                    return JsonResponse(reply.warn(msg))
                if i[4] not in td_list:
                    msg = Msg.Language(lang).main().Common.C01.format('TypeDefinition', i[4], user)
                    return JsonResponse(reply.warn(msg))
                if i[5] not in td_list:
                    msg = Msg.Language(lang).main().Common.C01.format('TypeDefinition', i[5], user)
                    return JsonResponse(reply.warn(msg))
                if i[6] not in ['Using', 'Stock', 'Scrapping', 'Scraped']:
                    msg = Msg.Language(lang).main().Excel.E02.format(user)
                    return JsonResponse(reply.warn(msg))
                if not pandas.isna(i[10]) and not pandas.isna(i[9]):
                    msg = Msg.Language(lang).main().Excel.E05.format(user)
                    return JsonResponse(reply.warn(msg))
                C_dic = {}
                C_dic.setdefault('sn', i[0].strip())
                C_dic.setdefault('ConsumableType_id', CT_objs.filter(name=i[1])[0].id)
                C_dic.setdefault('entertime', i[2])
                C_dic.setdefault('version_id', TD_objs.filter(name=i[3])[0].id)
                C_dic.setdefault('tooltype_id', TD_objs.filter(name=i[4])[0].id)
                C_dic.setdefault('model_id', TD_objs.filter(name=i[5])[0].id)
                C_dic.setdefault('status', i[6])
                C_dic.setdefault('usefullife', i[7])
                C_dic.setdefault('ratedlife', i[8])
                C_dic.setdefault('location', i[9] if not pandas.isna(i[9]) else '')
                C_dic.setdefault('position', i[10] if not pandas.isna(i[10]) else '')
                C_dic.setdefault('createtime', datetime.now())
                C_dic.setdefault('updateuser', user)
                C_dic.setdefault('updatetime', datetime.now())
                C_dic.setdefault('comment', i[14])
                C_dic.setdefault('inscrapping', False)
                C_dic.setdefault('pkg', True)
                C_dic.setdefault('mark', True)
                C_dic.setdefault('OQC', True)
                C_dic.setdefault('appearance', True)
                C_dic.setdefault('MeshPlugging', True)
                C_dic.setdefault('EmulsionShedding', True)
                C_objs.append(models.Consumable(**C_dic))
                if i[1] == 'Screen':
                    # 将间距信息存入Spacing表中
                    args = ['X', 'Y', 'Z']
                    a, ErrorRange = 0, 0.1
                    for arg in args:
                        S_dic = {}
                        if arg == 'Z':
                            ErrorRange = 0.15
                        # 外键关联，外键必须赋值一个Consumable实例而不是字符串
                        S_dic.setdefault('sn', models.Consumable(i[0].strip()))
                        S_dic.setdefault('Arg', arg)
                        S_dic.setdefault('StandardValue', i[15 + a])
                        S_dic.setdefault('ErrorRange', ErrorRange)
                        S_dic.setdefault('Arg1', '{}1'.format(arg))
                        S_dic.setdefault('MeasuredValue1', i[16 + a])
                        S_dic.setdefault('Arg2', '{}2'.format(arg))
                        S_dic.setdefault('MeasuredValue2', i[17 + a])
                        if not pandas.isna(i[15 + a]) and not pandas.isna(i[16 + a]) and not pandas.isna(i[17 + a]):
                            if isinstance(S_dic['StandardValue'], int):
                                StandardValue = S_dic['StandardValue']
                            else:
                                StandardValue = float(S_dic['StandardValue'])
                            if not StandardValue - ErrorRange <= float(S_dic['MeasuredValue1']) <= StandardValue + ErrorRange:
                                msg = Msg.Language(lang).main().Excel.E06.format(float(S_dic['MeasuredValue1']), user)
                                return JsonResponse(reply.warn(msg))
                            if not StandardValue - ErrorRange <= float(S_dic['MeasuredValue2']) <= StandardValue + ErrorRange:
                                msg = Msg.Language(lang).main().Excel.E06.format(float(S_dic['MeasuredValue2']), user)
                                return JsonResponse(reply.warn(msg))
                        else:
                            msg = Msg.Language(lang).main().Excel.E08.format(user)
                            return JsonResponse(reply.warn(msg))
                        a += 3
                        S_objs.append(models.Spacing(**S_dic))
                    # 将九点张力信息存入Tension表中
                    for n in range(9):
                        T_dic = {}
                        T_dic.setdefault('sn', models.Consumable(i[0].strip()))
                        T_dic.setdefault('Point', n + 1)
                        T_dic.setdefault('StandardValue', 24)
                        T_dic.setdefault('ErrorRange', 2)
                        T_dic.setdefault('MeasuredValue', i[24 + n])
                        if not pandas.isna(i[24 + n]):
                            if not T_dic['StandardValue'] - T_dic['ErrorRange'] <= T_dic['MeasuredValue'] <= T_dic['StandardValue'] + T_dic['ErrorRange']:
                                msg = Msg.Language(lang).main().Excel.E06.format(T_dic['MeasuredValue'], user)
                                return JsonResponse(reply.warn(msg))
                        else:
                            msg = Msg.Language(lang).main().Excel.E08.format(user)
                            return JsonResponse(reply.warn(msg))
                        T_objs.append(models.Tension(**T_dic))
            # 批量新建耗材附带所有基本信息
            models.Consumable.objects.bulk_create(C_objs)
            models.Spacing.objects.bulk_create(S_objs)
            models.Tension.objects.bulk_create(T_objs)
            transaction.savepoint_commit(sid)
            msg = Msg.Language(lang).main().Common.C02.format(gettext(self.title_name), user)
            return JsonResponse(reply.info(msg))
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return JsonResponse(reply.error(e))
