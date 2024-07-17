app: vscode
-
git diff all [<user.text>]:
    user.vscode("gitlens.externalDiffAll")
    sleep(100ms)
    insert(text or "")
