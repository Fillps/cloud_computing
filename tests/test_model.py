# -*- coding: utf-8 -*-
from cloud_computing.model.models import ServerRam

from cloud_computing.model import models
from tests.conftest import session


def test_user_model(user_data):
    users = models.User.query.all()
    assert len(users) == len(user_data)


def test_cpu_model(cpu_data):
    cpus = models.Cpu.query.all()
    assert len(cpus) == len(cpu_data)


def test_gpu_model(gpu_data):
    gpus = models.Gpu.query.all()
    assert len(gpus) == len(gpu_data)


def test_ram_model(ram_data):
    rams = models.Ram.query.all()
    assert len(rams) == len(ram_data)


def test_hd_model(hd_data):
    hds = models.Hd.query.all()
    assert len(hds) == len(hd_data)


def test_os_model(os_data):
    osos = models.Os.query.all()
    assert len(osos) == len(os_data)


def test_plan_model(plan_data):
    plans = models.Plan.query.all()
    assert len(plans) == len(plan_data)


def test_server_model(server_data):
    servers = models.Server.query.all()
    assert len(servers) == len(server_data)


def test_server_ram_model(server_ram_data):
    server_rams = models.ServerRam.query.all()
    s_r = server_rams[0]
    assert len(server_rams) == len(server_ram_data)
    assert s_r.quantity == s_r.ram.total - s_r.ram.available
    assert s_r.quantity * s_r.ram.capacity == s_r.server.ram_total
    assert s_r.quantity * s_r.ram.capacity == s_r.server.ram_available
    assert s_r.quantity == s_r.server.ram_slot_total - s_r.server.ram_slot_available


def test_server_start_cores(server_data):
    servers = models.Server.query.all()
    sv = servers[0]
    assert sv.cores_available == sv.cpu.cores
    
    
def test_credit_card_model(credit_card_data):
    credit_cards = models.CreditCard.query.all()
    assert len(credit_cards) == len(credit_card_data)
    
def test_purchase_model(purchase_data):
    purchases = models.Purchase.query.all()
    assert len(purchases) == len(purchase_data)

def test_user_plan_model(purchase_data):
    purchases = models.Purchase.query.all()
    purchase = purchases[0]
    assert purchase.user_plan.user_id == purchase.credit_card.user_id