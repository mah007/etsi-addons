
from odoo import api, fields, models, _

class Resource_Calendar(models.Model):
    _inherit = "resource.calendar"

    am_in = fields.Float(string="AM In", digits=(16 ,2))
    am_out = fields.Float(string="AM Out", digits=(16 ,2))
    pm_in = fields.Float(string="PM In", digits=(16 ,2))
    pm_out = fields.Float(string="PM Out", digits=(16 ,2))
    no_days_week = fields.Float(string="No. of Days per Week")
    flex_attendance_ids = fields.One2many('resource.calendar.attendance', 'calendar_id' ,string="Working Time")
    daily_attendance_ids = fields.One2many('resource.calendar.attendance', 'calendar_id', string="Working Time")
    work_type = fields.Selection([('daily' ,'Daily') ,('weekly' ,'Weekly') ,('flexi' ,'Flexi')], string="Type", default='weekly')
    flexi_type = fields.Selection([
        ('band', 'Flex Band'),
        ('range', 'Flex Range'),
        ('core', 'Flex Core'),
        ('core_plus', 'Flex Core Plus')], string="Flexi Type", index=True)

    @api.onchange('work_type')
    def onchange_work_type(self):
        context = self.env.context
        for rec in self.attendance_ids:
            rec.work_type = self.work_type
            rec.flexi_type

    @api.onchange('flexi_type')
    def onchange_flexi_type(self):
        for rec in self.attendance_ids:
            rec.work_type = self.work_type
            rec.flexi_type = self.flexi_type


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week', required=False, index=True, default='0')
    work_type = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ('flexi','Flexi')],compute='get_work_type')
    sched_hours = fields.Float(string="Scheduled Hours", digits=(16,2))
    flexi_type = fields.Selection([
        ('band', 'Flex band'),
        ('range', 'Flex Range'),
        ('core', 'Flex Core'),
        ('core_plus', 'Flex Core Plus')], string="Flexi Type")
    flex_start = fields.Float(string="Flex Start")
    flex_end = fields.Float(string="Flex End")
    flex_week_hours = fields.Float(string="Flex Weekly Hours")



    # @api.model
    # def default_get(self, fields):
    #     print 'context', self.env.context

    @api.onchange('name')
    def get_work_type(self):
        context =  self.env.context
        for rec in self:
            work_type = rec.calendar_id.work_type
            flex_type = rec.calendar_id.flexi_type
            rec.work_type = work_type
            rec.flexi_type = flex_type
            if rec.work_type == 'daily':
                rec.dayofweek = False
