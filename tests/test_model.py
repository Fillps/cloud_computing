# -*- coding: utf-8 -*-
from cloud_computing.model.models import ServerRam
from conftest import session, db
from cloud_computing.model import models


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

def test_insert_ram_model(server_data, ram_data):
    session.add(ServerRam(server_data[0].id, ram_data[0].id, 10))
    server_data[0].rams[0].quantity -= 10
    assert server_data[0].server_ram[0].quantity == 0