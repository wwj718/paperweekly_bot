#!/usr/bin/env python
# encoding: utf-8

def run(**kwargs):
    msg = kwargs.get("msg")
    print({"plugin1":msg})
