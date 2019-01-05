#!/usr/bin/python
# -*- coding:utf-8 -*-

from stark.service.stark import site, StarkConfig, get_choice_text, StarkModelForm, Option
from api import models
from django.utils.safestring import mark_safe  # 让html代码正常显示的
from stark.forms.widgets import DatePickerInput  # 定义时间样式的
from django.shortcuts import render


# 业务
class BusinessUnitConfig(StarkConfig):
    # 定制页面显示的列
    list_display = [StarkConfig.display_checkbox, 'id', 'name']

    # 定制模糊搜索
    search_list = ['name']
    # 排序 倒序排列
    order_by = ['-id', ]

    # 批量操作
    def multi_delete(self, request):
        pk_list = request.POST.getlist('pk')
        models.BusinessUnit.objects.filter(id__in=pk_list).delete()
        # 无返回值，返回当前页面,并删除你选中的数据
        from django.shortcuts import redirect
        # 有返回值，删除数据，并返回你自定义的一个页面
        return redirect('http://www.baidu.com')

    multi_delete.text = '批量操作'  # 必须这样写，因为用的别人的插件

    action_list = [multi_delete, ]  # 显示批量操作的按钮，不写就不显示


site.register(models.BusinessUnit, BusinessUnitConfig)


# idc机房
class IDCConfig(StarkConfig):
    list_display = ['name', 'floor', ]
    search_list = ['name', 'floor']


site.register(models.IDC, IDCConfig)


# 硬盘
class DiskConfig(StarkConfig):
    list_display = ['slot', 'capacity', 'server']
    search_list = ['slot', ]


site.register(models.Disk, DiskConfig)


# 内存
class MemoryConfig(StarkConfig):
    list_display = ['slot', 'capacity', 'model', 'server']
    search_list = ['slot', ]


site.register(models.Memory, MemoryConfig)


# 网卡
class NicConfig(StarkConfig):
    list_display = ['name', 'hwaddr', 'netmask', 'ipaddrs', 'server']
    search_list = ['name', 'ipaddrs']


site.register(models.NIC, NicConfig)


class ServerModelForm(StarkModelForm):
    """
    自定义一个modelform去继承StarkModelForm,用于显示时间样式
    """

    class Meta:
        model = models.Server
        fields = "__all__"
        widgets = {
            'latest_date': DatePickerInput(attrs={'class': 'date-picker'})

        }


class ServerConfig(StarkConfig):
    # 第一种写法
    # def display_status(self, row=None, header=False):
    #     if header:
    #         return '状态'
    #     from django.utils.safestring import mark_safe
    #     data = row.get_device_status_id_display()  # 如果想显示chionse类型的字段，需要get_字段名_display()
    #     tpl = "<span style='color:green'>%s</span>" % data
    #     return mark_safe(tpl)
    # 主机页面展示服务器的详细页面
    def display_detail(self, row=None, header=False):
        """
        查看详细
        :param row:
        :param header:
        :return:
        """
        if header:
            return '查看详细'
        return mark_safe("<a href='/stark/api/server/%s/detail/'>查看详细</a>" % row.id)

    def display_record(self, row=None, header=False):
        """
        查看详细
        :param row:
        :param header:
        :return:
        """
        if header:
            return '变更记录'
        return mark_safe("<a href='/stark/api/server/%s/record/'>变更记录</a>" % row.id)

    # 第二种写法
    list_display = [
        'hostname',
        'os_platform',
        'os_version',
        # display_status,
        'business_unit',
        'latest_date',
        get_choice_text('device_status_id', '状态'),  # device_status_id 这个是数据库的字段，状态是web页面上定义的标题
        display_detail,  # 注意自定义的字段不用加引号
        display_record,
    ]

    # 按字段快速搜索
    search_list = ['hostname', 'os_platform', 'business_unit__name']

    # 分类列表 Option需要导入
    list_filter = [
        # Option('business_unit',condition={'id__gt':0},is_choice=False,text_func=lambda x:x.name,value_func=lambda x:x.id,is_multi=True),
        Option('business_unit', condition={'id__gt': 0}, is_choice=False, text_func=lambda x: x.name,
               value_func=lambda x: x.id),
        Option('device_status_id', is_choice=True, text_func=lambda x: x[1], value_func=lambda x: x[0]),
    ]
    # 自定义ModelForm
    model_form_class = ServerModelForm  # 用来显示时间样式的

    def extra_url(self):
        """
        自定义扩展URL，必须用这个名字
        :return:
        """
        from django.conf.urls import url
        patterns = [
            url(r'^(?P<nid>\d+)/detail/$', self.detail_view),  # 主机详情url
            url(r'^(?P<nid>\d+)/record/$', self.record_view),  # 变更详情url
            # url(r'^login/$',self.login),
        ]
        return patterns
    # def login(self):


    def detail_view(self, request, nid):
        """
        主机详细页面的视图函数
        :param request:
        :param nid:
        :return:
        """
        base_list = models.Server.objects.filter(id=nid)
        nic_list = models.NIC.objects.filter(server_id=nid)
        memory_list = models.Memory.objects.filter(server_id=nid)
        disk_list = models.Disk.objects.filter(server_id=nid)

        context = {
            'base_list': base_list,
            'nic_list': nic_list,
            'memory_list': memory_list,
            'disk_list': disk_list,
        }
        return render(request, 'server_detail.html', context)

    def record_view(self, request, nid):
        """
        变更记录页面
        :param request:
        :param nid:
        :return:
        """
        record_list = models.AssetRecord.objects.filter(server_id=nid)
        context = {
            'record_list': record_list,

        }
        return render(request, 'server_record.html', context)


site.register(models.Server, ServerConfig)
