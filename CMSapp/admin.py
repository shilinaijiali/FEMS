import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.core.exceptions import ValidationError
from django.forms import TextInput, BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

from CMSapp.models import *

mylog = logging.getLogger('CMS')

admin.site.site_title = "消防器材信息化管理系统"
admin.site.index_title = "消防器材信息化管理系统"
admin.site.site_header = "消防器材信息化管理系统"


class ErrorTextInput(TextInput):
    def __init__(self, attrs=None):
        self.attrs = attrs
        attrs = {'class': 'error'}  # 添加 'error' 类到属性中
        super().__init__(attrs)


class ConsumableTypeAdmin(admin.ModelAdmin):
    list_display = ['translated_name', 'comment', 'lastupdate']
    ordering = ['name']
    search_fields = ('name',)
    save_as = True

    # 翻译name字段中的所有值
    def translated_name(self, obj):
        return _(obj.name)

    translated_name.short_description = '名稱'


admin.site.register(ConsumableType, ConsumableTypeAdmin)


class TypeGroupForm(forms.ModelForm):
    class Meta:
        model = TypeGroup
        fields = '__all__'

    # 翻译外键下拉框中的选项
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ConsumableType'].choices = [('', '--------')] + [(ct.pk, _(ct.name)) for ct in self.fields['ConsumableType'].queryset]


class TypeGroupAdmin(admin.ModelAdmin):
    form = TypeGroupForm
    list_display = ['translated_name', 'translated_ConsumableType', 'comment', 'lastupdate']
    ordering = ['name']
    search_fields = ('name',)
    save_as = True

    # 翻译name字段中的所有值
    def translated_name(self, obj):
        return _(obj.name)

    translated_name.short_description = '名稱'

    # 翻译ConsumableType字段中的所有值
    def translated_ConsumableType(self, obj):
        return _(obj.ConsumableType.name)

    translated_ConsumableType.short_description = '耗材類型'


admin.site.register(TypeGroup, TypeGroupAdmin)


class TypeDefinitionForm(forms.ModelForm):
    class Meta:
        model = TypeDefinition
        fields = '__all__'

    # 翻译外键下拉框中的选项
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typegroup'].choices = [('', '--------')] + [(td.pk, _(td.name)) for td in self.fields['typegroup'].queryset]


class TypeDefinitionAdmin(admin.ModelAdmin):
    form = TypeDefinitionForm
    list_display = ['name', 'translated_typegroup', 'comment', 'lastupdate']
    list_filter = ['typegroup']
    ordering = ['typegroup', 'name']
    search_fields = ('name',)
    save_as = True

    # 翻译typegroup字段中的所有值
    def translated_typegroup(self, obj):
        return _(obj.typegroup.name)

    translated_typegroup.short_description = '類型群組'


admin.site.register(TypeDefinition, TypeDefinitionAdmin)


class DimensionalRecordInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            StandardValue = form.cleaned_data.get('StandardValue')
            ErrorRange = form.cleaned_data.get('ErrorRange')
            MeasuredValue = form.cleaned_data.get('MeasuredValue')
            if StandardValue is not None and ErrorRange is not None and MeasuredValue is not None:
                if not (StandardValue - ErrorRange <= MeasuredValue <= StandardValue + ErrorRange):
                    form.add_error('MeasuredValue', _('MeasuredValue must be within range StandardValue ± ErrorRange.'))


class DimensionalRecordInline(admin.TabularInline):
    model = DimensionalRecord
    formset = DimensionalRecordInlineFormSet
    fields = ['TestPoint', 'StandardValue', 'ErrorRange', 'MeasuredValue', ]
    extra = 0  # 设置初始行数为0，即不显示任何行
    classes = ['collapse']  # 折叠该inline
    formfield_overrides = {
        models.DecimalField: {'widget': ErrorTextInput},
    }


class BladeWidthInline(admin.TabularInline):
    model = BladeWidth
    fields = ['Point', 'Value']
    extra = 0  # 设置初始行数为0，即不显示任何行
    classes = ['collapse']  # 折叠该inline


class BladeAngleInline(admin.TabularInline):
    model = BladeAngle
    fields = ['Angle', 'Value']
    extra = 0  # 设置初始行数为0，即不显示任何行
    classes = ['collapse']  # 折叠该inline


class SpacingInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 在初始化表单集合时进行修改
        arg_names = ['X', 'Y', 'Z']
        arg1_names = ['X1', 'Y1', 'Z1']
        arg2_names = ['X2', 'Y2', 'Z2']
        default_error_ranges = [0.1, 0.1, 0.15]
        for i in range(len(arg_names)):
            self.forms[i].initial['Arg'] = arg_names[i]
            self.forms[i].initial['Arg1'] = arg1_names[i]
            self.forms[i].initial['Arg2'] = arg2_names[i]
            self.forms[i].initial['ErrorRange'] = default_error_ranges[i]

    def clean(self):
        super().clean()
        for form in self.forms:
            StandardValue = form.cleaned_data.get('StandardValue')
            ErrorRange = form.cleaned_data.get('ErrorRange')
            MeasuredValue1 = form.cleaned_data.get('MeasuredValue1')
            MeasuredValue2 = form.cleaned_data.get('MeasuredValue2')
            if StandardValue is not None and ErrorRange is not None and MeasuredValue1 is not None:
                if not (StandardValue - ErrorRange <= MeasuredValue1 <= StandardValue + ErrorRange):
                    form.add_error('MeasuredValue1', _('MeasuredValue must be within range StandardValue ± ErrorRange.'))
            if StandardValue is not None and ErrorRange is not None and MeasuredValue2 is not None:
                if not (StandardValue - ErrorRange <= MeasuredValue2 <= StandardValue + ErrorRange):
                    form.add_error('MeasuredValue2', _('MeasuredValue must be within range StandardValue ± ErrorRange.'))


class SpacingInline(admin.TabularInline):
    model = Spacing
    fields = ['Arg', 'StandardValue', 'ErrorRange', 'Arg1', 'MeasuredValue1', 'Arg2', 'MeasuredValue2']
    extra = 3  # 设置初始行数为3
    classes = ['collapse']  # 折叠该inline
    # 调整输入框长度
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 40%;'})},
        models.DecimalField: {'widget': ErrorTextInput},
    }
    formset = SpacingInlineFormSet


class TensionInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 在初始化表单集合时进行修改
        StandardValue = 24
        ErrorRange = 2
        for i in range(9):
            self.forms[i].initial['Point'] = i + 1
            self.forms[i].initial['StandardValue'] = StandardValue
            self.forms[i].initial['ErrorRange'] = ErrorRange

    def clean(self):
        super().clean()
        for form in self.forms:
            StandardValue = form.cleaned_data.get('StandardValue')
            ErrorRange = form.cleaned_data.get('ErrorRange')
            MeasuredValue = form.cleaned_data.get('MeasuredValue')
            if StandardValue is not None and ErrorRange is not None and MeasuredValue is not None:
                if not (StandardValue - ErrorRange <= MeasuredValue <= StandardValue + ErrorRange):
                    form.add_error('MeasuredValue', _('MeasuredValue must be within range StandardValue ± ErrorRange.'))


class TensionInline(admin.TabularInline):
    model = Tension
    fields = ['Point', 'StandardValue', 'ErrorRange', 'MeasuredValue']
    extra = 9  # 设置初始行数为9
    classes = ['collapse']  # 折叠该inline
    formfield_overrides = {
        models.DecimalField: {'widget': ErrorTextInput},
    }
    formset = TensionInlineFormSet


class ConsumableForms(forms.ModelForm):
    location = forms.CharField(label=_('Location'), max_length=40, required=True)

    # ConsumableType = forms.ModelChoiceField(label=_('ConsumableType'), queryset=ConsumableType.objects.all())
    # version = forms.ModelChoiceField(label=_('version'), queryset=TypeDefinition.objects.none())    # 设置选项为空
    # tooltype = forms.ModelChoiceField(label=_('tooltype'), queryset=TypeDefinition.objects.none())
    # model = forms.ModelChoiceField(label=_('model'), queryset=TypeDefinition.objects.none())

    class Meta:
        model = Consumable
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].error_messages = {
            'required': _('Please enter a location'),
        }
        # 翻译外键下拉框中的选项
        self.fields['ConsumableType'].choices = [('', '--------')] + [(ct.pk, _(ct.name)) for ct in self.fields['ConsumableType'].queryset]


class ConsumableAdmin(admin.ModelAdmin):
    form = ConsumableForms
    # 设置只读字段
    readonly_fields = ('status', 'pkg', 'mark', 'OQC', 'appearance',)
    list_display = ['sn', 'ConsumableType', 'version', 'model', 'tooltype', 'status', 'entertime', 'ratedlife', 'usefullife', 'location']
    search_fields = ('sn',)
    list_filter = ['model', 'version', 'status']
    fieldsets = [
        (_('Basic Settings'), {
            'fields': (
                ('sn', 'ConsumableType', 'model',),
                ('version', 'tooltype', 'entertime'),
                ('ratedlife', 'usefullife', 'location'),
                ('comment', 'status'),
            ),
            # 'classes': ('collapse',),
        }),
        (_('Moulds Info'), {
            'classes': ('collapse',),
            'fields': (('pkg', 'mark', 'OQC', 'appearance'),),
        }),
        (_('Screen Info'), {
            'classes': ('collapse',),
            'fields': (('EmulsionShedding', 'MeshPlugging',),),
        }),
        (_('Advanced Settings'), {
            'fields': (),
        }),
        # (_('External Settings'), {
        #     'fields': (),
        # }),
    ]
    ordering = ['sn']
    save_as = True
    list_per_page = 15
    inlines = [DimensionalRecordInline, BladeWidthInline, BladeAngleInline, SpacingInline, TensionInline]

    # 重写方法，实现自定义只读字段
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        obj.checkoutuser = str(request.user.username)
        obj.updateuser = str(request.user.username)
        obj.save()


admin.site.register(Consumable, ConsumableAdmin)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'user', 'action_time', 'object_id', 'object_repr', 'action_flag', 'change_message']
    list_per_page = 15
    search_fields = ('content_type__app_label',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['equipment_type', ]
    list_per_page = 15
    list_filter = ['equipment_type', ]
    search_fields = ['equipment_type', ]
    ordering = ['equipment_type']
    save_as = True


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ['plot', ]
    list_per_page = 15
    list_filter = ['plot', ]
    search_fields = ['plot', ]
    ordering = ['plot']
    save_as = True


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ['build', ]
    list_per_page = 15
    list_filter = ['build', ]
    search_fields = ['build', ]
    ordering = ['build']
    save_as = True


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ['floor', ]
    list_per_page = 15
    list_filter = ['floor', ]
    search_fields = ['floor', ]
    ordering = ['floor']
    save_as = True


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room', ]
    list_per_page = 15
    list_filter = ['room', ]
    search_fields = ['room', ]
    ordering = ['room']
    save_as = True


@admin.register(EquipmentInfo)
class EquipmentInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'status', 'plot', 'build', 'floor', 'room', 'create_time', 'produced_date', 'expired_date', 'inspection_period', 'inspected', 'update_time']
    list_per_page = 15
    list_filter = ['name', 'equipment_type', 'status']
    search_fields = ['name', 'equipment_type', 'status']
    ordering = ['name']
    save_as = True
