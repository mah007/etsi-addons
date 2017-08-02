# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VesselType(models.Model):
    _name = "vessel.type"
    _description = "Vessel Type"
    # _inherit = ['mail.thread']

    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")


class PortRegistry(models.Model):
    _name = "port.registry"
    _description = "Port Registry"

    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")


class VesselEngine(models.Model):
    _name = "vessel.engine"
    _description = "Vessel Engine"

    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")


class TradeRoute(models.Model):
    _name = "trade.route"
    _description = "Trade Route"

    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")


class VesselStatus(models.Model):
    _name = "vessel.status"
    _description = "Vessel Status"

    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")


class PortEmbarkation(models.Model):
    _name = "port.embarkation"
    _description = "Port Embarcation"
    _order = "country_id,name"

    name = fields.Char(string="Name")
    desc = fields.Text(string="Description")
    country_id = fields.Many2one('res.country',string="Country")
