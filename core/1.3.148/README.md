# Go-обвязка ядра ChaMi VPN для Android 1.3.148

Эта папка содержит исходники Go-обвязки, из которой собрана `libgojni.so` для Android **1.3.148**, и скрипты для сборки библиотеки и повторной упаковки APK.

Обвязка основана на [AndroidLibXrayLite, коммит `2ffe5f794a32b`](https://github.com/2dust/AndroidLibXrayLite/tree/2ffe5f794a32ba15b122e177b5acffc6f11c4959). ChaMi VPN изменил набор доступных Android-методов, запуск и остановку ядра и обработку файлов геоданных. Эта версия обвязки вошла в выпуск от 27 ноября 2026 года. [LGPL‑3.0](android/native/LICENSE) · [GPL‑3.0](../../licenses/GPL-3.0.txt) · [Уведомления о сторонних компонентах](../../THIRD_PARTY_NOTICES.md)

Версии Xray, Go и инструментов привязки зафиксированы в [go.mod](android/native/go.mod) и [go.sum](android/native/go.sum). Исходники ядра доступны в форке ChaMi на коммите [`351d3d6e41e3`](https://github.com/chami-vpn/chami-core/tree/351d3d6e41e3995c92bed212ae0c14b2c992e443).

## Соберите библиотеку

Нужны Python 3.9 или новее, JDK с `java` и `keytool`, Go с поддержкой выбора инструментальной цепочки, Android SDK, NDK **30.0.16248370**, SDK Build Tools **36.0.0** и Platform Tools. Команды ниже предназначены для оболочки Bash или Zsh. Установите компоненты SDK через SDK Manager и задайте `ANDROID_HOME` и `JAVA_HOME`. Укажите в `PATH` каталоги с `go` и командами JDK.

Клонируйте репозиторий и перейдите в эту папку.

```sh
git clone https://github.com/chami-vpn/chami-android.git
cd chami-android/core/1.3.148
```

Внесите нужные изменения в `android/native/`. Сохраните сигнатуры экспортируемых вызовов Go, чтобы новая библиотека подошла к существующему коду в APK. Затем запустите скрипт.

```sh
python3 tools/build-android-core.py build
```

Он собирает `build/libv2ray.aar` с `libgojni.so` для ARMv7, ARM64, x86 и x86‑64. При первой сборке скрипт загружает зависимости и проверяет их контрольные суммы. Скрипт также получает геоданные той же версии, которые включаются в AAR.

## Перепакуйте APK и подпишите своим ключом

Скачайте [исходный APK Android 1.3.148](https://github.com/chami-vpn/chami-android/releases/download/v1.3.148/ChaMi-Android.apk) и поместите его в текущую папку. Его SHA‑256 указан ниже.

```text
ed3d0d17cc1b75dfd92521b70e6c1fe8d9616c3db770a439968c9aa9581b374c
```

Скрипт создаёт отдельный APK, заменяет в нём `libgojni.so` для архитектур исходного APK и удаляет старую подпись. Готовые DEX-файлы, ресурсы и базы маршрутизации берутся из исходного APK.

```sh
python3 tools/repack-apk.py ChaMi-Android.apk build/libv2ray.aar build/unsigned.apk

bt="$ANDROID_HOME/build-tools/36.0.0"
"$bt/zipalign" -P 16 -f 4 build/unsigned.apk build/aligned.apk

keytool -genkeypair -keystore local-test.jks -alias local-test \
  -keyalg RSA -keysize 2048 -validity 3650 -dname "CN=Local ChaMi Test"
"$bt/apksigner" sign --ks local-test.jks --ks-key-alias local-test \
  --out build/ChaMi-Android-local.apk build/aligned.apk
"$bt/apksigner" verify --verbose build/ChaMi-Android-local.apk
```

Ключ нужен один раз. При последующих сборках можно подписывать тем же `local-test.jks`. Используйте тестовый эмулятор или устройство без официального ChaMi VPN. Android требует совпадения подписей для обновления установленного приложения с тем же именем пакета. Для установки тестовой сборки выполните команду ниже.

```sh
"$ANDROID_HOME/platform-tools/adb" install build/ChaMi-Android-local.apk
```
