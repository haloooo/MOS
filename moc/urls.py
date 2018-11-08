"""sf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from MfcOpeSys.views import view_, view_assy, view_configure, view_summary_offset, view_progress, view_trend_chart
from MfcOpeSys.views import view_index
from MfcOpeSys.views import view_manufacture
from MfcOpeSys.views import view_ngreport
from MfcOpeSys.views import view_search
from MfcOpeSys.views import view_chart
from MfcOpeSys.views import view_worktime
from django.views.generic.base import RedirectView


urlpatterns = [
    url(r'^favicon.ico$',RedirectView.as_view(url=r'static/images/favicon.ico')),
    url(r'^$',view_index.go_index),
    url(r'^go_manufacture', view_manufacture.go_manufacture),
    url(r'^go_chart', view_chart.go_chart),
    url(r'^go_ngreport', view_ngreport.go_ngreport),
    url(r'^go_assy', view_.go_assy),
    url(r'^go_sttype', view_.go_sttype),
    url(r'^go_config', view_.go_config),
    url(r'^go_summary_offset', view_.go_summary_offset),
    url(r'^get_models', view_index.get_models),
    url(r'^get_lines', view_.get_lines),
    url(r'^get_assys', view_.get_assys),
    url(r'^get_datatypeIds', view_.get_datatypeIds),
    url(r'^get_tps', view_.get_tps),
    url(r'^get_1_processdetail', view_.get_1_processdetail),
    url(r'^get_2_processdetail', view_.get_2_processdetail),
    url(r'^get_1_defectdetail', view_.get_1_defectdetail),
    url(r'^get_2_defectdetail', view_.get_2_defectdetail),
    url(r'^upload', view_ngreport.upload),
    url(r'^insertDatabase', view_ngreport.insertDatabase),
    url(r'^exits_mplan', view_ngreport.exits_mplan),
    url(r'^initAssyData', view_assy.initAssyData),
    url(r'^update_assy', view_assy.update_assy),
    url(r'^get_summaryDetail', view_.get_summaryDetail),
    url(r'^add_worktime', view_worktime.add_worktime),
    url(r'^del_worktime', view_worktime.del_worktime),
    url(r'^del_worktime_detail', view_worktime.del_worktime_detail),
    url(r'^edit_worktime_detail', view_worktime.edit_worktime_detail),
    url(r'^get_worktime', view_worktime.get_worktime),
    url(r'^initConfigureData', view_configure.initConfigureData),
    url(r'^get_time_tbl_cd', view_configure.get_workTime),
    url(r'^get_assytext', view_configure.get_assytext),
    url(r'^update_worktime', view_configure.update_worktime),
    url(r'^update_sttype', view_worktime.update_sttype),
    url(r'^get_lineSummaryDetail', view_.get_lineSummaryDetail),
    url(r'^initSummaryOffsetData', view_summary_offset.initSummaryOffsetData),
    url(r'^update_summary_offset', view_summary_offset.update_summary_offset),
    url(r'^getServerDate', view_.getServerDate),
    url(r'^getFullServerDate', view_.getFullServerDate),
    url(r'^getTodayServerDate',view_.getTodayServerDate),
    url(r'^getLine', view_.getLine),
    url(r'^get_select_content',view_chart.get_select_content),
    url(r'^search_chart',view_chart.search_chart),
    url(r'^getSummaryTimeType',view_ngreport.getSummaryTimeType),
    url(r'^getStartEndTime',view_ngreport.getStartEndTime),
    url(r'^go_upload',view_.go_upload),
    url(r'^go_history',view_.go_history),
    url(r'^search_history',view_search.search_history),
    url(r'^get_history_targrt',view_search.get_history_targrt),
    url(r'^get_history_assy',view_search.get_history_assy),
    url(r'^go_defect',view_.go_defect),
    url(r'^search_defect',view_.search_defect),
    url(r'^get_toprank',view_search.get_toprank),
    url(r'^get_Achievement_Rate',view_ngreport.get_Achievement_Rate),
    url(r'^get_Trend_Data',view_search.get_Trend_Data),
    url(r'^checkConnection',view_.checkConnection),
    url(r'^get_sntracert', view_.get_sntracert),
    url(r'^go_sntracert', view_.go_sntracert),
    url(r'^get_configs', view_.get_configs),
    url(r'^go_progress', view_progress.go_progress),
    url(r'^getAutoUpdatings', view_progress.getAutoUpdatings),
    url(r'^getProcessDetail',view_progress.getProcessDetail),
    url(r'^getObjs',view_search.getObjs),
    url(r'^getDataType',view_search.getDataType),
    url(r'^go_trend_chart', view_trend_chart.go_trend_chart),
    url(r'^search_trend',view_trend_chart.search_trend),
    url(r'^getDataType',view_search.getDataType),
    url(r'^getInspect', view_trend_chart.get_inspect)
]
