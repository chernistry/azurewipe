# Project Description

AzureWipe — автоматизированный инструмент для очистки Azure ресурсов. Удаляет orphaned ресурсы во всех регионах и подписках, помогает поддерживать гигиену Azure аккаунта и избегать лишних расходов. Аналог awswipe для Azure.

## Core
- Primary goal: Безопасное и полное удаление неиспользуемых Azure ресурсов
- Users/personas: DevOps инженеры, разработчики с Azure подписками, команды с dev/test окружениями
- Key constraints: Безопасность (не удалять production ресурсы), идемпотентность, поддержка всех регионов и подписок

## Definition of Done
- [ ] Удаляет все основные типы ресурсов (VMs, Storage Accounts, Databases, Functions, VNets, AKS и т.д.)
- [ ] Работает во всех Azure регионах и подписках
- [ ] Имеет dry-run режим для предварительного просмотра
- [ ] Генерирует детальный отчёт об удалённых/failed ресурсах
- [ ] Обрабатывает зависимости между ресурсами (порядок удаления)
- [ ] Retry механизм для throttling и временных ошибок
- [ ] Логирование всех операций (structured JSON)
- [ ] Поддержка фильтрации по тегам/регионам/resource groups
- [ ] Interactive TUI меню (как в awswipe)
- [ ] YAML конфигурация

## Non-functional Requirements
- Performance: Параллельное удаление где возможно
- Reliability: Graceful handling rate limits и API errors
- Security: Использует стандартные Azure credentials (az login, service principal), не хранит секреты
- Observability: Structured logging, итоговый отчёт
