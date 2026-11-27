# Лицензии сторонних компонентов ChaMi VPN для Android

Сведения ниже относятся к [Android 1.3.148](https://github.com/chami-vpn/chami-android/releases/tag/v1.3.148). Авторские права на сторонние компоненты сохраняются за их правообладателями. Тексты лицензий находятся в папке [licenses](licenses/).

## Ядро и обвязка Android

- **Xray-core** — Mozilla Public License 2.0 ([текст](licenses/MPL-2.0.txt)). ChaMi VPN включает изменённую версию ядра из публичного форка. [Исходный проект](https://github.com/XTLS/Xray-core) · [Исходный код ядра для 1.3.148, коммит `351d3d6e41e3`](https://github.com/chami-vpn/chami-core/tree/351d3d6e41e3995c92bed212ae0c14b2c992e443).
- **AndroidLibXrayLite** — GNU Lesser General Public License v3.0. Изменённая обвязка на основе AndroidLibXrayLite входит в APK в составе `libgojni.so`. [Исходники обвязки для Android 1.3.148, скрипты сборки и инструкция по перепаковке APK](core/1.3.148/). [Исходный проект](https://github.com/2dust/AndroidLibXrayLite/tree/2ffe5f794a32ba15b122e177b5acffc6f11c4959) · [LGPL‑3.0](licenses/LGPL-3.0.txt) · [GPL‑3.0](licenses/GPL-3.0.txt).
- **Go**, © The Go Authors — стандартная библиотека и среда выполнения Go 1.27.4. [Лицензионное уведомление Go](licenses/Go-BSD-3-Clause.txt). [Тексты лицензий и уведомлений зависимостей Go](licenses/Go-dependency-notices.txt).

## Данные маршрутизации

**Loyalsoldier/v2ray-rules-dat** — проект распространяется по [GPL‑3.0](licenses/GPL-3.0.txt). Файлы `geoip.dat` и `geosite.dat` взяты из выпуска [`202611222203`](https://github.com/Loyalsoldier/v2ray-rules-dat/releases/tag/202611222203). Скрипты сборки и сведения об источниках данных доступны в [дереве соответствующего коммита](https://github.com/Loyalsoldier/v2ray-rules-dat/tree/9a1fbf47e0a1f673eac87ebe90178db5ecd7d21c). GeoIP включает данные GeoLite2, созданные [MaxMind](https://www.maxmind.com/). Сведения о генерации GeoIP доступны в [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip).

## Библиотеки Android и изображения

- Библиотеки AndroidX, Jetpack Compose, CameraX и другие зависимости перечислены в [списке артефактов релизной сборки](licenses/Android-runtime-dependencies.md). Сопроводительные файлы собраны в [Android-dependency-notices.txt](licenses/Android-dependency-notices.txt). [Текст Apache License 2.0](licenses/Apache-2.0.txt).
- Изображения флагов предоставлены [Flagpedia.net](https://flagpedia.net/download) через [FlagCDN](https://flagcdn.com/).
