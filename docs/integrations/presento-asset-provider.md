# Presento asset-provider boundary

Issue: 3DP#38

3DP accepts the optional Presento request/result boundary for raster and 3D render results.

- Request: `presento.asset-provider.request.v1` / `1.0.0`
- Result: `presento.asset-provider.result.v1` / `1.0.0`
- 3DP retains provider runtime and rendering ownership.
- Result must include exact provider revision, canonical configuration SHA-256, asset path and checksum provenance.
- Failures must be machine-readable.
- Contract tests must not require paid calls or secrets.
- No runtime dependency 3DP -> Presento is introduced.
- Source: https://github.com/sevranty/presento/issues/31
- Source merge: `3ce75515783cc6c956d43eaaa6dc0600a434a1e4`.


## Реализованный автономный адаптер

- Код: `skills/3d-visual-pipeline/scripts/presento_adapter.py`.
- Проверки: `skills/3d-visual-pipeline/tests/test_presento_adapter.py` (10 автономных сценариев).
- Поддерживаются `raster-image` и `3d-render` из заранее принятого локального PNG/JPEG.
- `make_executor(...)` возвращает явный Presento callback; `result_from_local_asset(...)` создаёт 13-польный результат v1.
- Входы: exact provider revision, корень локальных файлов, путь уже принятого результата и ожидаемая SHA-256.
- Контроль: строгий request/version/provider/kind, канонический SHA-256 config, выход за корень (включая symlink), байты/checksum, PNG/JPEG и MIME.
- Ошибки возвращаются как `PresentoAdapterError.code`; успешный результат при отказе не выдумывается.
- Вызов не генерирует изображение, не пишет файлы, не обращается в сеть, не использует секреты и не меняет runtime.
- Факт успешной 3DP visual QA доказывает вызывающий код; этот адаптер его не подменяет.

## Оставшиеся условия

Exact-HEAD CI, полный просмотр изменений, ноль нерешённых замечаний, merge PR#45 и readback из `main`. До этих доказательств 3DP#38 остаётся открытой.
