from talon import Module, Context

mod = Module()
mod.list("codesaway_symbol_key", desc="extra symbol keys")

ctx = Context()
ctx.lists["user.codesaway_symbol_key"] = {
    "semi": ";",
    "quotes": '"',
}


# Reference: https://old.talon.wiki/unofficial_talon_docs/
@ctx.capture("user.symbol_key", rule="{user.symbol_key} | {user.codesaway_symbol_key}")
def symbol_key(m):
    return str(m)
