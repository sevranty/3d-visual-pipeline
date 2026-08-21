# DDO#451 TRANSFER adapter — 3DP

Центральный канон: https://github.com/sevranty/design-director-ops/blob/main/06_governance/finuslugi_material_intake_fanout_contract.md

Rollout: https://github.com/sevranty/design-director-ops/issues/492

При `DELIVERY_MATRIX = TRANSFER` 3DP получает `MATERIAL_UMBRELLA`, `FDO_SOURCE_ID`, `FDO_SOURCE_URL` и `FDO_SOURCE_FINGERPRINT` только как provenance.

В 3DP переносится только privacy-safe reusable 3D/generative workflow, method или style-pack abstraction. Finuslugi-specific asset/style/fact не становится 3DP standard автоматически. Один case не доказывает универсальность. Actual write требует separate local child Issue/WRITE_SCOPE и local evidence/evaluation criteria.

Derived 3DP objects обязаны ссылаться на FDO source и DDO material umbrella.
