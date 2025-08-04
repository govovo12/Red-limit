import os
import subprocess

def run_cmd(command):
    print(f"\n👉 執行：{command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("❌ 指令執行失敗，終止流程。")
        exit(1)

def generate_requirements():
    run_cmd("pip freeze > requirements.txt")
    print("✅ requirements.txt 已更新")

def git_add_all():
    run_cmd("git add .")
    print("✅ 已執行 git add .")

def get_branch():
    branch = input("📌 要 push 到哪個分支？（例如 main 或 dev）：").strip()
    if not branch:
        print("❌ 未輸入分支名稱，終止")
        exit(1)
    return branch

def get_commit_message():
    message = input("📝 請輸入 commit 訊息：").strip()
    if not message:
        print("❌ 未輸入 commit 訊息，終止")
        exit(1)
    return message

def git_commit_push(branch, message):
    run_cmd(f'git commit -m "{message}"')
    run_cmd(f"git push origin HEAD:{branch} --force")
    print(f"✅ 已強制推送到遠端分支 {branch}")

def main():
    generate_requirements()
    git_add_all()
    branch = get_branch()
    message = get_commit_message()
    git_commit_push(branch, message)

if __name__ == "__main__":
    main()
