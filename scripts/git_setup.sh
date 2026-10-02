#!/usr/bin/env bash
# Подготовка репозитория и ветки для пул-реквеста.
# Перед запуском создайте на GitHub/GitLab ПУСТОЙ ПУБЛИЧНЫЙ репозиторий «architecture-standart»
# (без README и .gitignore) и возьмите его адрес.
#
# Использование:  bash scripts/git_setup.sh https://github.com/abeginyan/architecture-standart.git
set -euo pipefail

REPO_URL="https://github.com/abeginyan/architecture-standart.git"
cd "$(dirname "$0")/.."

git init -b main
git remote add origin "$REPO_URL"

# 1) Базовый коммит в основной ветке: пустые директории Task1–Task4 + README
for d in Task1 Task2 Task3 Task4; do touch "$d/.gitkeep"; done
git add README.md Task1/.gitkeep Task2/.gitkeep Task3/.gitkeep Task4/.gitkeep
git commit -m "Initial structure: Task1-Task4"
git push -u origin main

# 2) Ветка с решениями
git checkout -b sprint3-solution
git add -A
git commit -m "Sprint 3: IT landscape, FURPS+, ADR online deposits, ADR rates for call centers, RoadMap"
git push -u origin sprint3-solution

echo
echo "Готово. Откройте репозиторий в браузере и создайте Pull Request: sprint3-solution -> main."
echo "Ссылку на пул-реквест отправьте во вкладке «Ревью»."
