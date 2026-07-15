<p align="center">
  <img src="assets/finuslugi-base.png" alt="Финуслуги" width="180">
</p>

# Finuslugi 3D Visual Pipeline

Skill-only Codex plugin для управляемого производства 3D-иллюстраций Финуслуг: от коммуникационной задачи и набора референсов до проверенного финального изображения.

## Что делает репозиторий

Пайплайн разделяет дизайнерское решение и генерацию. Навык:

1. фиксирует задачу, метафору и главный объект;
2. назначает каждому референсу отдельную роль;
3. формирует Scene Specification как источник правды;
4. выбирает один версионированный style pack;
5. строит один промпт или последовательность промптов;
6. выполняет предгенерационный контроль;
7. передаёт исполнение доступному image-generation инструменту;
8. проводит визуальный QA и диагностические локальные итерации;
9. фиксирует output manifest;
10. гарантирует видимую пользовательскую выдачу финального изображения.

## Целевая архитектура

```text
finuslugi-3d-visual-pipeline/
|-- .codex-plugin/
|   `-- plugin.json
|-- assets/
|   |-- finuslugi-base.png
|   |-- finuslugi-inverted.png
|   |-- manifest.json
|   `-- checksums.sha256
|-- docs/
|   `-- decisions/
|-- skills/
|   `-- finuslugi-3d-visual-pipeline/
|       |-- SKILL.md
|       |-- agents/
|       |-- references/
|       |-- assets/
|       |   `-- schemas/
|       |-- scripts/
|       `-- evals/
|-- AGENTS.md
|-- CHANGELOG.md
|-- LICENSE
`-- README.md
```

## Канонические контракты

- runtime-порядок: `skills/finuslugi-3d-visual-pipeline/SKILL.md`;
- Scene Specification: `skills/finuslugi-3d-visual-pipeline/references/scene-specification.md`;
- JSON Schema сцены: `skills/finuslugi-3d-visual-pipeline/assets/schemas/scene-spec.schema.json`;
- output manifest: `skills/finuslugi-3d-visual-pipeline/assets/schemas/output-manifest.schema.json`;
- source traceability: `skills/finuslugi-3d-visual-pipeline/references/source-map.md`;
- архитектурные решения: `docs/decisions/`.

## Style packs

| Style pack | Версия | Статус в репозитории |
|---|---:|---|
| Modern Flat | 2.1 | основной канонический |
| Silver-Gold | 3.1 | каноническая спецификация, контролируемое применение |
| Obsidian Gold | 1.0 | каноническая спецификация, контролируемое применение |

Техническая валидность style pack не означает автоматическое согласование конкретного продуктового или маркетингового применения.

## Цифровой след

- архитектура: [Issue #1](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/1);
- канонический навык: [Issue #2](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/2);
- style packs: [Issue #3](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/3);
- eval-контур: [Issue #4](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/4);
- validator и schemas: [Issue #5](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/5);
- runtime adapters: [Issue #6](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/6);
- asset governance: [Issue #7](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/7);
- release: [Issue #8](https://github.com/sevranty/finuslugi-3d-visual-pipeline/issues/8).

## Статус

`0.1.0` — архитектурная и каноническая draft-версия.

Уже реализованы:

- plugin manifest;
- канонический orchestration skill;
- три нормализованных style pack;
- Scene Specification и output manifest schemas;
- diagnostic codes;
- позитивные и негативные eval fixtures;
- stdlib-only repository validator;
- asset manifest и SHA-256 checksums;
- ADR и source map.

До production-ready остаются:

- локальный validation evidence на зафиксированном HEAD;
- утверждённый golden set;
- visual regression runs;
- runtime capability adapters;
- проверка прав публичного распространения брендовых и эталонных ассетов;
- installation smoke test и release gates.

## Брендовые активы

- светлый или белый фон: `assets/finuslugi-base.png`;
- красный или тёмный фон: `assets/finuslugi-inverted.png`;
- фирменный цвет Финуслуг и MOEX: `#FF0508`;
- логотип не генерируется и добавляется после генеративного прохода.

Статус прав и разрешённые роли файлов фиксируются в `assets/manifest.json`.

## Локальная проверка

```bash
python3 skills/finuslugi-3d-visual-pipeline/scripts/validate_repository.py
```

Validator проверяет структуру plugin, frontmatter, ASCII-пути, относительные ссылки, версии style pack, schemas, positive/negative fixtures, asset manifest и checksums. Visual QA он не заменяет.

## Лицензия

MIT применяется к коду и оригинальной документации репозитория. Права на товарные знаки, логотипы, внутренние исходные документы и сторонние референсы регулируются отдельно.
