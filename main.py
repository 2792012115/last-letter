"""
AI "最后一封信" - 命令行交互版
运行: python main.py
"""

from letter_engine import (
    RELATIONSHIP_PRESETS,
    LetterSession,
    get_questions,
    generate_letter,
    format_letter_for_display,
)


def clear_screen():
    """清屏"""
    print("\033[2J\033[H", end="")


def main():
    clear_screen()

    print("""
╔══════════════════════════════════════╗
║     ✉️  如果明天不在了              ║
║     你想对谁说些什么？              ║
╚══════════════════════════════════════╝
    """)

    # ---- 第 1 步：选择关系 ----
    print("📌 这封信写给谁？\n")
    relationships = list(RELATIONSHIP_PRESETS.keys())
    for i, key in enumerate(relationships, 1):
        preset = RELATIONSHIP_PRESETS[key]
        print(f"  [{i}] {preset['icon']}  {preset['label']}")

    print()
    while True:
        choice = input("👉 输入编号 (1-{}): ".format(len(relationships))).strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(relationships):
                relationship = relationships[idx]
                break
        except ValueError:
            pass
        print("  ⚠️ 请输入有效编号")

    # ---- 第 2 步：称呼 ----
    preset = RELATIONSHIP_PRESETS[relationship]
    clear_screen()
    print(f"\n{preset['icon']}  {preset['label']}\n")

    if relationship == "自定义":
        recipient = input("👉 TA 的名字/称呼: ").strip() or "你"
    else:
        default_name = relationship
        recipient = input(f"👉 称呼（直接回车用「{default_name}」）: ").strip() or default_name

    # ---- 第 3 步：AI 引导提问 ----
    questions = get_questions(relationship)
    answers = []

    for i, question in enumerate(questions, 1):
        clear_screen()
        print(f"\n{preset['icon']}  {preset['label']}  →  {recipient}\n")
        print(f"━━━ 第 {i}/{len(questions)} 问 ━━━\n")
        print(f"  💭 {question}\n")
        answer = input("  ✍️  你的回答: ").strip()
        if not answer:
            answer = "（这个问题我暂时不知道怎么回答）"
        answers.append(answer)

    # ---- 第 4 步：生成 ----
    clear_screen()
    print(f"\n{preset['icon']}  正在为你书写...\n")
    print("  ✍️  整理你的回答...")
    print("  💡  寻找合适的词句...")
    print("  📝  落笔成信...\n")

    session = LetterSession(
        relationship=relationship,
        recipient_name=recipient,
        answers=answers,
        questions=questions,
    )

    try:
        letter, keywords = generate_letter(session)
    except Exception as e:
        print(f"\n  ❌ 生成失败: {e}")
        print("  请确认 .env 中 OPENAI_API_KEY 已正确配置")
        return

    # ---- 第 5 步：展示 ----
    clear_screen()
    formatted = format_letter_for_display(letter, keywords, session)
    print(formatted)

    print("\n  📋 选项:")
    print("  [S] 保存到文件")
    print("  [R] 重新写一封")
    print("  [Q] 退出")
    choice = input("\n👉 ").strip().upper()

    if choice == "S":
        filename = f"最后一封信_给{recipient}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"\n  ✅ 已保存到: {filename}")
    elif choice == "R":
        main()
        return


if __name__ == "__main__":
    main()
