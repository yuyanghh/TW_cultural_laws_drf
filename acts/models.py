from django.db import models
from datetime import date


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Act(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=500, unique=True)  # 法案名稱
    pcode = models.CharField(max_length=30, unique=True, blank=True)  # 法案Pcode
    valid_state = models.CharField(
        max_length=300, unique=True, blank=True)  # 法案生效狀態
    act_type = models.CharField(max_length=30, blank=True)  # 位階
    legislated_at = models.DateField(blank=True, null=True)  # 制定日期
    amended_at = models.DateField(blank=True, null=True)  # 修正日期
    announced_at = models.DateField(blank=True, null=True)  # 公佈日期
    applied_at = models.DateField(blank=True, null=True)  # 施行日期
    rich_content = models.TextField(unique=True, blank=True)  # 現行法案全文
    keyword = models.TextField(blank=True)  # 現行法案全文關鍵字


class Article(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    rich_content = models.TextField(blank=True, unique=True)  # 現行法條全文
    act = models.ForeignKey('Act', related_name='articles',
                            on_delete=models.CASCADE)  # 所屬法案
    chapter_nr = models.IntegerField(blank=True)  # 章節
    article_nr = models.IntegerField()  # 條目
    legislated_at = models.DateField(blank=True, null=True)  # 制定日期
    amended_at = models.DateField(blank=True, null=True)  # 修正日期
    announced_at = models.DateField(blank=True, null=True)  # 公佈日期
    applied_at = models.DateField(blank=True, null=True)  # 施行日期
    keyword = models.TextField(blank=True)  # 現行法條全文關鍵字
    updated_reason = models.TextField(blank=True)  # 條文修正/制定理由
    deliberation_duration = models.IntegerField(blank=True)  # 立法歷程天數
    appended_decision = models.TextField(blank=True)  # 附帶決議連結


class Legislation(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    article = models.ForeignKey(
        'Article', related_name='legislations', on_delete=models.CASCADE)  # 所屬法條
    procedure_schedule = models.CharField(
        max_length=30)  # 議案進度(一讀、二讀、委員會審查、三讀...)
    sittings_date = models.DateField()  # 會議日期
    gazette = models.TextField(blank=True)  # 立法院公報紀錄連結
    main_proposer = models.CharField(max_length=30, blank=True)  # 主提案
    related_doc = models.TextField(blank=True)  # 關係文書連結
