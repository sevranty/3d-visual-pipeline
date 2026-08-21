# DDO#451 TRANSFER adapter — 3DP

Центральный orchestration source: https://github.com/sevranty/design-director-ops/issues/451

Rollout: https://github.com/sevranty/design-director-ops/issues/492

При `DELIVERY_MATRIX = TRANSFER` 3DP получает `MATERIAL_UMBRELLA`, `FDO_SOURCE_ID`, `FDO_SOURCE_URL` и `FDO_SOURCE_FINGERPRINT` только как provenance pointers из material umbrella.

В 3DP переносится только privacy-safe reusable 3D/generative workflow, method или style-pack abstraction. Source-project-specific asset/style/fact не становится 3DP standard автоматически. Один case не доказывает универсальность. Actual write требует separate local child Issue/WRITE_SCOPE и local evidence/evaluation criteria.

Derived 3DP objects обязаны ссылаться на canonical source pointer и DDO material umbrella. Этот generic repository не хранит brand-specific raw/copy и не встраивает brand-specific identifiers в active canonical content.
