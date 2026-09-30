from talon import Module

mod = Module()

apps = mod.apps
apps.heidisql = """
os: windows
and app.exe: heidisql.exe
"""
